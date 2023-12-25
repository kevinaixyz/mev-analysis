import json
from typing import Dict, Any

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
    if isinstance(v, HexBytes) or isinstance(v, bytes):
        return v.hex()
    elif isinstance(v, dict):
        return hexbytes_to_str_in_dict(v)
    elif isinstance(v, list) or isinstance(v, tuple):
        return hexbytes_to_str_in_iter(v)
    else:
        return v


def hexbytes_to_str_in_dict(v: Dict[str, Any]) -> None:
    for key, value in v.items():
        if isinstance(value, HexBytes):
            v[key] = value.hex()
        if isinstance(value, dict):
            hexbytes_to_str_in_dict(value)


def hexbytes_to_str_in_iter(v: list | tuple) -> list | tuple:
    if isinstance(v, list):
        for i, value in enumerate(v):
            v[i] = hexbytes_to_str(value)
        return v
    if isinstance(v, tuple):
        new_list = []
        for value in v:
            new_list.append(hexbytes_to_str(value))
        return tuple(new_list)


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
