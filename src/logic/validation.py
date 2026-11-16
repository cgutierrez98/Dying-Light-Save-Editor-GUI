"""Validacion basica del JSON del save antes de cifrarlo."""
import math

INT32_MAX = 2**31 - 1


class SaveValidationError(ValueError):
    pass


def _walk(node, path="$"):
    if isinstance(node, dict):
        for k, v in node.items():
            _walk(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _walk(v, f"{path}[{i}]")
    elif isinstance(node, float):
        if math.isnan(node) or math.isinf(node):
            raise SaveValidationError(f"Valor no valido (NaN/Inf) en {path}")
    elif isinstance(node, int) and not isinstance(node, bool):
        if abs(node) > 2**63 - 1:
            raise SaveValidationError(f"Entero fuera de rango en {path}")


def validate_save_data(data):
    if not isinstance(data, (dict, list)) or not data:
        raise SaveValidationError("Los datos del save estan vacios o tienen un formato inesperado.")
    _walk(data)
    return True
