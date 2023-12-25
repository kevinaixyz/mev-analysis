import asyncio

from config import get_key
from mev_analysis.db import get_inspect_session, get_trace_session
from mev_analysis.mevanalysis import MEVAnalysis
from mev_analysis.utils.prices import fetch_prices, fetch_prices_range
from mev_analysis.crud.prices import write_prices

from mev_analysis.tracedata.etl import load_flashbot_blocks

import logging
import sys


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_block_command(block_number: int, rpc: str):
    trace_db_session = get_trace_session()

    inspector = MEVAnalysis(rpc)
    block = await inspector.create_from_block(
        block_number=block_number,
        trace_db_session=trace_db_session,
    )
    print(block.json())


async def inspect_block_command(block_number: int, rpc: str):
    inspect_db_session = get_inspect_session()
    trace_db_session = get_trace_session()

    inspector = MEVAnalysis(rpc)

    await inspector.inspect_single_block(
        inspect_db_session=inspect_db_session,
        trace_db_session=trace_db_session,
        block=block_number,
    )


async def inspect_many_blocks_command(
        after_block: int,
        before_block: int,
        rpc: str,
        max_concurrency: int,
        request_timeout: int,
):
    inspect_db_session = get_inspect_session()
    trace_db_session = get_trace_session()

    inspector = MEVAnalysis(
        rpc,
        max_concurrency=max_concurrency,
        request_timeout=request_timeout,
    )
    await inspector.inspect_many_blocks(
        inspect_db_session=inspect_db_session,
        trace_db_session=trace_db_session,
        after_block=after_block,
        before_block=before_block,
    )


def fetch_all_prices():
    inspect_db_session = get_inspect_session()

    logger.info("Fetching prices")
    prices = fetch_prices()

    logger.info("Writing prices")
    write_prices(inspect_db_session, prices)


def init():
    fetch_all_prices()


if __name__ == '__main__':
    rpc = get_key('Node', 'RPC_URL')
    block_numbers = load_flashbot_blocks()
    for block_number in block_numbers[: 10]:
        task = asyncio.run(inspect_block_command(block_number, rpc))
