import asyncio

from config import config, get_key
from mev_analysis.db import get_inspect_session, get_trace_session
from mev_analysis.mevanalysis import MEVAnalysis


async def fetch_block_command(block_number: int, rpc: str):
    trace_db_session = get_trace_session()

    inspector = MEVAnalysis(rpc)
    block = await inspector.create_from_block(
        block_number=block_number,
        trace_db_session=trace_db_session,
    )
    print(block.json())

async def inspect_block_command(block_number:int, rpc:str):
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

if __name__ == '__main__':
    rpc = get_key('Node', 'RPC_URL')
    task = asyncio.run(inspect_block_command(18541697, rpc))
