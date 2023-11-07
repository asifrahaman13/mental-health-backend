from fastapi import APIRouter
from connection.connection import collection
from fastapi import HTTPException
from models.models import UserInfo,VerifyPasswordData
from security.security import (
    create_access_token,
    hash_password,
    verify_password,
    verify_token,
)
from datetime import timedelta
from fastapi import Depends, HTTPException
from security.security import generate_reset_token
from datetime import datetime
from gmail.gmail import send_verification_email
from config.config import access_token_time

ACCESS_TOKEN_EXPIRE_DAYS = int(access_token_time)

signin_router = APIRouter(
    prefix="/signin",
)


# Google endpoint
@signin_router.post("/google-signup")
async def signup(users: UserInfo):
    user_data = users.model_dump()
    # Hash the password before storing it
    if user_data["password"]:
        user_data["password"] = hash_password(user_data["password"])

    # Filter out fields with None values
    user_data = {key: value for key, value in user_data.items() if value is not None}

    _ = collection.insert_one(user_data).inserted_id

    if "_id" in user_data:
        user_data["_id"] = str(user_data["_id"])

    access_token = create_access_token(
        {"email_address": user_data["email_address"]},
        timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS),
    )

    return {"access_token": access_token}


# Route to get user details using the token
@signin_router.post("/user-details")
async def user_details(current_user: dict = Depends(verify_token)):
    user_info = {
        "email_address": current_user.get("email_address"),
    }
    return {"user_details": user_info}


# Endpoint to verify the user's password
@signin_router.post("/verify-password")
async def verify_user_password(data: VerifyPasswordData):
    # Retrieve the user's data from the database based on the provided email_address
    user_data = collection.find_one({"email_address": data.email_address})

    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the provided password matches the hashed password in the database
    if not verify_password(data.password, user_data["password"]):
        raise HTTPException(status_code=401, detail="Incorrect password")

    return {"message": "Password verified successfully"}


# Modify your signup route to include email verification
@signin_router.post("/signup")
async def signup(user: UserInfo):
    # Check if the user already exists
    existing_user = collection.find_one({"email_address": user.email_address})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Hash the password securely
    hashed_password = hash_password(user.password)

    # Generate a random verification token
    token = generate_reset_token()

    # Create a document to store in the database
    user_data = {
        "email_address": user.email_address,
        "password": hashed_password,
        "verified": False,
        "verification_token": token,
        "registration_date": datetime.now(),
    }

    # Insert the user data into the database
    inserted_user = collection.insert_one(user_data)

    if inserted_user:
        # Send a verification email to the user
        send_verification_email(user.email_address, token, "signin/verify")

        # Return a response indicating successful registration
        return {
            "message": "Registration successful. Check your email for verification instructions."
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to register the user")


# Verification endpoint for confirming the email address
@signin_router.get("/verify")
async def verify_email(token: str):
    # Find the user with the given verification token
    user = collection.find_one({"verification_token": token, "verified": False})

    if user:
        # Update the user's status to verified
        collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"verified": True, "verification_token": None}},
        )

        # Redirect the user to the home page or display a success message
        # You can use a front-end framework for a more interactive experience

        return {"message": "Email address verified. You can now login."}
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid verification token or email is already verified.",
        )


@signin_router.post("/login")
async def login(users: UserInfo):
    user_data = users.model_dump()

    # Check if the 'password' field is not null before hashing it and storing it
    if user_data.get("password") is not None:
        user_data["password"] = hash_password(user_data["password"])

    user = collection.find_one({"email_address": user_data["email_address"]})

    if user is None:
        raise HTTPException(status_code=400, detail="Please sign up first.")

    user_data_db = collection.find_one({"email_address": users.email_address})

    # Verify the provided password against the hashed password
    if not verify_password(users.password, user_data_db["password"]):
        raise HTTPException(status_code=401, detail="Incorrect password")

    if not user["verified"]:
        raise HTTPException(status_code=400, detail="Please verify your email first.")

    # Filter out fields with None values
    user_data = {key: value for key, value in user_data.items() if value is not None}

    if user_data:
        if "_id" in user_data:
            user_data["_id"] = str(user_data["_id"])

        access_token = create_access_token(
            {"email_address": user_data["email_address"]},
            timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS),
        )

        return {"access_token": access_token}
    else:
        raise HTTPException(status_code=400, detail="No valid data provided for login")
