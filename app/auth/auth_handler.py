import time
from typing import Dict

import jwt
from decouple import config

# JWT_SECRET = config("JWT_SECRET")
# JWT_ALGORITHM = config("JWT_ALGORITHM")


def token_response(token: str):
    return {
        "access_token": token
    }


def sign_jwt(user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 600,
    }
    token = jwt.encode(payload, "secret", algorithm="HS256")

    return token_response(token)

def decode_jwt(token: str) -> dict:
    try:
        decode_token = jwt.decode(token, "secret", algorithms=["HS256"])
        return decode_token if decode_token["expires"] >= time.time() else None
    except:
        raise jwt.exceptions.DecodeError("Problem decoding the token")