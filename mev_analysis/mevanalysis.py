import asyncio
import logging
import traceback
from asyncio import CancelledError
from typing import Optional

from sqlalchemy import orm
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth

from mev_analysis.utils.block import create_from_block_number
from classifiers.trace import TraceClassifier
from inspectors.blockinspector import inspect_block, inspect_many_blocks
from methods import get_block_receipts, trace_block

logger = logging.getLogger(__name__)

AsyncEth.trace_block = trace_block
AsyncEth.get_block_receipts = get_block_receipts


def get_base_provider(rpc: str, request_timeout: int = 500) -> Web3.AsyncHTTPProvider:
    base_provider = AsyncHTTPProvider(rpc, request_kwargs={"timeout": request_timeout})
    return base_provider


class MEVAnalysis:
    def __init__(self, rpc: str, request_timeout: int = 300):
        base_provider = get_base_provider(rpc, request_timeout)
        self.w3 = Web3(base_provider, modules={"eth": (AsyncEth,)}, middlewares=[])

        self.trace_classifier = TraceClassifier()

    async def create_from_block(
            self,
            trace_db_session: Optional[orm.Session],
            block_number: int,
    ):
        return await create_from_block_number(
            w3=self.w3,
            block_number=block_number,
            trace_db_session=trace_db_session,
        )

    async def inspect_single_block(
            self,
            inspect_db_session: orm.Session,
            block: int,
            trace_db_session: Optional[orm.Session],
    ):
        return await inspect_block(
            inspect_db_session,
            self.w3,
            self.trace_classifier,
            block,
            trace_db_session=trace_db_session,
        )

    async def inspect_many_blocks(
            self,
            inspect_db_session: orm.Session,
            trace_db_session: Optional[orm.Session],
            after_block: int,
            before_block: int,
            block_batch_size: int = 10,
    ):
        tasks = []
        for block_number in range(after_block, before_block, block_batch_size):
            batch_after_block = block_number
            batch_before_block = min(block_number + block_batch_size, before_block)

            tasks.append(
                asyncio.ensure_future(
                    self.safe_inspect_many_blocks(
                        inspect_db_session,
                        trace_db_session,
                        after_block_number=batch_after_block,
                        before_block_number=batch_before_block,
                    )
                )
            )
        logger.info(f"Gathered {before_block - after_block} blocks to inspect")
        try:
            await asyncio.gather(*tasks)
        except CancelledError:
            logger.info("Requested to exit, cleaning up...")
        except Exception as e:
            logger.error(f"Exited due to {type(e)}")
            traceback.print_exc()
            raise

    async def safe_inspect_many_blocks(
            self,
            inspect_db_session: orm.Session,
            trace_db_session: Optional[orm.Session],
            after_block_number: int,
            before_block_number: int,
    ):
        async with self.max_concurrency:
            return await inspect_many_blocks(
                inspect_db_session,
                self.w3,
                self.trace_classifier,
                after_block_number,
                before_block_number,
                trace_db_session=trace_db_session,
            )
