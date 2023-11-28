import json

def is_json(data):
    try:
        json_object = json.loads(data)
        return True
    except (json.JSONDecodeError, TypeError):
        return False

def is_valid_abi(obj):
    return True if isinstance(obj, list) else False