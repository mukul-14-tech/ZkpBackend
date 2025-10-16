from sqlalchemy import Column, Integer, DateTime, LargeBinary, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    enc_name = Column(LargeBinary, nullable=False)
    enc_age = Column(LargeBinary, nullable=False)
    name_nonce = Column(LargeBinary, nullable=False)
    name_tag = Column(LargeBinary, nullable=False)
    age_nonce = Column(LargeBinary, nullable=False)
    age_tag = Column(LargeBinary, nullable=False)
    status = Column(String(20), default="active")