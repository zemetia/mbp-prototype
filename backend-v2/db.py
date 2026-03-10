"""
Database persistence module for MBP Prototype
Handles PostgreSQL operations for clients, sessions, and answers
"""
import os
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mbp_prototype")

# Import psycopg2 or use asyncpg
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False

# In-memory fallback (for development without database)
_in_memory_mode = not PSYCOPG2_AVAILABLE and not ASYNCPG_AVAILABLE

# In-memory stores (fallback)
_clients_store: Dict[str, Dict] = {}
_sessions_store: Dict[str, Dict] = {}
_answers_store: Dict[str, List[Dict]] = {}


@contextmanager
def get_db_connection():
    """Get database connection context manager"""
    if _in_memory_mode:
        yield None
        return
    
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize database tables"""
    global _in_memory_mode
    
    if _in_memory_mode:
        print("⚠️  Running in IN-MEMORY mode (no PostgreSQL)")
        return True
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Read and execute schema
                schema_path = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')
                if os.path.exists(schema_path):
                    with open(schema_path, 'r') as f:
                        cur.execute(f.read())
                    conn.commit()
                    print("✅ Database initialized")
                    return True
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        print("⚠️  Falling back to IN-MEMORY mode")
        _in_memory_mode = True
        return False


# ==================== CLIENT OPERATIONS ====================

def create_client(nama: str, tanggal_lahir: str, tempat_lahir: str, agama: str) -> Dict[str, Any]:
    """Create a new client (called when starting new analysis)"""
    client_id = str(uuid.uuid4())
    
    if _in_memory_mode:
        _clients_store[client_id] = {
            "id": client_id,
            "nama": nama,
            "tanggal_lahir": tanggal_lahir,
            "tempat_lahir": tempat_lahir,
            "agama": agama,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_phase": 0,
            "last_session_id": None,
            "status": "active"
        }
        return _clients_store[client_id]
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO clients (id, nama, tanggal_lahir, tempat_lahir, agama)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
            """, (client_id, nama, tanggal_lahir, tempat_lahir, agama))
            result = dict(cur.fetchone())
            conn.commit()
            return result


def get_client(client_id: str) -> Optional[Dict[str, Any]]:
    """Get client by ID"""
    if _in_memory_mode:
        return _clients_store.get(client_id)
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM clients WHERE id = %s", (client_id,))
            result = cur.fetchone()
            return dict(result) if result else None


def update_client_phase(client_id: str, phase: int, session_id: Optional[str] = None):
    """Update client's last phase"""
    if _in_memory_mode:
        if client_id in _clients_store:
            _clients_store[client_id]["last_phase"] = phase
            _clients_store[client_id]["updated_at"] = datetime.now().isoformat()
            if session_id:
                _clients_store[client_id]["last_session_id"] = session_id
        return
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE clients 
                SET last_phase = %s, 
                    last_session_id = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (phase, session_id, client_id))
            conn.commit()


def get_client_by_name(nama: str) -> Optional[Dict[str, Any]]:
    """Find client by name (for continuing analysis)"""
    if _in_memory_mode:
        for client in _clients_store.values():
            if client["nama"].lower() == nama.lower():
                return client
        return None
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM clients WHERE nama = %s", (nama,))
            result = cur.fetchone()
            return dict(result) if result else None


def list_clients() -> List[Dict[str, Any]]:
    """List all clients"""
    if _in_memory_mode:
        return list(_clients_store.values())
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM clients ORDER BY updated_at DESC")
            return [dict(row) for row in cur.fetchall()]


# ==================== SESSION OPERATIONS ====================

def create_session(client_id: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
    """Create a new session for a client"""
    import uuid
    session_id = str(uuid.uuid4())
    
    if _in_memory_mode:
        _sessions_store[session_id] = {
            "id": session_id,
            "client_id": client_id,
            "status": "active",
            "current_phase": "safety",
            "current_phase_number": 0,
            "phase_complete": False,
            "ai_processing_complete": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "completed_at": None,
            "metadata": json.dumps(metadata) if metadata else '{}'
        }
        # Update client's last_session_id
        update_client_phase(client_id, 0, session_id)
        return _sessions_store[session_id]
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sessions (id, client_id, status, current_phase, current_phase_number, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (session_id, client_id, 'active', 'safety', 0, json.dumps(metadata or {})))
            result = dict(cur.fetchone())
            conn.commit()
            
            # Update client's last_session_id
            update_client_phase(client_id, 0, session_id)
            
            return result


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session by ID"""
    if _in_memory_mode:
        return _sessions_store.get(session_id)
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM sessions WHERE id = %s", (session_id,))
            result = cur.fetchone()
            return dict(result) if result else None


def update_session_phase(session_id: str, phase: str, phase_number: int, 
                         phase_complete: bool = False):
    """Update session phase"""
    if _in_memory_mode:
        if session_id in _sessions_store:
            _sessions_store[session_id]["current_phase"] = phase
            _sessions_store[session_id]["current_phase_number"] = phase_number
            _sessions_store[session_id]["phase_complete"] = phase_complete
            _sessions_store[session_id]["updated_at"] = datetime.now().isoformat()
            
            # Update client's last_phase
            client_id = _sessions_store[session_id]["client_id"]
            update_client_phase(client_id, phase_number, session_id)
        return
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE sessions 
                SET current_phase = %s,
                    current_phase_number = %s,
                    phase_complete = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING client_id
            """, (phase, phase_number, phase_complete, session_id))
            result = cur.fetchone()
            conn.commit()
            
            # Update client's last_phase
            if result:
                client_id = result[0]
                update_client_phase(client_id, phase_number, session_id)


