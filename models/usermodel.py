from pydantic import BaseModel
import datetime
import bcrypt

class User(BaseModel):

    username: str
    email: str
    password: str
    created_at: datetime.datetime
    last_used_token : str

    def __init__(self, username: str, email: str, password: str) -> None: 
        super().__init__(username = username, 
                         email = email, 
                         password = get_password_hash(password), 
                         created_at =datetime.datetime.utcnow(), 
                         last_used_token = "")

class LoginRequest(BaseModel):
    username_or_email: str | None = None
    password: str | None = None

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

def get_password_hash(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())