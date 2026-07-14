import os
import json
import logging
import copy
import asyncio
from datetime import datetime

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_manager")

# Configuration constants
STATE_FILE = "l200_state.json"
FIRESTORE_COLLECTION = "l200_student_states"
DEFAULT_USER_ID = "default_student"

DEFAULT_STATE = {
    "user_id": DEFAULT_USER_ID,
    "overall_progress_percent": 0.0,
    "hours_completed": 0.0,
    "hours_total": 69.25,
    "modules": {
        "s1_m1": { "name": "Accelerate Development with Antigravity", "completed": False, "hours_completed": 0.0, "hours_total": 8.5 },
        "s1_m2": { "name": "Deploy an Agent with Agent Development Kit (ADK)", "completed": False, "hours_completed": 0.0, "hours_total": 12.25 },
        "s1_m3": { "name": "Deploy Evaluate and Improve Agent Development Kit Agents", "completed": False, "hours_completed": 0.0, "hours_total": 11.5 },
        "s2_m1": { "name": "Deploy Gemini Enterprise with Workspace Data & Model Armor", "completed": False, "hours_completed": 0.0, "hours_total": 23.0 },
        "s2_m2": { "name": "Add Agents to Gemini Enterprise", "completed": False, "hours_completed": 0.0, "hours_total": 6.5 },
        "s2_m3": { "name": "Govern Agent Access with Gemini Enterprise Agent Platform", "completed": False, "hours_completed": 0.0, "hours_total": 7.5 }
    },
    "active_struggles": [],
    "quiz_history": [],
    "chat_history": []  # Context & Memory: Conversational History Tracking
}

