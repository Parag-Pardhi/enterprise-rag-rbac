import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Demo-only identities. Replace with a database/IdP in production.
USERS = {
    "admin": {"password": pwd_context.hash("admin123"), "role": "admin"},
    "analyst": {"password": pwd_context.hash("analyst123"), "role": "analyst"},
    "viewer": {"password": pwd_context.hash("viewer123"), "role": "viewer"},
}


def authenticate(username: str, password: str):
    user = USERS.get(username)
    if not user or not pwd_context.verify(password, user["password"]):
        return None
    return {"username": username, "role": user["role"]}


def create_access_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def current_user(token: str = Depends(oauth2_scheme)):
    credentials_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username, role = payload.get("sub"), payload.get("role")
        if not username or not role:
            raise credentials_error
        return {"username": username, "role": role}
    except JWTError as exc:
        raise credentials_error from exc


def require_roles(*roles):
    def checker(user=Depends(current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return checker
