import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure local L200 folder is on python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_manager import DBManager
from agent_definition import orchestrate_agents, L200_SYLLABUS

load_dotenv()

app = FastAPI(
    title="Gemini Enterprise L200 Agentic Hub",
    description="Multi-agent study advisor and performance dashboard backend.",
    version="1.0.0"
)

# Enable CORS for local developer setups
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DBManager()

# Request Models
class ChatRequest(BaseModel):
    message: str
    api_key: str = ""

class ModuleUpdateRequest(BaseModel):
    module_id: str
    completed: bool

class QuizSubmitRequest(BaseModel):
    module_id: str
    answer: str

# API Routes
@app.get("/api/state")
def get_state_endpoint():
    """Fetches current student learning metrics, active struggles, and quiz histories."""
    try:
        return db.get_state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/state/update_module")
def update_module_endpoint(req: ModuleUpdateRequest):
    """Manually toggles completion of a specific L200 module from the Learning Map."""
    if req.module_id not in L200_SYLLABUS:
        raise HTTPException(status_code=400, detail="Invalid module ID.")
    try:
        updated_state = db.update_module_status(req.module_id, req.completed)
        return updated_state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    """Processes user prompts through the multi-agent Orchestrator, logging struggles implicitly."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Prompt is empty.")
    
    # Securely feed api_key from client or fallback to system environment
    api_key = req.api_key.strip() or os.getenv("GEMINI_API_KEY", "")
    
    try:
        result = orchestrate_agents(req.message, api_key=api_key)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in multi-agent routing: {str(e)}")

@app.post("/api/quiz/submit")
def submit_quiz_endpoint(req: QuizSubmitRequest):
    """Validates student answer against syllabus, logs progress automatically on pass, and returns results."""
    if req.module_id not in L200_SYLLABUS:
        raise HTTPException(status_code=400, detail="Invalid module ID.")
    
    q_info = L200_SYLLABUS[req.module_id]["quiz_question"]
    correct = req.answer.strip().upper() == q_info["correct_answer"]
    
    try:
        score = 100.0 if correct else 0.0
        updated_state = db.add_quiz_result(req.module_id, score)
        
        return {
            "correct": correct,
            "correct_answer": q_info["correct_answer"],
            "explanation": q_info["explanation"],
            "state": updated_state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount Frontend static directory
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Bind to standard Port 8080 or Cloud Run environment PORT variable
    port = int(os.getenv("PORT", 8080))
    print(f"🚀 Launching L200 Agentic Hub Backend on http://localhost:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
