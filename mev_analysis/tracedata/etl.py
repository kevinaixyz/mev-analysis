import asyncio

import pandas as pd
from typing import List, Type, Optional, Dict, Any
import json

from sqlalchemy import orm, text
from web3 import Web3

from mev_analysis.config import get_key
from mev_analysis.mevanalysis import MEVAnalysis
from mev_analysis.schemas.traces import Trace
from mev_analysis.tracedata.base_fee import BaseFeeModel
from mev_analysis.tracedata.block_timestamp import BlockTimestampModel
from mev_analysis.tracedata.receipt import ReceiptModel
from mev_analysis.tracedata.trace import BlockTraceModel
from mev_analysis.utils.block import _fetch_block_timestamp, fetch_base_fee_per_gas

from mev_analysis.db import get_trace_session
from mev_analysis.models.base import Base
from hexbytes import HexBytes

import logging
from pathlib import Path

PARSED_BLOCKS_PATH = Path(__file__).parent / 'blocks.csv'
logger = logging.getLogger(__file__)


def init_w3() -> Web3:
    rpc = get_key('Node', 'RPC_URL')
    inspector = MEVAnalysis(rpc)
    return inspector.w3


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
    result = find_by_block(trace_db_session, block_number, BlockTraceModel)
    if not result:
        traces_json = await w3.eth.trace_block(block_number)
        new_traces_json = []
        if traces_json:
            for trace_json in traces_json:
                hex_to_str_in_dict(trace_json)
                new_traces_json.append(trace_json)

        new_traces_json = json.dumps(new_traces_json)

        write_block_traces(trace_db_session, block_number, new_traces_json)


def hex_to_str_in_dict(v: Dict[str, Any]) -> None:
    for key, value in v.items():
        if isinstance(value, HexBytes):
            v[key] = value.hex()
        if isinstance(value, dict):
            hex_to_str_in_dict(value)


async def fetch_block_receipts(
        w3: Web3,
        trace_db_session: orm.Session,
        block_number: int) -> None:
    result = find_by_block(trace_db_session, block_number, ReceiptModel)
    if not result:
        receipts_json = await w3.eth.get_block_receipts(block_number)
        receipts_json = json.dumps(receipts_json)
        write_block_receipts(trace_db_session, block_number, receipts_json)


async def fetch_base_fee(
        w3: Web3,
        trace_db_session: orm.Session,
        block_number: int) -> None:
    result = find_by_block(trace_db_session, block_number, BaseFeeModel)
    if not result:
        base_fee = await fetch_base_fee_per_gas(w3, block_number)
        write_base_fee(trace_db_session, block_number, base_fee)


def load_flashbot_blocks() -> List[int]:
    blocks_df = pd.read_csv(PARSED_BLOCKS_PATH)
    blocks_df = blocks_df.sort_values('block_number')
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
    trace_db_session.commit()


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

    trace_db_session.execute(stmt, params={"block_number": block_number, "raw_receipts": block_receipts_json})
    trace_db_session.commit()


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
    trace_db_session.commit()


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
    trace_db_session.execute(stmt, params={"block_number": block_number, "base_fee": base_fee})
    trace_db_session.commit()


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
    for i, block_number in enumerate(block_numbers):
        timestamp_task = asyncio.run(fetch_block_timestamp(w3, trace_db_session, block_number))
        receipt_task = asyncio.run(fetch_block_receipts(w3, trace_db_session, block_number))
        trace_task = asyncio.run(fetch_block_traces(w3, trace_db_session, block_number))
        base_fee_task = asyncio.run(fetch_base_fee(w3, trace_db_session, block_number))
        print(f'Finished for block {block_number} (index: {i})')
