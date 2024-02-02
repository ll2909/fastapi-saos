from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Request
from fastapi.security import HTTPBearer
from models.usermodel import User, LoginRequest, RegisterRequest, verify_password
from db.mongodb import get_user_collection, invalid_token
from easyjwt.jwthandler import generate_token, get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address

import os
import vtapi

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/login", tags=["user"])
@limiter.limit("3/minute")
async def login(request: Request, lr_req: LoginRequest = Depends(), current_user: str = Depends(get_current_user), token: str = Depends(HTTPBearer(auto_error=False))):

    assert not (lr_req.username_or_email and current_user)

    user_query = lr_req.username_or_email or current_user

    if user_query == "":
        raise HTTPException(status_code=401, detail="Missing or expired authentication token")

    user_collection = get_user_collection()
    user = user_collection.find_one({"$or": [{"username": user_query}, {"email": user_query}]})
    if user and current_user:
        invalid_token(current_user, token)
        access_token = generate_token(user['username'])
        return {"access_token": access_token, "token_type": "Bearer"}
    elif user and verify_password(lr_req.password, user['password']):
        access_token = generate_token(user['username'])
        return {"access_token": access_token, "token_type": "Bearer"}
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")


@router.post("/refresh", tags=["utils"])
async def refresh(current_user = Depends(get_current_user), token: str = Depends(HTTPBearer(auto_error=False))):
    
    if current_user == "":
        raise HTTPException(status_code=401, detail="Missing or expired authentication token")

    invalid_token(current_user, token)
    access_token = generate_token(current_user)
    return {"access_token": access_token, "token_type": "Bearer", "msg" : "Refreshed"}


@router.post("/register", tags=["user"])
@limiter.limit("1/minute")
async def register(request: Request, reg_req: RegisterRequest = Depends()):
    user = User(username = reg_req.username, email = reg_req.email, password = reg_req.password)
    user_collection = get_user_collection()
    user_collection.insert_one(dict(user))
    return {"msg" : "User registration completed, now you can log in"}


@router.post("/logout", tags = ['user'])
async def logout(current_user = Depends(get_current_user), token: str = Depends(HTTPBearer(auto_error=False))):
    if not current_user:
        raise HTTPException(status_code=401, detail="Missing or expired authentication token")
    
    invalid_token(current_user, token)
    return {"msg": "Logged out."}


@router.post("/uploadfile", tags = ['files'])
async def upload_file(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Missing or expired authentication token")

    path = os.path.join("./uploads", current_user)
    if not os.path.exists(path):
        os.makedirs(path)

    try:
        contents = file.file.read()
        path = os.path.join(path, file.filename)
        with open(path, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"msg" : "Error in file upload."}
    finally:
        file.file.close()

    return {"filename" : file.filename}


@router.post("/vtapi/{filename}/", tags = ['files'])
async def scan_vt(filename: str, current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Missing or expired authentication token")

    path = os.path.join("./uploads", current_user)
    try:
        print("Calling VT API for analysis.")
        path = os.path.join(path, filename)
        print(path)
        stats, id = await vtapi.analyze_file_vt(path)
    except:
        raise HTTPException(status_code=404, detail="File not found")

    return {"filename" : filename, "stats" : stats, "id" : id}
