import os
import json
import logging
import copy
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
    "quiz_history": []
}

class DBManager:
    def __init__(self):
        self._firestore_client_cache = None

    @property
    def firestore_db(self):
        """Lazy-loads the Firestore client, preventing pickling issues during deployment."""
        if not hasattr(self, "_firestore_client_cache") or self._firestore_client_cache is None:
            try:
                from google.cloud import firestore
                self._firestore_client_cache = firestore.Client()
                logger.info("🔥 Firestore client successfully initialized (lazy).")
            except Exception as e:
                logger.warning(f"⚠️ Firestore init skipped (falling back to local storage): {str(e)}")
                self._firestore_client_cache = None
        return self._firestore_client_cache

    def __getstate__(self):
        """Custom serialization to ensure firestore.Client is excluded from pickles."""
        state = self.__dict__.copy()
        # Do not pickle the active firestore socket/client cache
        state["_firestore_client_cache"] = None
        return state

    def __setstate__(self, state):
        """Custom deserialization to restore DBManager state."""
        self.__dict__.update(state)


    def get_state(self, user_id=DEFAULT_USER_ID) -> dict:
        """Retrieves user state from Firestore or local JSON."""
        if self.firestore_db:
            try:
                doc_ref = self.firestore_db.collection(FIRESTORE_COLLECTION).document(user_id)
                doc = doc_ref.get()
                if doc.exists:
                     return doc.to_dict()
                else:
                    # Write default state to Firestore
                    default_copy = copy.deepcopy(DEFAULT_STATE)
                    doc_ref.set(default_copy)
                    return default_copy
            except Exception as e:
                logger.error(f"Error reading from Firestore: {e}. Falling back to local file.")
        
        # Local JSON Fallback
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading local state file: {e}. Returning default state.")
        
        # If no file exists, save and return default state
        default_copy = copy.deepcopy(DEFAULT_STATE)
        self.save_state(default_copy, user_id)
        return default_copy

    def save_state(self, state: dict, user_id=DEFAULT_USER_ID):
        """Persists the user state to Firestore or local JSON."""
        # Calculate overall progress and hours dynamically before saving
        self._recalculate_progress(state)

        if self.firestore_db:
            try:
                self.firestore_db.collection(FIRESTORE_COLLECTION).document(user_id).set(state)
                logger.info("Successfully saved state to Firestore.")
                return
            except Exception as e:
                logger.error(f"Error saving to Firestore: {e}. Writing to local file instead.")
        
        # Local JSON Fallback
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(state, f, indent=2)
            logger.info("Successfully saved state to local JSON file.")
        except Exception as e:
            logger.error(f"Fatal error writing to local state file: {e}")

    def log_struggle(self, topic: str, severity: str = "medium", user_id=DEFAULT_USER_ID):
        """Adds a newly detected study struggle to the student state logs."""
        state = self.get_state(user_id)
        
        # Check if this topic is already active to prevent duplicates
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
        self.save_state(state, user_id)
        return state

    def resolve_struggle(self, topic: str, user_id=DEFAULT_USER_ID):
        """Marks an active struggle as resolved once mastery is demonstrated (e.g. quiz passed)."""
        state = self.get_state(user_id)
        updated = False
        for struggle in state["active_struggles"]:
            if struggle["topic"].lower() == topic.lower() and struggle["status"] == "active":
                struggle["status"] = "resolved"
                struggle["resolved_at"] = datetime.now().isoformat()
                updated = True
        
        if updated:
            self.save_state(state, user_id)
        return state

    def add_quiz_result(self, module_id: str, score_percent: float, user_id=DEFAULT_USER_ID):
        """Logs quiz execution details and triggers auto-module completion if score >= 80%."""
        state = self.get_state(user_id)
        
        quiz_record = {
            "module_id": module_id,
            "score_percent": score_percent,
            "date": datetime.now().isoformat()
        }
        state["quiz_history"].append(quiz_record)

        # Auto-complete module and allocate completed hours if score is passing (80%)
        if score_percent >= 80.0:
            if module_id in state["modules"]:
                module = state["modules"][module_id]
                module["completed"] = True
                module["hours_completed"] = module["hours_total"]
                
                # Resolve active struggles associated with this module
                self._resolve_struggles_for_module(state, module_id)

        self.save_state(state, user_id)
        return state

    def update_module_status(self, module_id: str, completed: bool, user_id=DEFAULT_USER_ID):
        """Explicitly toggles a module's study completion checkpoints."""
        state = self.get_state(user_id)
        if module_id in state["modules"]:
            module = state["modules"][module_id]
            module["completed"] = completed
            module["hours_completed"] = module["hours_total"] if completed else 0.0
            self.save_state(state, user_id)
        return state

    def _resolve_struggles_for_module(self, state: dict, module_id: str):
        """Inner helper mapping module focus to struggle tags for automatic resolution."""
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
        """Recalculates completed hours and final progress percent dynamically."""
        total_hours = state["hours_total"]
        completed_hours = 0.0
        
        for module in state["modules"].values():
            completed_hours += module["hours_completed"]
            
        state["hours_completed"] = round(completed_hours, 2)
        state["overall_progress_percent"] = round((completed_hours / total_hours) * 100.0, 1) if total_hours > 0 else 0.0
