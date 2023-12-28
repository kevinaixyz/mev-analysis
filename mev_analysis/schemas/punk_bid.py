from typing import List

from pydantic import BaseModel, field_validator


class PunkBid(BaseModel):
    block_number: int
    transaction_hash: str
    trace_address: List[int]
    from_address: str
    punk_index: int
    price: int

    @field_validator("from_address", mode="before")
    @classmethod
    def lowercase_address(cls, v: str) -> str:
        return v.lower()