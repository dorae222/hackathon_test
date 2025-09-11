def json_err(code: str, msg: str):
    return {"error": {"code": code, "message": msg, "details": {}}}
