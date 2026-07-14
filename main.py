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

def fetch_secret_from_manager(secret_id: str, project_id: str = None) -> str:
    """Attempts to programmatically retrieve a secret from Google Secret Manager."""
    try:
        from google.cloud import secretmanager
        import google.auth
        client = secretmanager.SecretManagerServiceClient()
        
        if not project_id:
            try:
                _, project_id = google.auth.default()
            except Exception:
                project_id = os.getenv("GCP_PROJECT", "")
        
        if not project_id:
            return ""
            
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8").strip()
    except Exception as e:
        # Graceful fallback if Secret Manager authentication or secret is not available
        return ""


def get_gemini_api_key(req_key: str = "") -> str:
    """Retrieves the Gemini API key, falling back through client input, environment, and Secret Manager."""
    key = req_key.strip()
    if key:
        return key
    
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key:
        return key
    
    return fetch_secret_from_manager("gemini-api-key")


from fastapi import FastAPI, HTTPException, BackgroundTasks

# API Routes
@app.get("/api/state")
async def get_state_endpoint():
    """Fetches current student learning metrics, active struggles, and quiz histories asynchronously."""
    try:
        return await db.get_state_async()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/state/update_module")
async def update_module_endpoint(req: ModuleUpdateRequest):
    """Manually toggles completion of a specific L200 module from the Learning Map asynchronously."""
    if req.module_id not in L200_SYLLABUS:
         raise HTTPException(status_code=400, detail="Invalid module ID.")
    try:
        updated_state = await db.update_module_status_async(req.module_id, req.completed)
        return updated_state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest, background_tasks: BackgroundTasks):
    """Processes user prompts through the multi-agent Orchestrator asynchronously, logging struggles implicitly."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Prompt is empty.")
    
    # Securely retrieve API Key programmatically with fallback to Secret Manager
    api_key = get_gemini_api_key(req.api_key)
    
    try:
        from agent_definition import orchestrate_agents_async
        result = await orchestrate_agents_async(req.message, api_key=api_key)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in multi-agent routing: {str(e)}")

@app.post("/api/quiz/submit")
async def submit_quiz_endpoint(req: QuizSubmitRequest):
    """Validates student answer against syllabus, logs progress automatically on pass, and returns results asynchronously."""
    if req.module_id not in L200_SYLLABUS:
        raise HTTPException(status_code=400, detail="Invalid module ID.")
    
    q_info = L200_SYLLABUS[req.module_id]["quiz_question"]
    correct = req.answer.strip().upper() == q_info["correct_answer"]
    
    try:
        score = 100.0 if correct else 0.0
        updated_state = await db.add_quiz_result_async(req.module_id, score)
        
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
