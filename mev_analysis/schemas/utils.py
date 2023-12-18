import json

from hexbytes import HexBytes
from pydantic import ConfigDict, BaseModel
from web3.datastructures import AttributeDict


def to_camel(string: str) -> str:
    return "".join(
        word.capitalize() if i > 0 else word for i, word in enumerate(string.split("_"))
    )


def to_original_json_dict(model: BaseModel) -> dict:
    return json.loads(model.json(by_alias=True, exclude_unset=True))


def hexbytes_to_str(v: HexBytes) -> str:
        return v.hex() if isinstance(v, HexBytes) else v

class Web3Model(BaseModel):
    """BaseModel that handles web3's unserializable objects"""
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(json_encoders={
        AttributeDict: dict,
        HexBytes: lambda h: h.hex(),
    })


class CamelModel(BaseModel):
    """BaseModel that translates from snake_case to camelCase"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
