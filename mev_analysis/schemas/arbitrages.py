from typing import List, Optional

from pydantic import BaseModel, field_validator

from .swaps import Swap


class Arbitrage(BaseModel):
    swaps: List[Swap]
    block_number: int
    transaction_hash: str
    account_address: str
    profit_token_address: str
    start_amount: int
    end_amount: int
    profit_amount: int
    error: Optional[str] = None

    @field_validator("account_address", "profit_token_address", mode="before")
    @classmethod
    def lowercase_address(cls, v: str) -> str:
        return v.lower()