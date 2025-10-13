from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import SessionLocal, init_db
from app.models import Base, User
from app.schemas import UserRegistrationRequest, UserRegistrationResponse
from app.fp_utils import get_fingerprint_embedding
from app.key_utils import generate_key_from_embedding
from app.encryption import encrypt_data
import os

app = FastAPI()

# Initialize database
init_db(Base)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register", response_model=UserRegistrationResponse)
async def register_user(user_data: UserRegistrationRequest, db: Session = Depends(get_db)):
    try:
        # 1. Get fingerprint embedding
        embedding = get_fingerprint_embedding(user_data.fingerprint_image_path)
        
        # 2. Generate AES key from embedding + password
        aes_key = generate_key_from_embedding(embedding, user_data.password)
        
        # 3. Encrypt name and age
        enc_name, name_nonce, name_tag = encrypt_data(user_data.name, aes_key)
        enc_age, age_nonce, age_tag = encrypt_data(str(user_data.age), aes_key)
        
        # 4. Create user record
        user = User(
            enc_name=enc_name,
            enc_age=enc_age,
            enc_nonce=name_nonce,  # Using name_nonce for simplicity
            enc_tag=name_tag,      # Using name_tag for simplicity
            status="active"
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return UserRegistrationResponse(
            user_id=user.user_id,
            status="success",
            message="User registered successfully"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
async def root():
    return {"message": "ZKP Backend API"}