from sqlalchemy import Column, String, Date, TIMESTAMP
from sqlalchemy.sql import func
from db.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    wca_id = Column(String(10), nullable=True)
    name = Column(String(45), nullable=False)
    email = Column(String(45), nullable=False)
    hashed_password = Column(String(100))
    gender = Column(String(1), nullable=False)
    dob = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=True)
    deleted_at = Column(TIMESTAMP, nullable=True)

    organized_competitions = relationship("CompetitionOrganizer", back_populates="user")
    competition_registrations = relationship("CompetitionRegistration", back_populates="user")
    result_users = relationship("ResultUser", back_populates="user", cascade="all, delete-orphan")