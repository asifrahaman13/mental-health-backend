from fastapi import APIRouter
from connection.connection import collection
from fastapi import HTTPException
from models.models import UserEmail
from fastapi.security import OAuth2PasswordBearer
from security.security import create_access_token, create_refresh_token
from jose import jwt
from datetime import timedelta
from fastapi import Depends, HTTPException
from config.config import (
    secret_key,
    hashing_algorithm,
    refresh_token_key,
    access_token_time,
    refresh_token_time
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = secret_key
ALGORITHM = hashing_algorithm
REFRESH_TOKEN_SECRET = refresh_token_key
ACCESS_TOKEN_EXPIRE_MINUTES = int(access_token_time)
REFRESH_TOKEN_TIME= int(refresh_token_time)


token_router = APIRouter(
    prefix="/token",
)


# Create an endpoint to generate and return an initial refresh token upon login or signup
@token_router.post("/generate-refresh-token")
async def generate_refresh_token(email_address: UserEmail):
    # Check if the email_address exists in the database

    email_address = email_address.model_dump()

    user_data = collection.find_one({"email_address": email_address["email_address"]})

    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Create an initial refresh token for the user
    refresh_token = create_refresh_token({"email_address": email_address})

    return {"refresh_token": refresh_token}


# Create an endpoint to refresh the access token using a refresh token from the Bearer token in the header
@token_router.post("/refresh-access-token")
async def refresh_access_token(refresh_token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            refresh_token, REFRESH_TOKEN_SECRET, algorithms=[ALGORITHM]
        )
        email_address = payload.get("email_address")
        # Check if the email_address exists in the database and perform any additional checks as needed
        # Here, we assume that the email_address exists in the database
        user_data = collection.find_one(
            {"email_address": email_address["email_address"]}
        )

        if user_data is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Generate a new access token
        access_token = create_access_token(
            {"email_address": email_address},
            timedelta(days=REFRESH_TOKEN_TIME),
        )

        return {"access_token": access_token}
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Invalid refresh token")
