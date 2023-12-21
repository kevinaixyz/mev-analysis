import json
from hexbytes._utils import hexstr_to_bytes


def hex_to_int(value: str) -> int:
    return int.from_bytes(hexstr_to_bytes(value), byteorder="big")


def equal_within_percent(
    first_value: int, second_value: int, threshold_percent: float
) -> bool:
    difference = abs(
        (first_value - second_value) / (0.5 * (first_value + second_value))
    )
    return difference < threshold_percent


def is_json(data):
    try:
        json_object = json.loads(data)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def is_valid_abi(obj):
    return True if isinstance(obj, list) else False