def complete_session(session_id: str):
    """Mark session as completed"""
    if _in_memory_mode:
        if session_id in _sessions_store:
            _sessions_store[session_id]["status"] = "completed"
            _sessions_store[session_id]["completed_at"] = datetime.now().isoformat()
        return
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE sessions 
                SET status = 'completed',
                    completed_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (session_id,))
            conn.commit()


def get_client_sessions(client_id: str) -> List[Dict[str, Any]]:
    """Get all sessions for a client"""
    if _in_memory_mode:
        return [s for s in _sessions_store.values() if s["client_id"] == client_id]
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM sessions 
                WHERE client_id = %s 
                ORDER BY created_at DESC
            """, (client_id,))
            return [dict(row) for row in cur.fetchall()]


# ==================== ANSWER OPERATIONS ====================

def save_answer(client_id: str, session_id: str, question_id: str, 
                question_text: str, answer: str, phase: str,
                dimensions: List[str] = None, question_type: str = "fixed",
                order_index: int = 0) -> Dict[str, Any]:
    """Save an answer to the database"""
    if _in_memory_mode:
        answer_data = {
            "id": len(_answers_store.get(session_id, [])),
            "client_id": client_id,
            "session_id": session_id,
            "question_id": question_id,
            "question_text": question_text,
            "answer": answer,
            "phase": phase,
            "dimensions": dimensions or [],
            "question_type": question_type,
            "order_index": order_index,
            "created_at": datetime.now().isoformat()
        }
        if session_id not in _answers_store:
            _answers_store[session_id] = []
        _answers_store[session_id].append(answer_data)
        return answer_data
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO answers 
                    (client_id, session_id, question_id, question_text, 
                     answer, phase, dimensions, question_type, order_index)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (client_id, session_id, question_id, question_text, 
                  answer, phase, json.dumps(dimensions or []), question_type, order_index))
            result = dict(cur.fetchone())
            conn.commit()
            return result


def get_session_answers(session_id: str) -> List[Dict[str, Any]]:
    """Get all answers for a session"""
    if _in_memory_mode:
        return _answers_store.get(session_id, [])
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM answers 
                WHERE session_id = %s 
                ORDER BY created_at ASC
            """, (session_id,))
            return [dict(row) for row in cur.fetchall()]


def get_client_answers(client_id: str) -> List[Dict[str, Any]]:
    """Get all answers for a client"""
    if _in_memory_mode:
        result = []
        for answers in _answers_store.values():
            for ans in answers:
                if ans["client_id"] == client_id:
                    result.append(ans)
        return result
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM answers 
                WHERE client_id = %s 
                ORDER BY created_at ASC
            """, (client_id,))
            return [dict(row) for row in cur.fetchall()]


def get_phase_answers(session_id: str, phase: str) -> List[Dict[str, Any]]:
    """Get answers for a specific phase"""
    if _in_memory_mode:
        answers = _answers_store.get(session_id, [])
        return [a for a in answers if a["phase"] == phase]
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM answers 
                WHERE session_id = %s AND phase = %s
                ORDER BY order_index ASC, created_at ASC
            """, (session_id, phase))
            return [dict(row) for row in cur.fetchall()]


# ==================== RESUME OPERATIONS ====================

def get_client_progress(client_id: str) -> Optional[Dict[str, Any]]:
    """Get client progress for resuming analysis"""
    client = get_client(client_id)
    if not client:
        return None
    
    # Get last session
    sessions = get_client_sessions(client_id)
    if not sessions:
        return {
            "client": client,
            "can_resume": False,
            "message": "No active session found"
        }
    
    last_session = sessions[0]  # Most recent
    session_id = last_session["id"]
    
    # Get answers for this session
    answers = get_session_answers(session_id)
    
    # Determine current phase
    current_phase = last_session.get("current_phase", "safety")
    current_phase_number = last_session.get("current_phase_number", 0)
    
    # Get answered question IDs for current phase
    answered_ids = [a["question_id"] for a in answers if a["phase"] == current_phase]
    
    return {
        "client": client,
        "session": last_session,
        "can_resume": last_session["status"] == "active",
        "current_phase": current_phase,
        "current_phase_number": current_phase_number,
        "total_answers": len(answers),
        "answered_question_ids": answered_ids,
        "last_answer": answers[-1] if answers else None
    }


def can_resume_analysis(client_id: str) -> bool:
    """Check if client can resume analysis"""
    progress = get_client_progress(client_id)
    if not progress:
        return False
    return progress.get("can_resume", False)


# ==================== BACKUP / EXPORT ====================

def export_session_data(session_id: str) -> Dict[str, Any]:
    """Export complete session data"""
    session = get_session(session_id)
    if not session:
        return None
    
    client = get_client(session["client_id"])
    answers = get_session_answers(session_id)
    
    return {
        "client": client,
        "session": session,
        "answers": answers,
        "export_time": datetime.now().isoformat()
    }
