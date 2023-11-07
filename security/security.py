from datetime import datetime
from datetime import datetime, timedelta
from fastapi import Header, HTTPException
from jose import JWTError, jwt
import bcrypt
from config.config import hashing_algorithm
from config.config import secret_key
import secrets
from config.config import refresh_token_key, refresh_token_time

SECRET_KEY = secret_key
ALGORITHM = hashing_algorithm

# Define a secret key for signing and verifying refresh tokens
REFRESH_TOKEN_SECRET = refresh_token_key

REFRESH_TOKEN_EXPIRE_DAYS = int(refresh_token_time)


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Function to create a refresh token
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expiration = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expiration})
    refresh_token = jwt.encode(to_encode, REFRESH_TOKEN_SECRET, algorithm=ALGORITHM)
    return refresh_token


def verify_token(authorization: str = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Bearer token not found in Authorization header"
        )

    token = authorization.split("Bearer ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


def hash_password(password: str) -> str:
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Verify the plain password against the hashed password
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)


# Generate a unique token for password reset
def generate_reset_token():
    return secrets.token_urlsafe(32)
