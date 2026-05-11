from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base
from sqlalchemy.dialects.mysql import TINYINT


class Result(Base):
    __tablename__ = "results"

    id = Column(String(36), primary_key=True, index=True)
    round_id = Column(String(36), ForeignKey("competition_rounds.id"), nullable=False)
    best = Column(Integer, nullable=False)
    average = Column(Integer, nullable=False)

    round = relationship("CompetitionRound", back_populates="results")
    attempts = relationship("ResultAttempt", back_populates="result", cascade="all, delete-orphan")
    result_users = relationship("ResultUser", back_populates="result", cascade="all, delete-orphan")


class ResultAttempt(Base):
    __tablename__ = "result_attempts"

    result_id = Column(String(36), ForeignKey("results.id"), primary_key=True)
    attempt_number = Column(TINYINT(unsigned=True), primary_key=True)
    value = Column(Integer, nullable=False)

    result = relationship("Result", back_populates="attempts")


class ResultUser(Base):
    __tablename__ = "result_users"

    result_id = Column(String(36), ForeignKey("results.id"), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)

    result = relationship("Result", back_populates="result_users")
    user = relationship("User", back_populates="result_users")