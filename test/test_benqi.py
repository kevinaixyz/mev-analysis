import asyncio
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
import pytest



from mev_analysis.utils.block import _fetch_block_traces

RPC_URL = ""


@pytest.fixture(name="w3")
def init_w3() -> Web3:
    base_provider = AsyncHTTPProvider(RPC_URL, request_kwargs={"timeout": 500})
    w3 = Web3(base_provider, modules={"eth": (AsyncEth,)}, middlewares=[])
    return w3


@pytest.mark.asyncio
async def test_fetch_block_traces(w3):
    block_number = 18541697
    traces = await _fetch_block_traces(w3, block_number, './blocks')
    assert len(traces) > 0


if __name__ == '__main__':
    w3 = init_w3(RPC_URL)
    task = asyncio.run(test_fetch_block_traces())
