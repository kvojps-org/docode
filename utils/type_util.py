from typing import Any


def cast_to_bool(value: Any) -> bool:
    if value is None:
        return False
    elif type(value) is bool:
        return value
    elif type(value) is str:
        return _cast_str_to_bool(value)
    elif type(value) is int:
        return _cast_int_to_bool(value)
    else:
        raise ValueError(f"Parâmetro boolean possui tipo inválido '{type(value)}'")


def _cast_str_to_bool(value: str) -> bool:
    valid_values = {"true": True, "false": False}
    if value.lower() not in valid_values:
        raise ValueError(f"Parâmetro boolean possui valor inválido '{value}'")

    return valid_values[value.lower()]


def _cast_int_to_bool(value: int) -> bool:
    if value not in [0, 1]:
        raise ValueError(f"Parâmetro boolean possui valor inválido '{value}'")
    return bool(value)
