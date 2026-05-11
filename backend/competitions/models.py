from sqlalchemy import Column, String, Integer, Boolean, Date, TIMESTAMP, ForeignKey, SmallInteger
from sqlalchemy.sql import func
from db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import SMALLINT, LONGTEXT


class Competition(Base):
    __tablename__ = "competitions"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    competitor_limit = Column(Integer, nullable=True)
    is_online = Column(Boolean, nullable=False, default=False)
    registration_start_time = Column(TIMESTAMP(timezone=False), nullable=False)
    registration_end_time = Column(TIMESTAMP(timezone=False), nullable=False)
    allow_on_site_registration = Column(Boolean, nullable=False, default=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=False), nullable=True, onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=False), nullable=True)

    rounds = relationship("CompetitionRound", back_populates="competition")
    activities = relationship("CompetitionActivity", back_populates="competition")
    info_tabs = relationship("CompetitionInfoTab", back_populates="competition")
    organizers = relationship("CompetitionOrganizer", back_populates="competition")
    registrations = relationship("CompetitionRegistration", back_populates="competition")
    venues = relationship("CompetitionVenue", back_populates="competition")


class CompetitionCustomEvent(Base):
    __tablename__ = "competition_custom_events"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(LONGTEXT, nullable=True)
    is_blindfolded = Column(Boolean, nullable=False, default=False)
    is_fmc = Column(Boolean, nullable=False, default=False)
    is_oh = Column(Boolean, nullable=False, default=False)
    is_feet = Column(Boolean, nullable=False, default=False)
    is_team = Column(Boolean, nullable=False, default=False)
    is_relay = Column(Boolean, nullable=False, default=False)
    is_miniguild = Column(Boolean, nullable=False, default=False)

    rounds = relationship("CompetitionRound", back_populates="custom_event")


class CompetitionRound(Base):
    __tablename__ = "competition_rounds"

    id = Column(String(36), primary_key=True, index=True)
    competition_id = Column(String(36), ForeignKey("competitions.id"), nullable=False)
    event_id = Column(String(25), nullable=False)
    round_type_id = Column(String(1), nullable=False)
    format_id = Column(String(1), nullable=False)
    time_limit = Column(Integer, nullable=True)
    cutoff_attempts = Column(Integer, nullable=True)
    cutoff_result = Column(Integer, nullable=True)
    advancement_condition_type = Column(String(15), nullable=True)
    advancement_condition_value = Column(Integer, nullable=True)
    custom_event_id = Column(String(36), ForeignKey("competition_custom_events.id"), nullable=True)

    competition = relationship("Competition", back_populates="rounds")
    custom_event = relationship("CompetitionCustomEvent", back_populates="rounds")
    activities = relationship("CompetitionActivity", back_populates="round")
    results = relationship("Result", back_populates="round")
    # this round's entry cumulative rounds
    cumulative_time_limit_entries = relationship("TimeLimitCumulativeRound", foreign_keys="[TimeLimitCumulativeRound.round_id]", back_populates="owner_round")
    # this round is included in other rounds' cumulative
    included_in_cumulative_limits = relationship("TimeLimitCumulativeRound", foreign_keys="[TimeLimitCumulativeRound.cumulative_round_id]", back_populates="included_round")


class CompetitionActivity(Base):
    __tablename__ = "competition_activities"

    id = Column(String(36), primary_key=True, index=True)
    display_name = Column(String(45), nullable=False)
    competition_id = Column(String(36), ForeignKey("competitions.id"), nullable=False)
    round_id = Column(String(36), ForeignKey("competition_rounds.id"), nullable=True)
    start_time = Column(TIMESTAMP(timezone=False), nullable=False)
    end_time = Column(TIMESTAMP(timezone=False), nullable=False)

    competition = relationship("Competition", back_populates="activities")
    round = relationship("CompetitionRound", back_populates="activities")


class CompetitionInfoTab(Base):
    __tablename__ = "competition_info_tabs"

    id = Column(String(36), primary_key=True, index=True)
    competition_id = Column(String(36), ForeignKey("competitions.id"), nullable=False)
    name = Column(String(45), nullable=False)
    data = Column(LONGTEXT, nullable=False)

    competition = relationship("Competition", back_populates="info_tabs")


class CompetitionOrganizer(Base):
    __tablename__ = "competition_organizers"

    id = Column(String(36), primary_key=True, index=True)
    competition_id = Column(String(36), ForeignKey("competitions.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=False), nullable=True, onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=False), nullable=True)

    competition = relationship("Competition", back_populates="organizers")
    user = relationship("User", back_populates="organized_competitions")


class CompetitionRegistration(Base):
    __tablename__ = "competition_registrations"

    id = Column(String(36), primary_key=True, index=True)
    competition_id = Column(String(36), ForeignKey("competitions.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")
    id_at_competition = Column(SMALLINT(unsigned=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=False), nullable=True, onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=False), nullable=True)

    competition = relationship("Competition", back_populates="registrations")
    user = relationship("User", back_populates="competition_registrations")


class CompetitionVenue(Base):
    __tablename__ = "competition_venues"

    id = Column(String(36), primary_key=True, index=True)
    competition_id = Column(String(36), ForeignKey("competitions.id"), nullable=False)
    name = Column(String(100), nullable=False)
    province = Column(String(20), nullable=False)
    latitude_microdegrees = Column(Integer, nullable=False)
    longitude_microdegrees = Column(Integer, nullable=False)

    competition = relationship("Competition", back_populates="venues")


class TimeLimitCumulativeRound(Base):
    __tablename__ = "time_limit_cumulative_rounds"

    id = Column(String(36), primary_key=True, index=True)
    round_id = Column(String(36), ForeignKey("competition_rounds.id"), nullable=False)
    cumulative_round_id = Column(String(36), ForeignKey("competition_rounds.id"), nullable=False)

    owner_round = relationship("CompetitionRound", foreign_keys=[round_id], back_populates="cumulative_time_limit_entries")
    included_round = relationship("CompetitionRound", foreign_keys=[cumulative_round_id], back_populates="included_in_cumulative_limits")