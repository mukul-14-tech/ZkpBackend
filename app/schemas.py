from pydantic import BaseModel
from typing import Optional

class UserRegistrationRequest(BaseModel):
    name: str
    age: int
    fingerprint_image_path: str  # Path to fingerprint image
    password: str  # User's password for key derivation

class UserRegistrationResponse(BaseModel):
    user_id: int
    status: str
    message: str