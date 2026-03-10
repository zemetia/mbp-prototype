"""
MBP Prototype API - LangGraph Implementation (HTTP Only)
MirrorBreak Protocol with Timestamp Tracking
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
import uuid
import time
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3
import os

# LangGraph imports
from graph import run_mbp_graph
from state import Phase

# Database setup
DB_PATH = "mbp_sessions.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            phase TEXT DEFAULT 'safety_check',
            status TEXT DEFAULT 'active',
            safety_cleared BOOLEAN DEFAULT FALSE,
            graph_state JSON,
            final_profile JSON,
            overall_confidence REAL DEFAULT 0.0
        )
    ''')
    
    # Messages table with timing metadata
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            phase TEXT,
            response_timestamp TEXT,      -- ISO timestamp of when response was received
            response_time_ms INTEGER,     -- Time taken to respond (for user responses)
            processing_time_ms INTEGER,   -- Time taken by AI processing
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''')
    
    # Response timing log for detailed analysis
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS response_timings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            message_id INTEGER,
            received_at TEXT,             -- When request was received
            processing_started_at TEXT,   -- When AI processing started
            processing_ended_at TEXT,     -- When AI processing ended
            response_sent_at TEXT,        -- When response was sent
            total_duration_ms INTEGER,    -- Total round-trip time
            ai_duration_ms INTEGER,       -- Time in AI/graph processing
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''')
    
    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="MBP LangGraph API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATABASE HELPERS
# ============================================================================

def get_session(session_id: str) -> Optional[Dict]:
    """Get session from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "created_at": row[1],
            "updated_at": row[2],
            "phase": row[3],
            "status": row[4],
            "safety_cleared": row[5],
            "graph_state": json.loads(row[6]) if row[6] else None,
            "final_profile": json.loads(row[7]) if row[7] else None,
            "overall_confidence": row[8]
        }
    return None

def create_session(session_id: str):
    """Create new session"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (id, phase) VALUES (?, ?)",
        (session_id, Phase.SAFETY_CHECK.value)
    )
    conn.commit()
    conn.close()

def update_session(session_id: str, updates: Dict):
    """Update session"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [session_id]
    
    cursor.execute(f"UPDATE sessions SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()

def add_message(session_id: str, role: str, content: str, phase: str, 
                response_timestamp: Optional[str] = None,
                response_time_ms: Optional[int] = None,
                processing_time_ms: Optional[int] = None) -> int:
    """Add message to session with timing data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO messages 
           (session_id, role, content, phase, response_timestamp, response_time_ms, processing_time_ms) 
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (session_id, role, content, phase, response_timestamp, response_time_ms, processing_time_ms)
    )
    message_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return message_id

def add_timing_log(session_id: str, message_id: int, timings: Dict):
    """Add detailed timing log"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO response_timings 
           (session_id, message_id, received_at, processing_started_at, 
            processing_ended_at, response_sent_at, total_duration_ms, ai_duration_ms)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (session_id, message_id,
         timings.get("received_at"),
         timings.get("processing_started_at"),
         timings.get("processing_ended_at"),
         timings.get("response_sent_at"),
         timings.get("total_duration_ms"),
         timings.get("ai_duration_ms"))
    )
    conn.commit()
    conn.close()

def get_messages(session_id: str) -> List[Dict]:
    """Get all messages for session with timing data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT role, content, phase, response_timestamp, response_time_ms, 
                  processing_time_ms, timestamp 
           FROM messages WHERE session_id = ? ORDER BY id""",
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "role": row[0],
            "content": row[1],
            "phase": row[2],
            "response_timestamp": row[3],
            "response_time_ms": row[4],
            "processing_time_ms": row[5],
            "timestamp": row[6]
        }
        for row in rows
    ]

def get_timings(session_id: str) -> List[Dict]:
    """Get all timing logs for session"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM response_timings WHERE session_id = ? ORDER BY id""",
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "received_at": row[3],
            "processing_started_at": row[4],
            "processing_ended_at": row[5],
            "response_sent_at": row[6],
            "total_duration_ms": row[7],
            "ai_duration_ms": row[8]
        }
        for row in rows
    ]

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy", 
        "service": "mbp-langgraph", 
        "version": "2.1.0",
        "websocket": False,
        "timestamp_tracking": True
    }

