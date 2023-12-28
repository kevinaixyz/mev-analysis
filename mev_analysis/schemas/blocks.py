from typing import List
from hexbytes import HexBytes
from pydantic import field_validator, Field

from mev_analysis.utils.utils import hex_to_int

from .receipts import Receipt
from .traces import Trace
from .utils import CamelModel, Web3Model, hexbytes_to_str


class CallResult(CamelModel):
    gas_used: int

    @field_validator("gas_used", mode="before")
    @classmethod
    def maybe_hex_to_int(cls, v):
        if isinstance(v, str):
            return hex_to_int(v)
        return v


class CallAction(Web3Model):
    to: str
    from_: str = Field(validation_alias='from')
    input: str
    value: int
    gas: int

    @field_validator("value", "gas", mode="before")
    @classmethod
    def maybe_hex_to_int(cls, v):
        if isinstance(v, str):
            return hex_to_int(v)
        return v

    @field_validator("input", mode="before")
    @classmethod
    def hex_to_str(cls, v: HexBytes) -> str:
        return hexbytes_to_str(v)

    @field_validator("from_", "to", mode="before")
    @classmethod
    def lowercase_address(cls, v: str) -> str:
        return v.lower()


class Block(Web3Model):
    block_number: int
    block_timestamp: int
    miner: str
    base_fee_per_gas: int
    traces: List[Trace]
    receipts: List[Receipt]

    def get_filtered_traces(self, hash: str) -> List[Trace]:
        return [trace for trace in self.traces if trace.transaction_hash.lower() == hash.lower()]