class DBManager:
    def __init__(self):
        self._firestore_client_cache = None
        self._firestore_async_client_cache = None

    @property
    def firestore_db(self):
        """Lazy-loads the synchronous Firestore client (legacy)."""
        if not hasattr(self, "_firestore_client_cache") or self._firestore_client_cache is None:
            try:
                from google.cloud import firestore
                self._firestore_client_cache = firestore.Client()
                logger.info("🔥 Firestore Client successfully initialized.")
            except Exception as e:
                logger.warning(f"⚠️ Firestore sync client init skipped: {str(e)}")
                self._firestore_client_cache = None
        return self._firestore_client_cache

    @property
    def firestore_db_async(self):
        """Lazy-loads the asynchronous Firestore client."""
        if not hasattr(self, "_firestore_async_client_cache") or self._firestore_async_client_cache is None:
            try:
                from google.cloud import firestore
                self._firestore_async_client_cache = firestore.AsyncClient()
                logger.info("🔥 Async Firestore Client successfully initialized.")
            except Exception as e:
                logger.warning(f"⚠️ Async Firestore Client skipped: {str(e)}")
                self._firestore_async_client_cache = None
        return self._firestore_async_client_cache

    def __getstate__(self):
        """Custom serialization to exclude clients from pickles."""
        state = self.__dict__.copy()
        state["_firestore_client_cache"] = None
        state["_firestore_async_client_cache"] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def _load_local_state(self) -> dict:
        """Helper to load state from local file."""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    data = json.load(f)
                    if "chat_history" not in data:
                        data["chat_history"] = []
                    return data
            except Exception as e:
                logger.error(f"Error reading local state: {e}")
        return copy.deepcopy(DEFAULT_STATE)

    def _save_local_state(self, state: dict):
        """Helper to save state to local file."""
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving local state: {e}")

    # ==========================================
    # ⚡ Asynchronous Implementation (FastAPI / Runtime)
    # ==========================================
    async def get_state_async(self, user_id=DEFAULT_USER_ID) -> dict:
        """Retrieves user state asynchronously from Firestore or local storage."""
        if self.firestore_db_async:
            try:
                doc_ref = self.firestore_db_async.collection(FIRESTORE_COLLECTION).document(user_id)
                doc = await doc_ref.get()
                if doc.exists:
                     data = doc.to_dict()
                     if "chat_history" not in data:
                         data["chat_history"] = []
                     return data
                else:
                    default_copy = copy.deepcopy(DEFAULT_STATE)
                    await doc_ref.set(default_copy)
                    return default_copy
            except Exception as e:
                logger.error(f"Error reading async from Firestore: {e}. Falling back to local.")
        
        return await asyncio.to_thread(self._load_local_state)

    async def save_state_async(self, state: dict, user_id=DEFAULT_USER_ID):
        """Persists the user state asynchronously."""
        self._recalculate_progress(state)

        if self.firestore_db_async:
            try:
                await self.firestore_db_async.collection(FIRESTORE_COLLECTION).document(user_id).set(state)
                logger.info("Successfully saved state to Firestore (async).")
                return
            except Exception as e:
                logger.error(f"Error saving async to Firestore: {e}. Falling back to local.")
        
        await asyncio.to_thread(self._save_local_state, state)

    async def log_struggle_async(self, topic: str, severity: str = "medium", user_id=DEFAULT_USER_ID) -> dict:
        """Logs a detected learning struggle asynchronously."""
        state = await self.get_state_async(user_id)
        
        # Prevent duplicates
        for struggle in state["active_struggles"]:
            if struggle["topic"].lower() == topic.lower() and struggle["status"] == "active":
                return state
        
        new_struggle = {
            "topic": topic,
            "severity": severity,
            "detected_at": datetime.now().isoformat(),
            "status": "active"
        }
        state["active_struggles"].append(new_struggle)
        await self.save_state_async(state, user_id)
        return state

    async def resolve_struggle_async(self, topic: str, user_id=DEFAULT_USER_ID) -> dict:
        """Marks an active struggle as resolved asynchronously."""
        state = await self.get_state_async(user_id)
        updated = False
        for struggle in state["active_struggles"]:
            if struggle["topic"].lower() == topic.lower() and struggle["status"] == "active":
                struggle["status"] = "resolved"
                struggle["resolved_at"] = datetime.now().isoformat()
                updated = True
        
        if updated:
            await self.save_state_async(state, user_id)
        return state

    async def add_quiz_result_async(self, module_id: str, score_percent: float, user_id=DEFAULT_USER_ID) -> dict:
        """Logs quiz execution details asynchronously, completing modules automatically on pass."""
        state = await self.get_state_async(user_id)
        
        quiz_record = {
            "module_id": module_id,
            "score_percent": score_percent,
            "date": datetime.now().isoformat()
        }
        state["quiz_history"].append(quiz_record)

        if score_percent >= 80.0:
            if module_id in state["modules"]:
                module = state["modules"][module_id]
                module["completed"] = True
                module["hours_completed"] = module["hours_total"]
                self._resolve_struggles_for_module(state, module_id)

        await self.save_state_async(state, user_id)
        return state

    async def update_module_status_async(self, module_id: str, completed: bool, user_id=DEFAULT_USER_ID) -> dict:
        """Explicitly toggles module completion status asynchronously."""
        state = await self.get_state_async(user_id)
        if module_id in state["modules"]:
            module = state["modules"][module_id]
            module["completed"] = completed
            module["hours_completed"] = module["hours_total"] if completed else 0.0
            await self.save_state_async(state, user_id)
        return state

    async def add_chat_message_async(self, role: str, text: str, user_id=DEFAULT_USER_ID) -> dict:
        """Appends a new conversational message and automatically executes context compaction on bloat."""
        state = await self.get_state_async(user_id)
        if "chat_history" not in state or state["chat_history"] is None:
            state["chat_history"] = []
            
        state["chat_history"].append({
            "role": role,
            "text": text,
            "timestamp": datetime.now().isoformat()
        })
        
        # Context Bloat Management: If conversation history exceeds 8, compact older history
        if len(state["chat_history"]) > 8:
            logger.info("⚡ Context Bloat Detected: Triggering automatic conversational history compaction.")
            to_compact = state["chat_history"][:-4]
            recent = state["chat_history"][-4:]
            
            # Extract simple keyword markers to compile a semantic summary
            topics = []
            for msg in to_compact:
                for kw in ["antigravity", "adk", "model armor", "hill climbing", "rbac", "syllabus", "quiz"]:
                    if kw in msg["text"].lower() and kw not in topics:
                        topics.append(kw)
            
            summary_text = f"The student previously inquired and demonstrated interest in: {', '.join(topics) if topics else 'general syllabus lessons'}."
            compacted_summary_msg = {
                "role": "system",
                "text": f"[Compacted History Summary]: {summary_text}",
                "timestamp": datetime.now().isoformat()
            }
            
            state["chat_history"] = [compacted_summary_msg] + recent
            logger.info("🟢 Chat history compaction successfully executed.")

        await self.save_state_async(state, user_id)
        return state

    # ==========================================
    # 🔄 Legacy Synchronous Wrappers (Tests / Backward Compatibility)
    # ==========================================
    def get_state(self, user_id=DEFAULT_USER_ID) -> dict:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # If running in another loop, call the legacy sync Firestore method
            return self._get_state_sync_fallback(user_id)
        return loop.run_until_complete(self.get_state_async(user_id))

    def save_state(self, state: dict, user_id=DEFAULT_USER_ID):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            return self._save_state_sync_fallback(state, user_id)
        return loop.run_until_complete(self.save_state_async(state, user_id))

    def log_struggle(self, topic: str, severity: str = "medium", user_id=DEFAULT_USER_ID):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.log_struggle_async(topic, severity, user_id))

    def resolve_struggle(self, topic: str, user_id=DEFAULT_USER_ID):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.resolve_struggle_async(topic, user_id))

    def add_quiz_result(self, module_id: str, score_percent: float, user_id=DEFAULT_USER_ID):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.add_quiz_result_async(module_id, score_percent, user_id))

    def update_module_status(self, module_id: str, completed: bool, user_id=DEFAULT_USER_ID):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.update_module_status_async(module_id, completed, user_id))

    # ==========================================
    # 🛠️ Fallback Private Helpers
    # ==========================================
    def _get_state_sync_fallback(self, user_id=DEFAULT_USER_ID) -> dict:
        if self.firestore_db:
            try:
                doc = self.firestore_db.collection(FIRESTORE_COLLECTION).document(user_id).get()
                if doc.exists:
                     data = doc.to_dict()
                     if "chat_history" not in data:
                         data["chat_history"] = []
                     return data
            except Exception:
                pass
        return self._load_local_state()

    def _save_state_sync_fallback(self, state: dict, user_id=DEFAULT_USER_ID):
        self._recalculate_progress(state)
        if self.firestore_db:
            try:
                self.firestore_db.collection(FIRESTORE_COLLECTION).document(user_id).set(state)
                return
            except Exception:
                pass
        self._save_local_state(state)

    def _resolve_struggles_for_module(self, state: dict, module_id: str):
        keywords_map = {
            "s1_m1": ["antigravity", "prompt", "cli", "agents build agents"],
            "s1_m2": ["adk", "agent sdk", "tool definition", "fastapi wrapper"],
            "s1_m3": ["hill climbing", "evaluation", "validator", "prompt optimization"],
            "s2_m1": ["model armor", "workspace data", "grounding", "safety filters"],
            "s2_m2": ["drive impact", "enterprise integration", "vertex search"],
            "s2_m3": ["access governance", "rbac", "security", "iam"]
        }
        
        keywords = keywords_map.get(module_id, [])
        for struggle in state["active_struggles"]:
            if struggle["status"] == "active":
                if any(kw in struggle["topic"].lower() for kw in keywords):
                    struggle["status"] = "resolved"
                    struggle["resolved_at"] = datetime.now().isoformat()

    def _recalculate_progress(self, state: dict):
        total_hours = state["hours_total"]
        completed_hours = 0.0
        
        for module in state["modules"].values():
            completed_hours += module["hours_completed"]
            
        state["hours_completed"] = round(completed_hours, 2)
        state["overall_progress_percent"] = round((completed_hours / total_hours) * 100.0, 1) if total_hours > 0 else 0.0
