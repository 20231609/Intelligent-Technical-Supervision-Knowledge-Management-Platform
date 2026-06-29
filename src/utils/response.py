from typing import Any


def buildSuccessResponse(data: Any = None, message: str = "success") -> dict:
    return {"code": 200, "data": data, "message": message}


def buildErrorResponse(code: int, message: str) -> dict:
    return {"code": code, "data": None, "message": message}
