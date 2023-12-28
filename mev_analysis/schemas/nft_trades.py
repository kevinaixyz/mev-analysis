from typing import List, Optional

from pydantic import BaseModel, field_validator

from mev_analysis.schemas.traces import Protocol


class NftTrade(BaseModel):
    abi_name: str
    transaction_hash: str
    transaction_position: int
    block_number: int
    trace_address: List[int]
    protocol: Optional[Protocol] = None
    error: Optional[str] = None
    seller_address: str
    buyer_address: str
    payment_token_address: str
    payment_amount: int
    collection_address: str
    token_id: int

    @field_validator("seller_address", "buyer_address", "payment_token_address", "collection_address", mode="before")
    @classmethod
    def lowercase_address(cls, v: str) -> str:
        return v.lower()