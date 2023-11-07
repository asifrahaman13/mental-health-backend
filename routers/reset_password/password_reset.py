from fastapi import APIRouter
from models.models import UserCreate, UserResetPassword
from connection.connection import collection
from security.security import generate_reset_token, hash_password
from gmail.gmail import send_verification_email
from fastapi import HTTPException

authentication_router = APIRouter(
    prefix="/authenticate",
)


# Create a user for password reset and send the reset email
@authentication_router.post("/forgot-password")
async def forgot_password(user: UserCreate):
    email_address = user.email_address

    # Check if the email exists in the database
    existing_user = collection.find_one({"email_address": email_address})

    if existing_user:
        collection.update_one(
            {"_id": existing_user["_id"]},
            {"$set": {"verified": False, "reset_token": None}},
        )
        # Generate a unique reset token and store it in the database
        reset_token = generate_reset_token()
        collection.update_one(
            {"_id": existing_user["_id"]}, {"$set": {"reset_token": reset_token}}
        )

        # Send a password reset email to the user
        send_verification_email(email_address, reset_token, "authenticate/reset")

        # Return a response indicating the email has been sent
        return {
            "message": "Password reset email sent. Check your email for instructions."
        }
    else:
        raise HTTPException(status_code=404, detail="Email not found in the database")


# Verification endpoint for confirming the email address
@authentication_router.get("/reset")
async def verify_email(token: str):
    # Find the user with the given verification token
    user = collection.find_one({"reset_token": token})

    if user:
        # Update the user's status to verified
        collection.update_one(
            {"_id": user["_id"]}, {"$set": {"verified": True, "reset_token": None}}
        )

        # Redirect the user to the home page or display a success message
        # You can use a front-end framework for a more interactive experience

        return {"message": "Email address verified. You can now change your password."}
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid verification token or email is already verified.",
        )


# Reset the user's password
@authentication_router.post("/reset-password")
async def reset_password(user: UserResetPassword):
    email_address = user.email_address
    new_password = user.new_password
    confirm_password = user.confirm_password

    # Find the user with the given email
    existing_user = collection.find_one({"email_address": email_address})

    if existing_user:
        if new_password != confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")

        # Hash the new password securely
        hashed_password = hash_password(new_password)

        # Update the user's password and clear the reset token
        collection.update_one(
            {"_id": existing_user["_id"]},
            {"$set": {"password": hashed_password, "reset_token": None}},
        )

        return {"message": "Password reset successful. You can now login."}
    else:
        raise HTTPException(status_code=404, detail="Email not found in the database")
