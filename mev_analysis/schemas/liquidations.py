from typing import List, Optional

from pydantic import BaseModel, field_validator

from mev_analysis.schemas.traces import Protocol


class Liquidation(BaseModel):
    liquidated_user: str
    liquidator_user: str
    debt_token_address: str
    debt_purchase_amount: int
    received_amount: int
    received_token_address: Optional[str] = None
    protocol: Protocol
    transaction_hash: str
    trace_address: List[int]
    block_number: int
    error: Optional[str] = None

    @field_validator("liquidated_user", "liquidator_user", "debt_token_address", "received_token_address" ,mode="before")
    @classmethod
    def lowercase_address(cls, v: str) -> str:
        return v.lower()