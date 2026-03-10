from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from core.database import get_db
from models.domain import Session as SessionModel
from services.session_service import SessionService

# Quick schemas for router boundaries
class CreateSessionRequest(BaseModel):
    client_id: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

router = APIRouter(prefix="/sessions", tags=["sessions"])

def get_session_service(db: Session = Depends(get_db)) -> SessionService:
    return SessionService(db=db)

@router.post("/", status_code=201)
async def create_session(request: CreateSessionRequest, service: SessionService = Depends(get_session_service)):
    """Create new MBP session with question-based flow using DB layer"""
    try:
        session = service.create_session(client_id=request.client_id, metadata=request.metadata)
        return {
            "session_id": session.id,
            "status": "created",
            "created_at": session.created_at.isoformat(),
            "current_phase": "safety",
            "message": "Session created successfully."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{session_id}")
async def get_session(session_id: str, service: SessionService = Depends(get_session_service)):
    """Get current session state"""
    try:
        session = service.get_session(session_id)
        return {"session_id": session.id, "status": session.status, "current_phase": session.current_phase}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

