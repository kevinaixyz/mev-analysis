from typing import Optional

from pydantic import BaseModel, field_validator


class MinerPayment(BaseModel):
    block_number: int
    transaction_hash: str
    transaction_index: int
    miner_address: str
    coinbase_transfer: int
    base_fee_per_gas: int
    gas_price: int
    gas_price_with_coinbase_transfer: int
    gas_used: int
    transaction_to_address: Optional[str] = None
    transaction_from_address: Optional[str] = None

    @field_validator("miner_address", "transaction_to_address", "transaction_from_address", mode="before")
    @classmethod
    def lowercase_address(cls, v: str) -> str:
        return v.lower() if v is not None else v

    @field_validator("gas_price_with_coinbase_transfer", mode="before")
    @classmethod
    def to_int(cls, v: float) -> str:
        return int(v) if isinstance(v, float) else v