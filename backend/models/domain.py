"""
MBP v2.0 - SQLAlchemy Domain Models
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, ForeignKey, Float
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    nama = Column(String, nullable=False)
    tanggal_lahir = Column(String)
    tempat_lahir = Column(String)
    agama = Column(String)
    last_phase = Column(Integer, default=0)
    last_session_id = Column(String, nullable=True)
    status = Column(String, default="active")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sessions = relationship("Session", back_populates="client")


class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    status = Column(String, default="active")
    current_phase = Column(String, default="safety")
    current_phase_number = Column(Integer, default=0)
    phase_complete = Column(Boolean, default=False)
    session_metadata = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    client = relationship("Client", back_populates="sessions")
    answers = relationship("Answer", back_populates="session")


class Answer(Base):
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    question_id = Column(String, nullable=False)
    question_text = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    phase = Column(String, nullable=False)
    dimensions = Column(JSON, default=list)
    question_type = Column(String, default="fixed")
    order_index = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="answers")
