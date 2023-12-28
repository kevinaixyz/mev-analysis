from enum import Enum
from typing import Any, Dict, List, Optional

from .utils import CamelModel, hexbytes_to_str
from pydantic import ConfigDict, field_validator
from hexbytes import HexBytes


class TraceType(Enum):
    call = "call"
    create = "create"
    delegate_call = "delegateCall"
    reward = "reward"
    suicide = "suicide"


class Trace(CamelModel):
    action: dict
    block_hash: str
    block_number: int
    result: Optional[dict] = None
    subtraces: int
    trace_address: List[int]
    transaction_hash: Optional[str] = None
    transaction_position: Optional[int] = None
    type: TraceType
    error: Optional[str] = None

    @field_validator("block_hash", "transaction_hash", mode="before")
    @classmethod
    def hex_to_str(cls, v: HexBytes) -> str:
        return hexbytes_to_str(v)


class Classification(Enum):
    unknown = "unknown"
    swap = "swap"
    transfer = "transfer"
    liquidate = "liquidate"
    seize = "seize"
    punk_bid = "punk_bid"
    punk_accept_bid = "punk_accept_bid"
    nft_trade = "nft_trade"


class Protocol(Enum):
    uniswap_v2 = "uniswap_v2"
    uniswap_v3 = "uniswap_v3"
    sushiswap = "sushiswap"
    aave = "aave"
    aave_v3 = "aave_v3"
    weth = "weth"
    curve = "curve"
    zero_ex = "0x"
    balancer_v1 = "balancer_v1"
    balancer_v2 = "balancer_v2"
    compound_v2 = "compound_v2"
    cream = "cream"
    cryptopunks = "cryptopunks"
    bancor = "bancor"
    opensea = "opensea"
    traderjoe = "traderjoe"
    benqi = "benqi"
    gmx = 'gmx'
    pangolin = "pangolin"
    compound_v3 = "compound_v3"
    radiant_v2 = "radiant_v2"


class ClassifiedTrace(Trace):
    classification: Classification
    to_address: Optional[str] = None
    from_address: Optional[str] = None
    gas: Optional[int] = None
    value: Optional[int] = None
    gas_used: Optional[int] = None
    transaction_hash: str
    transaction_position: int
    protocol: Optional[Protocol] = None
    function_name: Optional[str] = None
    function_signature: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None
    abi_name: Optional[str] = None

    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    # model_config = ConfigDict(validate_assignment=True, json_encoders={
    #     # a little lazy but fine for now
    #     # this is used for bytes value inputs
    #     bytes: lambda b: b.hex(),
    # })

    @field_validator("inputs", mode="before")
    @classmethod
    def bytes_to_str(cls, v: Dict[str, Any]) -> str:
        for (k, val) in v.items():
            # if k == 'makerSignature' or k=="takerSignature":
            #     v[k] = hexbytes_to_str(val)
            v[k] = hexbytes_to_str(val)
        return v


class CallTrace(ClassifiedTrace):
    to_address: str
    from_address: str

    @field_validator("to_address","from_address", mode="before")
    @classmethod
    def lowercase_address(cls, v: str) -> str:
        return v.lower()


class DecodedCallTrace(CallTrace):
    inputs: Dict[str, Any]
    abi_name: str
    protocol: Optional[Protocol]
    gas: Optional[int]
    gas_used: Optional[int]
    function_name: str
    function_signature: str