@app.post("/sessions")
async def create_new_session():
    """Create new assessment session"""
    session_id = str(uuid.uuid4())
    create_session(session_id)
    
    return {
        "session_id": session_id,
        "phase": Phase.SAFETY_CHECK.value,
        "message": "Session created. Begin with safety check.",
        "next_action": "awaiting_response",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/sessions/{session_id}")
async def get_session_status(session_id: str):
    """Get session status"""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = get_messages(session_id)
    timings = get_timings(session_id)
    
    # Calculate average response times
    avg_response_time = None
    response_times = [m["response_time_ms"] for m in messages if m["response_time_ms"]]
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
    
    return {
        "session_id": session_id,
        "phase": session["phase"],
        "status": session["status"],
        "safety_cleared": session["safety_cleared"],
        "overall_confidence": session["overall_confidence"],
        "message_count": len(messages),
        "final_profile_available": session["final_profile"] is not None,
        "avg_response_time_ms": avg_response_time,
        "timing_logs_count": len(timings),
        "created_at": session["created_at"],
        "updated_at": session["updated_at"]
    }

@app.post("/sessions/{session_id}/respond")
async def process_response(session_id: str, request: Dict):
    """Process user response through LangGraph with timestamp tracking"""
    
    # Record start time
    received_at = datetime.utcnow()
    received_ts = received_at.isoformat()
    start_time_ms = int(time.time() * 1000)
    
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session["status"] == "completed":
        raise HTTPException(status_code=400, detail="Session already completed")
    
    if session["status"] == "aborted":
        raise HTTPException(status_code=400, detail="Session was aborted")
    
    user_response = request.get("message", "").strip()
    if not user_response:
        raise HTTPException(status_code=400, detail="Empty message")
    
    # Extract timing metadata from client
    client_timestamp = request.get("client_timestamp")  # ISO timestamp from client
    client_response_time_ms = request.get("response_time_ms")  # Time user took to respond
    
    current_phase = session["phase"]
    
    # Add user message with timing data
    message_id = add_message(
        session_id, 
        "user", 
        user_response, 
        current_phase,
        response_timestamp=client_timestamp or received_ts,
        response_time_ms=client_response_time_ms
    )
    
    # Get all messages
    messages = get_messages(session_id)
    
    # Get previous graph state if exists
    previous_state = session.get("graph_state")
    
    # Record processing start
    processing_started_at = datetime.utcnow().isoformat()
    
    try:
        # Run LangGraph
        result = await run_mbp_graph(
            session_id=session_id,
            user_response=user_response,
            messages=messages,
            previous_state=previous_state
        )
        
        # Record processing end
        processing_ended_at = datetime.utcnow()
        processing_ended_ts = processing_ended_at.isoformat()
        
        # Calculate timing metrics
        ai_duration_ms = int(time.time() * 1000) - start_time_ms
        
        # Extract results
        new_phase = result.get("current_phase", current_phase)
        next_question = result.get("next_question")
        safety_cleared = result.get("safety_cleared", False)
        final_profile = result.get("final_profile")
        overall_confidence = result.get("overall_confidence", 0.0)
        
        # Handle aborted
        if new_phase == Phase.ABORTED.value or new_phase == "aborted":
            update_session(session_id, {
                "status": "aborted",
                "phase": Phase.ABORTED.value,
                "graph_state": json.dumps(result),
                "updated_at": received_ts
            })
            
            # Log timing
            response_sent_at = datetime.utcnow().isoformat()
            total_duration_ms = int(time.time() * 1000) - start_time_ms
            add_timing_log(session_id, message_id, {
                "received_at": received_ts,
                "processing_started_at": processing_started_at,
                "processing_ended_at": processing_ended_ts,
                "response_sent_at": response_sent_at,
                "total_duration_ms": total_duration_ms,
                "ai_duration_ms": ai_duration_ms
            })
            
            return {
                "session_id": session_id,
                "phase": Phase.ABORTED.value,
                "status": "aborted",
                "message": "Session aborted due to safety concerns.",
                "safety_data": result.get("safety_data", {}),
                "next_action": "refer_to_support",
                "timing": {
                    "received_at": received_ts,
                    "processed_at": processing_ended_ts,
                    "duration_ms": total_duration_ms
                }
            }
        
        # Determine response
        if final_profile:
            # Session complete
            update_session(session_id, {
                "phase": Phase.CLOSURE.value,
                "status": "completed",
                "safety_cleared": safety_cleared,
                "graph_state": json.dumps(result),
                "final_profile": json.dumps(final_profile),
                "overall_confidence": overall_confidence,
                "updated_at": received_ts
            })
            
            # Add system message with timing
            summary = final_profile.get("core_summary", "Profile generated.")
            add_message(
                session_id, 
                "system", 
                summary, 
                Phase.CLOSURE.value,
                processing_time_ms=ai_duration_ms
            )
            
            # Log timing
            response_sent_at = datetime.utcnow().isoformat()
            total_duration_ms = int(time.time() * 1000) - start_time_ms
            add_timing_log(session_id, message_id, {
                "received_at": received_ts,
                "processing_started_at": processing_started_at,
                "processing_ended_at": processing_ended_ts,
                "response_sent_at": response_sent_at,
                "total_duration_ms": total_duration_ms,
                "ai_duration_ms": ai_duration_ms
            })
            
            return {
                "session_id": session_id,
                "phase": Phase.CLOSURE.value,
                "status": "completed",
                "profile": final_profile,
                "overall_confidence": overall_confidence,
                "message": summary,
                "next_action": "session_complete",
                "timing": {
                    "received_at": received_ts,
                    "processed_at": processing_ended_ts,
                    "ai_duration_ms": ai_duration_ms,
                    "total_duration_ms": total_duration_ms
                }
            }
        
        elif next_question:
            # Need to ask more questions
            update_session(session_id, {
                "phase": new_phase.value if isinstance(new_phase, Phase) else new_phase,
                "safety_cleared": safety_cleared,
                "graph_state": json.dumps(result),
                "overall_confidence": overall_confidence,
                "updated_at": received_ts
            })
            
            # Add assistant message with timing
            add_message(
                session_id, 
                "assistant", 
                next_question, 
                new_phase.value if isinstance(new_phase, Phase) else new_phase,
                processing_time_ms=ai_duration_ms
            )
            
            # Log timing
            response_sent_at = datetime.utcnow().isoformat()
            total_duration_ms = int(time.time() * 1000) - start_time_ms
            add_timing_log(session_id, message_id, {
                "received_at": received_ts,
                "processing_started_at": processing_started_at,
                "processing_ended_at": processing_ended_ts,
                "response_sent_at": response_sent_at,
                "total_duration_ms": total_duration_ms,
                "ai_duration_ms": ai_duration_ms
            })
            
            return {
                "session_id": session_id,
                "phase": new_phase.value if isinstance(new_phase, Phase) else new_phase,
                "status": "active",
                "message": next_question,
                "overall_confidence": overall_confidence,
                "next_action": "awaiting_response",
                "timing": {
                    "received_at": received_ts,
                    "processed_at": processing_ended_ts,
                    "ai_duration_ms": ai_duration_ms,
                    "total_duration_ms": total_duration_ms
                }
            }
        
        else:
            # Unexpected state
            return {
                "session_id": session_id,
                "phase": new_phase.value if isinstance(new_phase, Phase) else new_phase,
                "status": "active",
                "message": "Terima kasih. Mohon tunggu...",
                "next_action": "processing",
                "timing": {
                    "received_at": received_ts,
                    "ai_duration_ms": ai_duration_ms
                }
            }
            
    except Exception as e:
        print(f"[Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}/profile")
async def get_profile(session_id: str):
    """Get final profile"""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session["final_profile"]:
        raise HTTPException(status_code=400, detail="Profile not yet generated")
    
    return {
        "session_id": session_id,
        "profile": session["final_profile"],
        "overall_confidence": session["overall_confidence"],
        "phase": session["phase"]
    }

@app.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    """Get all messages for session with timing data"""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = get_messages(session_id)
    return {
        "session_id": session_id,
        "messages": messages
    }

@app.get("/sessions/{session_id}/timings")
async def get_session_timings(session_id: str):
    """Get detailed timing logs for analysis"""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    timings = get_timings(session_id)
    messages = get_messages(session_id)
    
    # Calculate statistics
    if timings:
        avg_ai_time = sum(t["ai_duration_ms"] for t in timings) / len(timings)
        avg_total_time = sum(t["total_duration_ms"] for t in timings) / len(timings)
    else:
        avg_ai_time = None
        avg_total_time = None
    
    return {
        "session_id": session_id,
        "timings": timings,
        "statistics": {
            "total_responses": len(timings),
            "avg_ai_duration_ms": avg_ai_time,
            "avg_total_duration_ms": avg_total_time
        },
        "messages_with_timing": len([m for m in messages if m["response_time_ms"]])
    }

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
