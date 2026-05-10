from sqlalchemy import Column, String, Date, TIMESTAMP
from sqlalchemy.sql import func
from db.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    wca_id = Column(String)
    name = Column(String)
    email = Column(String, index=True)
    hashed_password = Column(String)
    gender = Column(String)
    dob = Column(Date)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=True)
    deleted_at = Column(TIMESTAMP, nullable=True)

    # relationships