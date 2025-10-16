from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import SessionLocal, init_db
from app.models import Base, User
from app.schemas import UserRegistrationRequest, UserRegistrationResponse, UserDecryptionRequest, UserDecryptionResponse
from app.fp_utils import get_fingerprint_embedding
from app.key_utils import generate_key_from_embedding
from app.encryption import encrypt_data, decrypt_data
from app.faiss_store import FaissStore
import os

app = FastAPI()

# Initialize database
init_db(Base)

# Initialize FaissStore
faiss_store = FaissStore()

# Clear old data and sync with database
print("DEBUG: Clearing old FaissStore data...")
faiss_store.reset_index()
print("DEBUG: FaissStore cleared")

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
            name_nonce=name_nonce,
            name_tag=name_tag,
            age_nonce=age_nonce,
            age_tag=age_tag,
            status="active"
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 5. Add embedding to FaissStore for future matching
        print(f"DEBUG: Adding user {user.user_id} to FaissStore...")
        faiss_store.add(embedding, user.user_id)
        print(f"DEBUG: FaissStore now has {faiss_store.count()} embeddings")
        print(f"DEBUG: FaissStore user IDs: {list(faiss_store.data.keys())}")
        
        return UserRegistrationResponse(
            user_id=user.user_id,
            status="success",
            message="User registered successfully"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/decrypt", response_model=UserDecryptionResponse)
async def decrypt_user_data(request_data: UserDecryptionRequest, db: Session = Depends(get_db)):
    try:
        # 1. Get fingerprint embedding from the provided image
        query_embedding = get_fingerprint_embedding(request_data.fingerprint_image_path)
        
        # 2. Search for the most similar embedding in FaissStore
        similar_users = faiss_store.search_similar(query_embedding, k=1)
        
        if not similar_users:
            # Debug: Check what's in FaissStore
            all_users = db.query(User).all()
            db_user_ids = [u.user_id for u in all_users]
            faiss_user_ids = list(faiss_store.data.keys())
            
            debug_info = {
                "database_user_ids": db_user_ids,
                "faiss_user_ids": faiss_user_ids,
                "faiss_count": faiss_store.count(),
                "db_count": len(db_user_ids)
            }
            
            raise HTTPException(
                status_code=404, 
                detail=f"No matching fingerprint found. Debug info: {debug_info}"
            )
        
        # Get the highest match
        matched_user_id, similarity_score = similar_users[0]
        
        # 3. Retrieve user data from PostgreSQL
        user = db.query(User).filter(User.user_id == matched_user_id).first()
        if not user:
            # Debug: Check what users exist in database vs FaissStore
            all_users = db.query(User).all()
            db_user_ids = [u.user_id for u in all_users]
            faiss_user_ids = list(faiss_store.data.keys())
            
            debug_info = {
                "database_user_ids": db_user_ids,
                "faiss_user_ids": faiss_user_ids,
                "matched_user_id": matched_user_id,
                "matched_user_id_type": type(matched_user_id).__name__
            }
            
            raise HTTPException(
                status_code=404, 
                detail=f"User data not found in database. Debug info: {debug_info}"
            )
        
        # 4. Generate the same AES key using embedding + password
        aes_key = generate_key_from_embedding(query_embedding, request_data.password)
        
        # 5. Decrypt the user data
        try:
            print(f"DEBUG: Attempting decryption with key length: {len(aes_key)}")
            print(f"DEBUG: User data lengths - name: {len(user.enc_name)}, age: {len(user.enc_age)}")
            print(f"DEBUG: Name nonce length: {len(user.name_nonce)}, name tag length: {len(user.name_tag)}")
            print(f"DEBUG: Age nonce length: {len(user.age_nonce)}, age tag length: {len(user.age_tag)}")
            
            decrypted_name = decrypt_data(user.enc_name, aes_key, user.name_nonce, user.name_tag)
            print(f"DEBUG: Name decrypted successfully: {decrypted_name}")
            
            decrypted_age = decrypt_data(user.enc_age, aes_key, user.age_nonce, user.age_tag)
            print(f"DEBUG: Age decrypted successfully: {decrypted_age}")
            
        except Exception as decrypt_error:
            print(f"DEBUG: Decryption error: {str(decrypt_error)}")
            print(f"DEBUG: Error type: {type(decrypt_error).__name__}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=400, detail=f"Decryption failed: {str(decrypt_error)}")
        
        return UserDecryptionResponse(
            user_id=matched_user_id,
            name=decrypted_name,
            age=int(decrypted_age),
            status="success",
            message="User data decrypted successfully",
            similarity_score=similarity_score
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
async def root():
    return {"message": "ZKP Backend API"}

@app.get("/debug")
async def debug_info(db: Session = Depends(get_db)):
    """Debug endpoint to check database and FaissStore state"""
    # Get all users from database
    all_users = db.query(User).all()
    db_user_ids = [u.user_id for u in all_users]
    
    # Get all user IDs from FaissStore
    faiss_user_ids = list(faiss_store.data.keys())
    
    return {
        "database_user_ids": db_user_ids,
        "faiss_user_ids": faiss_user_ids,
        "faiss_count": faiss_store.count(),
        "db_count": len(db_user_ids)
    }