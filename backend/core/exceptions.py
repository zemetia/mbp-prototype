class MBPBaseException(Exception):
    pass

class QuestionFlowException(MBPBaseException):
    def __init__(self, message: str, phase: str = None):
        super().__init__(message)
        self.phase = phase

class SessionNotFoundException(MBPBaseException):
    def __init__(self, session_id: str):
        super().__init__(f"Session {session_id} not found")
        self.session_id = session_id

class DatabaseException(MBPBaseException):
    pass
