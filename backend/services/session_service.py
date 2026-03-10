from typing import Dict, Any, Optional
from repositories.session_repo import SessionRepository
from repositories.base import BaseRepository
from models.domain import Client, Session
from sqlalchemy.orm import Session as DBSession
from datetime import datetime
import json

class SessionService:
    def __init__(self, db: DBSession):
        self.session_repo = SessionRepository(db)
        self.client_repo = BaseRepository(model=Client, session=db)
    
    def create_session(self, client_id: str, metadata: Dict[str, Any] = None) -> Session:
        # First ensure client exists
        client = self.client_repo.get(client_id)
        if not client:
            raise ValueError(f"Client with id {client_id} not found")
            
        session_data = {
            "client_id": client_id,
            "status": "active",
            "current_phase": "safety",
            "current_phase_number": 0,
            "phase_complete": False,
            "session_metadata": metadata or {}
        }
        
        session = self.session_repo.create(session_data)
        
        # Update client last_session_id
        self.client_repo.update(client, {
            "last_session_id": session.id,
            "updated_at": datetime.utcnow()
        })
        
        return session
        
    def get_session(self, session_id: str) -> Optional[Session]:
        session = self.session_repo.get(session_id)
        if not session:
            raise ValueError(f"Session with id {session_id} not found")
        return session
