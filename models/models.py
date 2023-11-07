from pydantic import BaseModel


class User(BaseModel):
    username: str | None = None


class UserEmail(BaseModel):
    email_address: str = None


class UserInfo(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email_address: str | None = None
    image_url: str | None = None
    password: str | None = None


# class ManualSignup(BaseModel):
#     email: str | None = None
#     password: str | None = None


# Create a Pydantic model for input data
class VerifyPasswordData(BaseModel):
    email_address: str
    password: str


# Models
class UserCreate(BaseModel):
    email_address: str


class UserResetPassword(BaseModel):
    email_address: str
    new_password: str
    confirm_password: str
