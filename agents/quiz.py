from google.adk import Agent
from pydantic import BaseModel, Field, ValidationError
from utils.syllabus import L200_SYLLABUS
from db_manager import DBManager

db = DBManager()

class UpdateLearningProgressSchema(BaseModel):
    """Schema for validating update_learning_progress tool input."""
    module_id: str = Field(
        ...,
        description="The formal ID of the L200 curriculum module to update. MUST be one of: 's1_m1', 's1_m2', 's1_m3', 's2_m1', 's2_m2', 's2_m3'."
    )

def update_learning_progress(module_id: str) -> str:
    """Updates user state database, marking a specific L200 module as successfully studied.

    Args:
        module_id: The formal ID of the L200 curriculum module to complete (e.g. 's1_m1').

    Returns:
        A confirmation message of successful state logging or a guided error recovery response.
    """
    try:
        # Validate inputs using Pydantic schema
        validated = UpdateLearningProgressSchema(module_id=module_id)
        mod_id = validated.module_id
    except ValidationError as ve:
        # Structured validation error handling with guided recovery instructions
        error_details = ve.errors()
        return (
            f"❌ Tool Validation Error: The provided input parameter was invalid.\n"
            f"Details: {error_details}\n"
            f"👉 Guided Instructions: Please ensure you provide a valid 'module_id' parameter."
        )

    if mod_id in L200_SYLLABUS:
        db.update_module_status(mod_id, completed=True)
        return f"✅ Progress logged: Module '{L200_SYLLABUS[mod_id]['title']}' marked as COMPLETED! Dashboard metrics updated."

    # Structured guided instructions for invalid module IDs
    valid_ids_str = ", ".join([f"'{k}'" for k in L200_SYLLABUS.keys()])
    return (
        f"⚠️ Error: The module ID '{mod_id}' is invalid.\n"
        f"👉 Guided Instructions: Please specify one of the following official L200 module IDs: "
        f"{valid_ids_str}. For example, call this tool with 's1_m1' to complete Module 1."
    )

from google.adk.tools import FunctionTool

quiz_agent = Agent(
    name="QuizAgent",
    model="gemini-2.5-flash",
    tools=[FunctionTool(update_learning_progress, require_confirmation=True)],
    instruction="You are the L200 Quiz Agent. Your job is to evaluate student answers, deliver challenging multiple-choice questions, and log successful attempts to update learning status."
)
