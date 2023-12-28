from typing import List

from pydantic import BaseModel, field_validator

from .swaps import Swap


class Sandwich(BaseModel):
    block_number: int
    sandwicher_address: str
    frontrun_swap: Swap
    backrun_swap: Swap
    sandwiched_swaps: List[Swap]
    profit_token_address: str
    profit_amount: int

    @field_validator("sandwicher_address", "profit_token_address", mode="before")
    @classmethod
    def lowercase_address(cls, v: str) -> str:
        return v.lower()
