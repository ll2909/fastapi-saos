import jwt
import datetime
import rsa

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError
from jwt.exceptions import ExpiredSignatureError
from db.mongodb import get_user_collection

with open('./easyjwt/public.pem', mode='rb') as key_file:
    key_data = key_file.read()
    rsa_key = str(rsa.PublicKey.load_pkcs1_openssl_pem(key_data).n)

with open("./easyjwt/jwt_encoding_config",  "r") as file:
    enc_alg = file.read()
    

def generate_token(username: str):
    payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
        "iat": datetime.datetime.utcnow(),
        "sub": username
    }

    return jwt.encode(payload, key = rsa_key, algorithm=enc_alg)


def decode_token(token):
    try:
        return jwt.decode(token, key = rsa_key, algorithms=enc_alg)
    except ExpiredSignatureError:
        return None

def get_username_from_token(token):
    payload = jwt.decode(token, key = rsa_key, algorithms=enc_alg)
    return payload["sub"]


def get_current_user(token: str = Depends(HTTPBearer(auto_error=False))):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token.credentials)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    except AttributeError:
        return ""

    user_collection = get_user_collection()
    user = user_collection.find_one({"username": username})
    
    if user and token != user["last_used_token"]:
        return username
    else:
        raise credentials_exception
    