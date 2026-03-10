from typing import Optional, List
from sqlalchemy.orm import Session as DBSession
from repositories.base import BaseRepository
from models.domain import Session, Answer

class SessionRepository(BaseRepository[Session]):
    def __init__(self, db: DBSession):
        super().__init__(model=Session, session=db)

    def get_by_client_id(self, client_id: str) -> List[Session]:
        return self.session.query(Session).filter(Session.client_id == client_id).all()

class AnswerRepository(BaseRepository[Answer]):
    def __init__(self, db: DBSession):
        super().__init__(model=Answer, session=db)

    def get_by_session_id(self, session_id: str) -> List[Answer]:
        return self.session.query(Answer).filter(Answer.session_id == session_id).all()
