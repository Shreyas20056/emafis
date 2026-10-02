import os
import sys
import hmac
import hashlib
import base64
import json
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, EmailStr, Field

from database import users_collection

router = APIRouter(prefix="/api/auth", tags=["Auth"])

SECRET_KEY = os.getenv("JWT_SECRET", "emafis_super_secret_jwt_key_2026")


def hash_password(password: str, salt: bytes = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return hashed.hex(), salt.hex()


def verify_password(password: str, stored_hash: str, salt_hex: str) -> bool:
    salt = bytes.fromhex(salt_hex)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return hmac.compare_digest(hashed.hex(), stored_hash)


def create_jwt_token(payload: dict, expires_minutes: int = 60 * 24 * 7) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    exp = datetime.utcnow() + timedelta(minutes=expires_minutes)
    token_payload = {**payload, "exp": int(exp.timestamp())}
    
    b64_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    b64_payload = base64.urlsafe_b64encode(json.dumps(token_payload).encode()).decode().rstrip("=")
    
    signature_input = f"{b64_header}.{b64_payload}".encode()
    signature = hmac.new(SECRET_KEY.encode(), signature_input, hashlib.sha256).digest()
    b64_sig = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{b64_header}.{b64_payload}.{b64_sig}"


def decode_jwt_token(token: str) -> Optional[dict]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        b64_header, b64_payload, b64_sig = parts
        
        signature_input = f"{b64_header}.{b64_payload}".encode()
        expected_sig = hmac.new(SECRET_KEY.encode(), signature_input, hashlib.sha256).digest()
        b64_expected_sig = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")
        
        if not hmac.compare_digest(b64_sig, b64_expected_sig):
            return None
            
        rem = len(b64_payload) % 4
        padded_payload = b64_payload + ("=" * (4 - rem) if rem else "")
        payload = json.loads(base64.urlsafe_b64decode(padded_payload).decode())
        
        if payload.get("exp", 0) < int(datetime.utcnow().timestamp()):
            return None
            
        return payload
    except Exception:
        return None


class SignupRequest(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/signup")
def signup(req: SignupRequest):
    email_lower = req.email.lower().strip()
    if users_collection.find_one({"email": email_lower}):
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    pwd_hash, salt_hex = hash_password(req.password)
    user_doc = {
        "name": req.name.strip(),
        "email": email_lower,
        "password_hash": pwd_hash,
        "salt": salt_hex,
        "created_at": datetime.utcnow()
    }
    result = users_collection.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    token = create_jwt_token({"user_id": user_id, "email": email_lower, "name": req.name.strip()})
    return {
        "token": token,
        "user": {
            "id": user_id,
            "name": req.name.strip(),
            "email": email_lower
        }
    }


@router.post("/login")
def login(req: LoginRequest):
    email_lower = req.email.lower().strip()
    user = users_collection.find_one({"email": email_lower})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(req.password, user["password_hash"], user["salt"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user_id = str(user["_id"])
    token = create_jwt_token({"user_id": user_id, "email": email_lower, "name": user["name"]})
    return {
        "token": token,
        "user": {
            "id": user_id,
            "name": user["name"],
            "email": email_lower
        }
    }


@router.get("/me")
def get_me(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ")[1]
    payload = decode_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = users_collection.find_one({"email": payload["email"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    created_at = user.get("created_at")
    created_str = created_at.isoformat() if isinstance(created_at, datetime) else str(created_at or "")

    return {
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "created_at": created_str
        }
    }
