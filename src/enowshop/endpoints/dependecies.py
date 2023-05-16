from fastapi.params import Header
from jose.jwt import decode
from jose.exceptions import JWTError
from starlette.exceptions import HTTPException

from config import Config


def format_struct_key(jwt_token: str):
    header = '-----BEGIN PUBLIC KEY-----\n'
    trailer = '\n-----END PUBLIC KEY-----'
    if header not in jwt_token:
        jwt_token = f"{header}{jwt_token}"
    if trailer not in jwt_token:
        jwt_token = f"{jwt_token}{trailer}"

    return jwt_token


async def verify_jwt(authorization: str = Header()):
    jwt_token = authorization.split(" ", 1)[1]
    options = {"verify_signature": True, "verify_aud": False, "exp": True}
    try:
        return decode(jwt_token, format_struct_key(Config.KEYCLOAK_PUBLIC_KEY), algorithms="RS256", options=options)
    except JWTError:
        raise HTTPException(status_code=401, detail="Unauthorized token")
