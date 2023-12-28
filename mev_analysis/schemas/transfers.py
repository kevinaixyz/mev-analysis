from typing import List

from pydantic import BaseModel, field_validator


class Transfer(BaseModel):
    block_number: int
    transaction_hash: str
    trace_address: List[int]
    from_address: str
    to_address: str
    amount: int
    token_address: str

    @field_validator("to_address", "from_address", "token_address", mode="before")
    @classmethod
    def lowercase_address(cls, v: str) -> str:
        return v.lower()