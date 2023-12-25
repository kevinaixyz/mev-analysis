import asyncio

import pandas as pd
from typing import List, Type, Optional
import json

from sqlalchemy import create_engine, orm, text, Engine
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth

from mev_analysis.config import get_key
from mev_analysis.utils.block import _fetch_block_traces, _fetch_block_receipts, _fetch_block_timestamp, \
    fetch_base_fee_per_gas

from mev_analysis.db import get_trace_session
from mev_analysis.models.base import Base
from .trace import TraceModel
from .receipt import ReceiptModel
from .block_timestamp import BlockTimestampModel
from .base_fee import BaseFeeModel

import logging

PARSED_BLOCKS_PATH = './blocks.csv'
logger = logging.getLogger(__file__)


def init_w3() -> Web3:
    rpc_url = get_key('Node', 'RPC_URL')
    base_provider = AsyncHTTPProvider(rpc_url, request_kwargs={"timeout": 500})
    w3 = Web3(base_provider, modules={"eth": (AsyncEth,)}, middlewares=[])
    return w3


async def fetch_block_timestamp(
        w3: Web3,
        trace_db_session: orm.Session,
        block_number: int) -> None:
    result = find_by_block(trace_db_session, block_number, BlockTimestampModel)
    if not result:
        block_timestamp = await _fetch_block_timestamp(w3, block_number)
        write_block_timestamp(trace_db_session, block_number, block_timestamp)


async def fetch_block_traces(
        w3: Web3,
        trace_db_session: orm.Session,
        block_number: int) -> None:

    result = await find_by_block(trace_db_session, block_number, TraceModel)
    if not result:
        traces_json = await _fetch_block_traces(w3, block_number)
        write_block_traces(trace_db_session, block_number, traces_json)

    if not result:
        write_block_traces(trace_db_session, traces_json)


async def fetch_block_receipts(
        w3: Web3,
        trace_db_session: orm.Session,
        block_number: int) -> None:

    result = await find_by_block(trace_db_session, block_number, ReceiptModel)
    if not result:
        receipts_json = await _fetch_block_receipts(w3, block_number)
        write_block_traces(trace_db_session, block_number, receipts_json)

    if not result:
        write_block_receipts(trace_db_session, receipts_json)


async def fetch_base_fee(
        w3: Web3,
        trace_db_session: orm.Session,
        block_number: int) -> None:

    result = await find_by_block(trace_db_session, block_number, BaseFeeModel)
    if not result:
        base_fee = await fetch_base_fee_per_gas(w3, block_number)
        write_base_fee(trace_db_session, block_number, base_fee)


def load_flashbot_blocks() -> List[int]:
    blocks_df = pd.read_csv(PARSED_BLOCKS_PATH)
    return blocks_df['block_number'].tolist()


def write_block_timestamp(
        trace_db_session: orm.Session,
        block_number: int,
        block_timestamp: int) -> None:
    stmt = text(
        """
        INSERT INTO block_timestamps
        (block_number, block_timestamp)
        VALUES
        (:block_number, :block_timestamp)
        """
    )
    trace_db_session.execute(stmt, params={"block_number": block_number, "block_timestamp": block_timestamp})


def write_block_receipts(
        trace_db_session: orm.Session,
        block_number: int,
        block_receipts_json: json) -> None:
    stmt = text(
        """
        INSERT INTO block_receipts
        (block_number, raw_receipts)
        VALUES
        (:block_number, :raw_receipts)
        """
    )

    trace_db_session.execute(stmt, params={"block_number": block_number, "raw_receipt": block_receipts_json})


def write_block_traces(
        trace_db_session: orm.Session,
        block_number: int,
        block_traces_json: json) -> None:
    stmt = text(
        """
        INSERT INTO block_traces
        (block_number, raw_traces)
        VALUES
        (:block_number, :raw_traces)
        """
    )
    trace_db_session.execute(stmt, params={"block_number": block_number, "raw_traces": block_traces_json})


def write_base_fee(
        trace_db_session: orm.Session,
        block_number: int,
        base_fee: int) -> None:
    stmt = text(
        """
        INSERT INTO base_fee
        (block_number, base_fee_in_wei)
        VALUES
        (:block_number, :base_fee)
        """
    )
    trace_db_session.execute(stmt, params={"block_number": block_number, "base_fee_in_wei": base_fee})


def find_by_block(
        trace_db_session: orm.Session,
        block_number: int,
        model_class: Type[Base],
) -> Optional[List[Type[Base]]]:
    return trace_db_session.get(model_class, block_number)


if __name__ == '__main__':
    w3 = init_w3()
    block_numbers = load_flashbot_blocks()
    trace_db_session = get_trace_session()
    test_rec = 10
    for block_number in block_numbers[:test_rec]:
        timestamp_task = asyncio.run(fetch_block_timestamp(w3, trace_db_session, block_number))
        receipt_task = asyncio.run(fetch_block_receipts(w3, trace_db_session, block_number))
        trace_task = asyncio.run(fetch_block_traces(w3, trace_db_session, block_number))
        base_fee_task = asyncio.run(fetch_base_fee(w3, trace_db_session, block_number))
