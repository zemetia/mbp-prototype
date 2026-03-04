from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3
import os

# Agent imports
from agents.analyzer import AnalyzerAgent
from agents.hypothesis_maker import HypothesisMakerAgent
from agents.question_maker import QuestionMakerAgent
from agents.assessor import AssessorAgent
from agents.synthesizer import SynthesizerAgent

# Database setup
DB_PATH = "mbp_sessions.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            phase INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            safety_cleared BOOLEAN DEFAULT FALSE,
            final_profile JSON,
            confidence_scores JSON
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            phase INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata JSON,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hypotheses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            field TEXT,
            hypothesis_text TEXT,
            confidence REAL,
            evidence JSON,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matrix_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            dimension TEXT,
            score INTEGER,
            confidence INTEGER,
            evidence JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''')
    
    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="MBP Prototype API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Initialize agents
analyzer = AnalyzerAgent()
hypothesis_maker = HypothesisMakerAgent()
question_maker = QuestionMakerAgent()
assessor = AssessorAgent()
synthesizer = SynthesizerAgent()

class SessionManager:
    @staticmethod
    def create_session() -> str:
        session_id = str(uuid.uuid4())[:8]
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (id, phase) VALUES (?, ?)",
            (session_id, 0)
        )
        conn.commit()
        conn.close()
        return session_id
    
    @staticmethod
    def get_session(session_id: str):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        return row
    
    @staticmethod
    def update_phase(session_id: str, phase: int):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE sessions SET phase = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (phase, session_id)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def save_message(session_id: str, role: str, content: str, phase: int, metadata: dict = None):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_id, role, content, phase, metadata) VALUES (?, ?, ?, ?, ?)",
            (session_id, role, content, phase, json.dumps(metadata) if metadata else None)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_messages(session_id: str, phase: int = None) -> List[dict]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        if phase is not None:
            cursor.execute(
                "SELECT role, content, phase, metadata FROM messages WHERE session_id = ? AND phase = ? ORDER BY timestamp",
                (session_id, phase)
            )
        else:
            cursor.execute(
                "SELECT role, content, phase, metadata FROM messages WHERE session_id = ? ORDER BY timestamp",
                (session_id,)
            )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "role": row[0],
                "content": row[1],
                "phase": row[2],
                "metadata": json.loads(row[3]) if row[3] else None
            }
            for row in rows
        ]
    
    @staticmethod
    def save_hypothesis(session_id: str, field: str, hypothesis: str, confidence: float, evidence: list):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO hypotheses (session_id, field, hypothesis_text, confidence, evidence) VALUES (?, ?, ?, ?, ?)",
            (session_id, field, hypothesis, confidence, json.dumps(evidence))
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_hypotheses(session_id: str) -> List[dict]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT field, hypothesis_text, confidence, evidence, status FROM hypotheses WHERE session_id = ? AND status = 'active'",
            (session_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "field": row[0],
                "hypothesis": row[1],
                "confidence": row[2],
                "evidence": json.loads(row[3]) if row[3] else [],
                "status": row[4]
            }
            for row in rows
        ]
    
    @staticmethod
    def save_matrix_score(session_id: str, dimension: str, score: int, confidence: int, evidence: list):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO matrix_scores (session_id, dimension, score, confidence, evidence) VALUES (?, ?, ?, ?, ?)",
            (session_id, dimension, score, confidence, json.dumps(evidence))
        )
        conn.commit()
        conn.close()

session_manager = SessionManager()

@app.post("/api/sessions")
async def create_session():
    """Create new anonymous assessment session"""
    session_id = session_manager.create_session()
    return {
        "session_id": session_id,
        "phase": 0,
        "message": "Session created. Connect via WebSocket to start assessment."
    }

@app.get("/api/sessions/{session_id}")
async def get_session_status(session_id: str):
    """Get current session status"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = session_manager.get_messages(session_id)
    hypotheses = session_manager.get_hypotheses(session_id)
    
    return {
        "session_id": session_id,
        "phase": session[3],
        "status": session[4],
        "safety_cleared": session[5],
        "message_count": len(messages),
        "hypothesis_count": len(hypotheses),
        "created_at": session[1],
        "updated_at": session[2]
    }

@app.get("/api/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """Get full conversation history"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = session_manager.get_messages(session_id)
    return {
        "session_id": session_id,
        "messages": messages
    }

@app.get("/api/sessions/{session_id}/profile")
async def get_final_profile(session_id: str):
    """Get final structural profile (if completed)"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session[3] < 6:
        return {
            "status": "incomplete",
            "current_phase": session[3],
            "message": "Assessment not yet complete"
        }
    
    profile = json.loads(session[6]) if session[6] else None
    confidence = json.loads(session[7]) if session[7] else None
    
    return {
        "status": "complete",
        "profile": profile,
        "confidence_scores": confidence
    }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket for real-time assessment flow"""
    await websocket.accept()
    active_connections[session_id] = websocket
    
    try:
        # Verify session exists
        session = session_manager.get_session(session_id)
        if not session:
            await websocket.send_json({
                "type": "error",
                "message": "Session not found"
            })
            await websocket.close()
            return
        
        current_phase = session[3]
        
        # Send initial state
        await websocket.send_json({
            "type": "state",
            "phase": current_phase,
            "message": "Connected to MBP assessment"
        })
        
        # Start with Phase 0 (Safety) if new session
        if current_phase == 0:
            await handle_phase_0(websocket, session_id)
        
        # Main message loop
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            content = data.get("content", "")
            
            if message_type == "response":
                # Save user message
                session_manager.save_message(session_id, "user", content, current_phase)
                
                # Process based on current phase
                if current_phase == 0:
                    result = await process_safety_response(session_id, content)
                    if result.get("safety_cleared"):
                        current_phase = 1
                        session_manager.update_phase(session_id, current_phase)
                        await handle_phase_1(websocket, session_id)
                    else:
                        await websocket.send_json({
                            "type": "question",
                            "phase": 0,
                            "content": result.get("next_question", "Can you tell me more?"),
                            "context": "safety_screening"
                        })
                
                elif current_phase == 1:
                    result = await process_phase_1(session_id, content)
                    if result.get("phase_complete"):
                        current_phase = 2
                        session_manager.update_phase(session_id, current_phase)
                        await handle_phase_2(websocket, session_id)
                    else:
                        await websocket.send_json({
                            "type": "question",
                            "phase": 1,
                            "content": result.get("next_question"),
                            "context": result.get("context", "core_questioning")
                        })
                
                elif current_phase == 2:
                    result = await process_phase_2(session_id, content)
                    if result.get("phase_complete"):
                        current_phase = 3
                        session_manager.update_phase(session_id, current_phase)
                        await handle_phase_3(websocket, session_id)
                    else:
                        await websocket.send_json({
                            "type": "question",
                            "phase": 2,
                            "content": result.get("next_question"),
                            "hypothesis": result.get("current_hypothesis"),
                            "context": "adaptive_probing"
                        })
                
                elif current_phase == 3:
                    result = await process_phase_3(session_id, content)
                    if result.get("phase_complete"):
                        current_phase = 4
                        session_manager.update_phase(session_id, current_phase)
                        await handle_phase_4(websocket, session_id)
                    else:
                        await websocket.send_json({
                            "type": "question",
                            "phase": 3,
                            "content": result.get("next_question"),
                            "adaptation_pattern": result.get("pattern_detected"),
                            "context": "adaptation_mining"
                        })
                
                elif current_phase == 4:
                    result = await process_phase_4(session_id, content)
                    if result.get("phase_complete"):
                        current_phase = 5
                        session_manager.update_phase(session_id, current_phase)
                        await handle_phase_5(websocket, session_id)
                    else:
                        await websocket.send_json({
                            "type": "question",
                            "phase": 4,
                            "content": result.get("next_question"),
                            "tension_target": result.get("tension_pair"),
                            "context": "cross_validation"
                        })
                
                elif current_phase == 5:
                    result = await process_phase_5(session_id, content)
                    current_phase = 6
                    session_manager.update_phase(session_id, current_phase)
                    await handle_phase_6(websocket, session_id, result.get("profile"))
                
                elif current_phase == 6:
                    # Debriefing - just acknowledge
                    await websocket.send_json({
                        "type": "message",
                        "phase": 6,
                        "content": "Thank you for completing the assessment. Your profile has been saved.",
                        "context": "debriefing"
                    })
            
            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        del active_connections[session_id]
    except Exception as e:
        print(f"WebSocket error: {e}")
        if session_id in active_connections:
            del active_connections[session_id]

# Phase Handlers
async def handle_phase_0(websocket: WebSocket, session_id: str):
    """Phase 0: Safety Screening"""
    safety_questions = [
        "Selamat datang di MirrorBreak Protocol. Sebelum kita mulai, saya perlu memastikan kamu dalam kondisi yang aman untuk proses ini.",
        "Pertanyaan pertama: Ada nggak hal yang bikin kamu recently feel overwhelmed atau stuck?",
        "Kedua: Kalau ada memory atau topik yang muncul dan bikin kamu uncomfortable, kamu punya coping mechanism yang biasanya work?",
        "Terakhir: Saat ini, ada nggak pikiran untuk harm yourself atau others?"
    ]
    
    await websocket.send_json({
        "type": "phase_start",
        "phase": 0,
        "title": "Safety Screening",
        "description": "Pre-assessment safety check"
    })
    
    await websocket.send_json({
        "type": "question",
        "phase": 0,
        "content": safety_questions[1],  # Start with first actual question
        "context": "safety_screening"
    })

async def process_safety_response(session_id: str, content: str) -> dict:
    """Process Phase 0 safety responses using Analyzer"""
    messages = session_manager.get_messages(session_id, phase=0)
    
    # Analyze for safety indicators
    analysis = await analyzer.analyze_safety(content, messages)
    
    # Save analysis as system message
    session_manager.save_message(
        session_id, 
        "system", 
        f"Safety analysis: {analysis}", 
        0,
        {"analysis": analysis}
    )
    
    # Check if all safety questions answered
    user_messages = [m for m in messages if m["role"] == "user"]
    
    if analysis.get("crisis_detected"):
        return {
            "safety_cleared": False,
            "crisis": True,
            "next_question": "Saya mendengar bahwa kamu sedang mengalami kesulitan. Untuk keselamatanmu, saya perlu menghentikan sesi ini. Silakan hubungi layanan krisis: 119 (ext 8) atau 1500567."
        }
    
    if len(user_messages) >= 3:
        # All safety questions answered
        session_manager.save_message(
            session_id,
            "system",
            "Safety screening cleared",
            0,
            {"safety_cleared": True}
        )
        return {"safety_cleared": True}
    
    # Continue with next safety question
    next_questions = [
        "Kedua: Kalau ada memory atau topik yang muncul dan bikin kamu uncomfortable, kamu punya coping mechanism yang biasanya work?",
        "Terakhir: Saat ini, ada nggak pikiran untuk harm yourself atau others?"
    ]
    
    return {
        "safety_cleared": False,
        "next_question": next_questions[len(user_messages) - 1]
    }

async def handle_phase_1(websocket: WebSocket, session_id: str):
    """Phase 1: Core Questioning (Fixed Tension Generators)"""
    await websocket.send_json({
        "type": "phase_start",
        "phase": 1,
        "title": "Core Questions",
        "description": "Understanding your structural anchors"
    })
    
    # Fixed tension generator questions
    core_question = "Kamu bilang decision-making mu sangat logical. Coba ceritain decision terbesar akhir tahun ini — apa yang tubuhmu rasakan 5 detik sebelum bilang 'yes'?"
    
    await websocket.send_json({
        "type": "question",
        "phase": 1,
        "content": "Mari kita mulai dengan beberapa pertanyaan inti. " + core_question,
        "tension_target": "AB × Stress Response",
        "context": "core_questioning"
    })

async def process_phase_1(session_id: str, content: str) -> dict:
    """Process Phase 1 core responses"""
    messages = session_manager.get_messages(session_id, phase=1)
    
    # Analyze with Analyzer agent
    analysis = await analyzer.analyze(content, messages)
    
    # Check if we have enough data to move to Phase 2
    user_messages = [m for m in messages if m["role"] == "user"]
    
    if len(user_messages) >= 3:  # Minimum 3 core questions
        return {
            "phase_complete": True,
            "analysis": analysis
        }
    
    # Generate next core question (fixed pattern rotation)
    next_questions = [
        "Kalau bisa kasih advice ke diri mu 5 tahun lalu, apa yang kamu bilang? ... Terus kenapa advice yang sama nggak kamu apply sekarang?",
        "Di kantor atau situasi professional, kamu tipe yang gimana? ... Bandingkan dengan di rumah sama keluarga?",
        "Kalau disuruh rank: Comfort, Growth, Recognition, Stability — urutannya gimana? ... Terus decision terakhir yang melawan ranking itu kapan?"
    ]
    
    question_index = len(user_messages) % len(next_questions)
    
    return {
        "phase_complete": False,
        "next_question": next_questions[question_index],
        "context": "core_questioning",
        "analysis": analysis
    }

async def handle_phase_2(websocket: WebSocket, session_id: str):
    """Phase 2: Adaptive Probing (Hypothesis-Driven)"""
    # Get accumulated data for hypothesis generation
    all_messages = session_manager.get_messages(session_id)
    
    await websocket.send_json({
        "type": "phase_start",
        "phase": 2,
        "title": "Adaptive Probing",
        "description": "Deepening understanding through hypothesis testing"
    })
    
    # Generate hypotheses
    hypotheses = await hypothesis_maker.generate(all_messages)
    
    # Save hypotheses
    for hyp in hypotheses:
        session_manager.save_hypothesis(
            session_id,
            hyp["field"],
            hyp["hypothesis"],
            hyp["confidence"],
            hyp.get("evidence", [])
        )
    
    # Generate first adaptive question
    question = await question_maker.generate(hypotheses, all_messages)
    
    await websocket.send_json({
        "type": "question",
        "phase": 2,
        "content": question,
        "hypothesis_count": len(hypotheses),
        "context": "adaptive_probing"
    })

async def process_phase_2(session_id: str, content: str) -> dict:
    """Process Phase 2 adaptive responses"""
    messages = session_manager.get_messages(session_id)
    hypotheses = session_manager.get_hypotheses(session_id)
    
    # Refine hypotheses based on new data
    refined = await hypothesis_maker.refine(hypotheses, content, messages)
    
    # Check if we have sufficient confidence to proceed
    avg_confidence = sum(h["confidence"] for h in refined) / len(refined) if refined else 0
    
    if avg_confidence > 0.6 and len([m for m in messages if m["role"] == "user" and m["phase"] == 2]) >= 4:
        return {
            "phase_complete": True,
            "hypotheses": refined
        }
    
    # Generate next adaptive question
    question = await question_maker.generate(refined, messages)
    
    return {
        "phase_complete": False,
        "next_question": question,
        "current_hypothesis": refined[0] if refined else None,
        "context": "adaptive_probing"
    }

async def handle_phase_3(websocket: WebSocket, session_id: str):
    """Phase 3: Adaptation Pattern Mining"""
    await websocket.send_json({
        "type": "phase_start",
        "phase": 3,
        "title": "Adaptation Mining",
        "description": "Exploring how you developed your survival patterns"
    })
    
    # Generate mining question based on strongest hypothesis
    hypotheses = session_manager.get_hypotheses(session_id)
    strongest = max(hypotheses, key=lambda h: h["confidence"]) if hypotheses else None
    
    if strongest and "suppression" in strongest["hypothesis"].lower():
        question = "Kapan pertama kali kamu sadar bahwa kamu harus menahan emosi atau jadi 'orang yang kuat'? Apa yang terjadi waktu itu?"
    else:
        question = "Coba inget kapan pertama kali kamu develop cara kamu handle situasi sulit sekarang. Ada moment 'aha' atau gradual?"
    
    await websocket.send_json({
        "type": "question",
        "phase": 3,
        "content": question,
        "safety_note": "Kita akan focus pada pattern-nya, bukan detail traumanya.",
        "context": "adaptation_mining"
    })

async def process_phase_3(session_id: str, content: str) -> dict:
    """Process Phase 3 mining responses"""
    messages = session_manager.get_messages(session_id)
    
    # Look for adaptation patterns
    patterns = await analyzer.extract_patterns(content, messages)
    
    user_messages = [m for m in messages if m["role"] == "user" and m["phase"] == 3]
    
    if len(user_messages) >= 3:
        return {
            "phase_complete": True,
            "patterns": patterns
        }
    
    # Generate follow-up mining question
    follow_ups = [
        "Hal apa yang paling sering kamu sacrifice untuk maintain cara ini?",
        "Situasi seperti apa yang bikin pattern ini nggak work lagi?",
        "Kalau kamu nggak pakai cara ini, apa yang kamu takutkan bakal terjadi?"
    ]
    
    return {
        "phase_complete": False,
        "next_question": follow_ups[len(user_messages) - 1],
        "pattern_detected": patterns[0] if patterns else None,
        "context": "adaptation_mining"
    }

async def handle_phase_4(websocket: WebSocket, session_id: str):
    """Phase 4: Cross-Validation with 12D Matrix"""
    await websocket.send_json({
        "type": "phase_start",
        "phase": 4,
        "title": "Cross-Validation",
        "description": "Testing consistency across dimensions"
    })
    
    # Select tension pair to test
    question = "Menarik... jadi di situasi professional kamu bilang kamu sangat terbuka, tapi di situasi personal kamu mention lebih tertutup. Itu karena context-nya beda, atau memang ada approach yang berbeda untuk situasi berbeda?"
    
    await websocket.send_json({
        "type": "question",
        "phase": 4,
        "content": question,
        "tension_pair": "VB × Context",
        "technique": "innocent_mirror",
        "context": "cross_validation"
    })

async def process_phase_4(session_id: str, content: str) -> dict:
    """Process Phase 4 cross-validation"""
    messages = session_manager.get_messages(session_id)
    
    # Assess 12D matrix scores
    scores = await assessor.assess_12d(content, messages)
    
    # Save scores
    for dimension, data in scores.items():
        session_manager.save_matrix_score(
            session_id,
            dimension,
            data["score"],
            data["confidence"],
            data.get("evidence", [])
        )
    
    user_messages = [m for m in messages if m["role"] == "user" and m["phase"] == 4]
    
    if len(user_messages) >= 3:
        return {
            "phase_complete": True,
            "scores": scores
        }
    
    # More tension tests
    tension_tests = [
        "Kamu bilang 'itu bukan masalah buatku'. Coba bayangin scenario: besok situation yang sama terjadi lagi, tapi kali ini kamu NGGAK bisa handle dengan cara biasanya. Apa yang bakal muncul?",
        "Kalau orang yang paling kenal kamu ditanya 'apa kelemahan dia?', apa yang mereka akan jawab? ... Terus setuju nggak sama jawaban itu?"
    ]
    
    return {
        "phase_complete": False,
        "next_question": tension_tests[len(user_messages) - 1],
        "tension_pair": "CRF × Defense",
        "context": "cross_validation"
    }

async def handle_phase_5(websocket: WebSocket, session_id: str):
    """Phase 5: Structural Synthesis"""
    await websocket.send_json({
        "type": "phase_start",
        "phase": 5,
        "title": "Synthesis",
        "description": "Generating your structural profile"
    })
    
    # Gather all data
    messages = session_manager.get_messages(session_id)
    hypotheses = session_manager.get_hypotheses(session_id)
    
    # Generate profile
    profile = await synthesizer.synthesize(messages, hypotheses)
    
    await websocket.send_json({
        "type": "synthesis_preview",
        "phase": 5,
        "content": "Saya akan membuat ringkasan struktur yang kita temukan. Apa yang paling resonate dengan kamu dari percakapan ini?",
        "profile_preview": profile.get("core_summary", ""),
        "context": "synthesis"
    })

async def process_phase_5(session_id: str, content: str) -> dict:
    """Process Phase 5 synthesis confirmation"""
    messages = session_manager.get_messages(session_id)
    hypotheses = session_manager.get_hypotheses(session_id)
    
    # Final synthesis with user feedback
    profile = await synthesizer.synthesize(messages, hypotheses, user_feedback=content)
    
    return {
        "phase_complete": True,
        "profile": profile
    }

async def handle_phase_6(websocket: WebSocket, session_id: str, profile: dict):
    """Phase 6: Debriefing"""
    await websocket.send_json({
        "type": "phase_start",
        "phase": 6,
        "title": "Debriefing",
        "description": "Closing and integration"
    })
    
    # Save final profile
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE sessions SET final_profile = ?, confidence_scores = ?, status = 'completed' WHERE id = ?",
        (json.dumps(profile), json.dumps(profile.get("confidence", {})), session_id)
    )
    conn.commit()
    conn.close()
    
    await websocket.send_json({
        "type": "profile_complete",
        "phase": 6,
        "content": f"Terima kasih telah menyelesaikan MirrorBreak Protocol.\\n\\nRingkasan struktur yang kita temukan:\\n{profile.get('core_summary', '')}\\n\\nIni bukan diagnosis atau label, tapi pemetaan pola adaptasi. Jika ada yang feel off atau kamu ingin explore lebih dalam, konsultasikan dengan professional.",
        "profile": profile,
        "next_steps": [
            "Review your profile anytime at /profile",
            "Journaling tentang pola yang kita temukan",
            "Konsultasi dengan therapist jika ada distress"
        ],
        "context": "debriefing"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
