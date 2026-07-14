import os
import requests
import json
import logging
from google.adk import Agent
from .db_manager import DBManager

logger = logging.getLogger("agent_definition")
db = DBManager()

# ==========================================
# 📚 L200 Syllabus Knowledge Base
# ==========================================
L200_SYLLABUS = {
    "s1_m1": {
        "title": "Accelerate Development with Antigravity",
        "description": "Learn to use agentic workflows to build other agents using Google Antigravity.",
        "skills_path": "https://partner.skills.google/paths/3476",
        "challenge_lab": "https://partner.skills.google/course_templates/1568",
        "topics": [
            "Antigravity CLI (agy) commands",
            "Agents-build-agents design paradigms",
            "Declarative skill configurations (skill.yaml)",
            "Workspace manifest definitions"
        ],
        "quiz_question": {
            "question": "When building an agent using Google Antigravity, which file is used to define the agent's core identity, metadata, and available tool permissions?",
            "options": [
                "A) main.py",
                "B) skill.yaml",
                "C) model_armor.json",
                "D) agent_definition.py"
            ],
            "correct_answer": "B",
            "explanation": "In Antigravity (AGY), `skill.yaml` acts as the declarative manifest defining metadata, intents, and capabilities of the custom agent skill."
        }
    },
    "s1_m2": {
        "title": "Deploy an Agent with Agent Development Kit (ADK)",
        "description": "Learn the Python-based Agent Development Kit (ADK) to build, wrap, and deploy custom agent endpoints.",
        "skills_path": "https://partner.skills.google/paths/4144",
        "challenge_lab": "https://partner.skills.google/course_templates/1435",
        "topics": [
            "Google ADK class syntax (Agent, Tool)",
            "FastAPI routing of agent prompts",
            "Registering Custom Python functions as tools",
            "CORS and REST API packaging for Agent Runner"
        ],
        "quiz_question": {
            "question": "In the Google Agent Development Kit (ADK), how do you register a custom Python function to be called by an ADK Agent?",
            "options": [
                "A) Decorate the function with @app.route('/tool')",
                "B) Add the function name to python-dotenv",
                "C) Wrap the function using the Tool constructor: Tool(name='...', func=my_func, description='...')",
                "D) Write the function directly inside index.html"
            ],
            "correct_answer": "C",
            "explanation": "ADK registers python routines as tool-calls by wrapping them in the `google.adk.Tool` wrapper, passing the executable function reference as the `func` argument."
        }
    },
    "s1_m3": {
        "title": "Deploy Evaluate and Improve Agent Development Kit Agents",
        "description": "Evaluate agent outputs and implement prompt tuning loops using Hill Climbing.",
        "skills_path": "https://partner.skills.google/paths/4306",
        "challenge_lab": "https://partner.skills.google/course_templates/1754",
        "topics": [
            "Agent performance evaluations",
            "Defining compliance rubrics & tests",
            "Hill Climbing optimization loops",
            "Prompt tuning and iteration automation"
        ],
        "quiz_question": {
            "question": "What is the primary objective of the 'Hill Climbing' search algorithm in the context of ADK agent evaluation and improvement?",
            "options": [
                "A) To map optimal server routing paths on GCP",
                "B) To secure local API credentials using encryption",
                "C) To iteratively tweak prompt parameters and system instructions to maximize grading rubric compliance",
                "D) To balance traffic between active container replicas"
            ],
            "correct_answer": "C",
            "explanation": "Hill Climbing is a local search algorithm utilized to optimize agent prompts by iteratively making subtle prompt tweaks, scoring them against rubrics, and adopting the highest-scoring instruction candidate."
        }
    },
    "s2_m1": {
        "title": "Deploy Gemini Enterprise with Workspace Data & Model Armor",
        "description": "Ground agents securely on Google Workspace files and implement safety controls using Model Armor.",
        "skills_path": "https://partner.skills.google/paths/3575",
        "challenge_lab": "https://partner.skills.google/paths/3575/course_templates/1665",
        "topics": [
            "Workspace data source grounding (Drive, Docs, Sheets)",
            "Configuring Model Armor safety filters",
            "Mitigating jailbreak prompts",
            "Sanitizing sensitive data leakages (PII filters)"
        ],
        "quiz_question": {
            "question": "Which Google Cloud platform tool is specifically configured to block user jailbreak attempts, filter toxic content, and sanitize agent outputs in a Gemini Enterprise deployment?",
            "options": [
                "A) Cloud Armor",
                "B) Identity-Aware Proxy (IAP)",
                "C) Model Armor",
                "D) Artifact Registry"
            ],
            "correct_answer": "C",
            "explanation": "Model Armor is Google Cloud's safety proxy designed to inspect inputs and outputs of Generative AI systems, applying custom filters for safety, toxic content, and security breaches (jailbreaks)."
        }
    },
    "s2_m2": {
        "title": "Add Agents to Gemini Enterprise",
        "description": "Integrate custom agent workloads directly into Google Workspace enterprise apps.",
        "skills_path": "https://partner.skills.google/paths/3581",
        "challenge_lab": "https://partner.skills.google/paths/3581/course_templates/1632",
        "topics": [
            "Gemini in Gmail/Docs side panels",
            "Enterprise extension integrations",
            "OAuth scopes configuration for Workspace",
            "Synchronizing corporate knowledge catalogs"
        ],
        "quiz_question": {
            "question": "When connecting an ADK agent to a Workspace enterprise deployment for grounding, what is the best practice to protect confidential company files?",
            "options": [
                "A) Copying files into a public Github repository",
                "B) Configuring fine-grained data source credentials and respecting existing enterprise access control list (ACL) rules",
                "C) Disabling all safety filters to maximize token speed",
                "D) Embedding the secret API key in client-side app.js"
            ],
            "correct_answer": "B",
            "explanation": "Workspace grounding requires integrating securely with enterprise Access Control Lists (ACLs) so that agents can only retrieve files the current active user is authorized to read."
        }
    },
    "s2_m3": {
        "title": "Govern Agent Access with Gemini Enterprise Agent Platform",
        "description": "Govern, secure, and scale the corporate agent ecosystem using security best practices.",
        "skills_path": "https://partner.skills.google/paths/3810",
        "challenge_lab": "https://partner.skills.google/course_templates/1749",
        "topics": [
            "Gemini Enterprise Access Governance policies",
            "Role-Based Access Control (RBAC) configurations",
            "Auditing agent API usage and transaction logs",
            "Managing secret API tokens securely in Secret Manager"
        ],
        "quiz_question": {
            "question": "What is the recommended approach for governing custom agent capabilities and authorization scopes across an enterprise organization?",
            "options": [
                "A) Providing the exact same admin credentials to every agent instance",
                "B) Setting up fine-grained Role-Based Access Control (RBAC) mapping specific agents to narrow, verified service accounts",
                "C) Running all workloads outside the enterprise network firewall",
                "D) Storing credentials in plain text comments inside agent_definition.py"
            ],
            "correct_answer": "B",
            "explanation": "Secure governance relies on RBAC (Role-Based Access Control) to assign least-privilege permissions and narrow service accounts to each distinct agent workload on the platform."
        }
    }
}

# ==========================================
# 🛠️ Define ADK Tools (Official ADK Callables)
# ==========================================
from pydantic import BaseModel, Field, ValidationError

class QuerySyllabusSchema(BaseModel):
    """Schema for validating query_syllabus tool input."""
    topic_query: str = Field(
        ...,
        description="The keyword, module ID (e.g., 's1_m1', 's2_m3'), or specific topic to search for in the L200 curriculum."
    )

class UpdateLearningProgressSchema(BaseModel):
    """Schema for validating update_learning_progress tool input."""
    module_id: str = Field(
        ...,
        description="The formal ID of the L200 curriculum module to update. MUST be one of: 's1_m1', 's1_m2', 's1_m3', 's2_m1', 's2_m2', 's2_m3'."
    )

def query_syllabus(topic_query: str) -> str:
    """Queries L200 curriculum lessons, critical topics, and learning pathways.

    Args:
        topic_query: The keyword, module ID, or topic to search for. Must be a valid, non-empty string.

    Returns:
        A detailed summary of the matching module, or structured error instructions on mismatch.
    """
    try:
        # Validate inputs using Pydantic schema
        validated = QuerySyllabusSchema(topic_query=topic_query)
        q = validated.topic_query.lower()
    except ValidationError as ve:
        # Structured error handling with guided recovery instructions
        error_details = ve.errors()
        return (
            f"❌ Tool Validation Error: The provided input parameter was invalid.\n"
            f"Details: {error_details}\n"
            f"👉 Guided Instructions: Please ensure you pass a valid, non-empty string as the 'topic_query' parameter."
        )

    for m_id, content in L200_SYLLABUS.items():
        if m_id in q or any(t.lower() in q for t in content["topics"]) or content["title"].lower() in q:
            return (
                f"📖 **Module Found: {content['title']}**\n"
                f"📝 *Description:* {content['description']}\n"
                f"🔗 *Official Learning Path:* {content['skills_path']}\n"
                f"🧪 *Official Challenge Lab:* {content['challenge_lab']}\n"
                f"📌 *Key Topics Covered:* {', '.join(content['topics'])}"
            )

    # Guided instructions on failure to find match
    return (
        "⚠️ Module not found. I couldn't match your query with any L200 syllabus modules.\n"
        "👉 Guided Instructions: To get a match, please search using a general concept or a specific module ID. "
        "Try searching for one of the following exact module IDs:\n"
        "  - 's1_m1' (Accelerate Development with Antigravity)\n"
        "  - 's1_m2' (Deploy Agents with ADK)\n"
        "  - 's1_m3' (Evaluate & Improve Agents / Hill Climbing)\n"
        "  - 's2_m1' (Workspace Grounding & Model Armor)\n"
        "  - 's2_m2' (Add Agents to Gemini Workspace)\n"
        "  - 's2_m3' (Govern Agent Access / Platform Governance)\n"
        "Or enter keywords like 'Antigravity CLI', 'Model Armor', 'Hill Climbing', etc."
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


# ==========================================
# 🤖 Instantiate ADK Study Agents
# ==========================================
teaching_agent = Agent(
    name="TeachingAgent",
    model="gemini-2.5-flash",
    tools=[query_syllabus],
    instruction="You are the L200 Teaching Agent. Your job is to lecture and explain L200 syllabus topics, provide links, and prepare students for testing. Keep answers clear and supportive."
)

coaching_agent = Agent(
    name="CoachingAgent",
    model="gemini-2.5-flash",
    tools=[],
    instruction="You are the L200 Coaching Agent. Your job is to analyze conversations, identify student doubts or struggles, and suggest adjustments. You help them overcome cognitive gaps."
)

quiz_agent = Agent(
    name="QuizAgent",
    model="gemini-2.5-flash",
    tools=[update_learning_progress],
    instruction="You are the L200 Quiz Agent. Your job is to evaluate student answers, deliver challenging multiple-choice questions, and log successful attempts to update learning status."
)

# ==========================================
# 🧠 Direct REST-based Gemini Inferences
# ==========================================
def _query_gemini_api(prompt: str, api_key: str) -> str:
    """Invokes the Gemini API via secure, direct REST request with no SDK dependencies."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 800}
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            res_json = response.json()
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        else:
            logger.error(f"Gemini API Error {response.status_code}: {response.text}")
            return f"Error: Received API code {response.status_code}."
    except Exception as e:
        logger.error(f"Error connecting to Gemini API: {str(e)}")
        return "Error connecting to Gemini platform."

# ==========================================
# 🌊 Combined Multi-Agent Orchestration Loop
# ==========================================
def orchestrate_agents(user_message: str, user_id="default_student", api_key="") -> dict:
    """
    Coordinates Coaching, Teaching, and Quiz subagents.
    Analyzes inputs for struggle keywords to log implicit memories.
    Uses Direct Gemini API if a key is provided; falls back to an intelligent local engine.
    """
    state = db.get_state(user_id)
    user_prompt_lower = user_message.lower()
    
    # 1. 📋 Coaching Agent: Implicit Struggle Analysis
    detected_gaps = []
    struggle_topics_map = {
        "antigravity": ("Antigravity CLI (agy)", "medium"),
        "agy": ("Antigravity CLI (agy)", "medium"),
        "skill.yaml": ("Declarative skill configs", "high"),
        "adk": ("ADK Python Class definitions", "high"),
        "tool": ("ADK Tool registration", "medium"),
        "hill climbing": ("Hill Climbing prompt optimization", "high"),
        "evaluation": ("Grading rubrics & validation", "medium"),
        "model armor": ("Model Armor config", "high"),
        "grounding": ("Workspace data grounding", "high"),
        "rbac": ("Access governance & service accounts", "high"),
        "governance": ("Access governance & service accounts", "high"),
    }
    
    for kw, (struggle_title, severity) in struggle_topics_map.items():
        if kw in user_prompt_lower:
            detected_gaps.append(struggle_title)
            db.log_struggle(struggle_title, severity, user_id)
            
    # Refresh state after logging struggles
    state = db.get_state(user_id)

    # 2. 📝 Quiz Agent: Trigger check
    is_quiz_request = any(word in user_prompt_lower for word in ["quiz", "test me", "exam", "question", "test"])
    
    # 3. Handle live Gemini API or local intelligent routing
    if api_key:
        logger.info("Using Live Gemini API Mode for Agent orchestrator.")
        system_prompt = (
            "You are coordinating an L200 Study Companion multi-agent platform consisting of:\n"
            "- TeachingAgent: Delivers lectures, syllabus overviews, and links.\n"
            "- CoachingAgent: Inspects struggles and provides motivational correction.\n"
            "- QuizAgent: Asks mock questions.\n\n"
            f"Active student struggles: {json.dumps([s['topic'] for s in state['active_struggles'] if s['status']=='active'])}\n"
            f"Progress state: {state['overall_progress_percent']}% complete. Course Syllabus: {json.dumps(L200_SYLLABUS)}\n\n"
            "Represent the subagents transparently in your response. Combine their thoughts like this:\n"
            "📋 **[Coaching Agent Insights]** ...\n"
            "📘 **[Teaching Agent Lecture]** ...\n"
            "If the user wants a test/quiz, generate a custom multiple-choice question tailored to their active struggles or current module, labeled under:\n"
            "📝 **[Quiz Agent Question]** ..."
        )
        
        full_prompt = f"{system_prompt}\n\nStudent Message: {user_message}\n\nAgent responses:"
        response_text = _query_gemini_api(full_prompt, api_key)
        
    else:
        logger.info("Using Local Intelligent Mode (Rule-based routing).")
        if is_quiz_request:
            selected_module = "s1_m1"
            for m_id in L200_SYLLABUS.keys():
                if not state["modules"][m_id]["completed"]:
                    selected_module = m_id
                    break
            
            content = L200_SYLLABUS[selected_module]
            q_info = content["quiz_question"]
            
            response_text = (
                f"📋 **[Coaching Agent]** I noticed you're ready for an assessment on **{content['title']}**! Let's see what you've mastered.\n\n"
                f"📝 **[Quiz Agent Question]**\n"
                f"**Module: {content['title']}**\n\n"
                f"{q_info['question']}\n\n"
                f"{chr(10).join(q_info['options'])}\n\n"
                f"*Reply with your answer (e.g., 'The answer is B') to test your mastery!*"
            )
        else:
            matched_syllabus = False
            for m_id, content in L200_SYLLABUS.items():
                if m_id in user_prompt_lower or any(kw in user_prompt_lower for kw in matched_keywords(m_id)):
                    matched_syllabus = True
                    syllabus_text = query_syllabus(m_id)
                    
                    coaching_encouragement = ""
                    active_gaps = [s["topic"] for s in state["active_struggles"] if s["status"] == "active"]
                    if active_gaps:
                        coaching_encouragement = f"📋 **[Coaching Agent]** I see you have active struggles in: *{', '.join(active_gaps)}*. Don't worry, reviewing this module is the perfect step to build confidence!\n\n"
                    else:
                        coaching_encouragement = "📋 **[Coaching Agent]** You are making phenomenal steady progress! Let's conquer this next milestone.\n\n"
                        
                    response_text = (
                        f"{coaching_encouragement}"
                        f"📘 **[Teaching Agent Lesson]**\n"
                        f"{syllabus_text}\n\n"
                        f"Would you like to take a quick quiz on this topic to test your knowledge and unlock your completion badges? Just type **'Quiz me'**!"
                    )
                    break
            
            if not matched_syllabus:
                response_text = (
                    f"📋 **[Coaching Agent]** Hello! I am scanning your learning logs. You've completed **{state['overall_progress_percent']}%** of the L200 path. "
                    "I am monitoring your conversation to capture study struggles implicitly and update your gaps map.\n\n"
                    "📘 **[Teaching Agent]** Welcome! I can teach you any of the 6 core modules of the L200 path:\n"
                    "1. `s1_m1` - Accelerate Development with Antigravity\n"
                    "2. `s1_m2` - Deploy Agents with ADK\n"
                    "3. `s1_m3` - Evaluate & Improve Agents (Hill Climbing)\n"
                    "4. `s2_m1` - Workspace Grounding & Model Armor\n"
                    "5. `s2_m2` - Gemini Workspace integration\n"
                    "6. `s2_m3` - Platform Access Governance\n\n"
                    "Tell me what topic you want to study (e.g. *'Explain Model Armor'*) or say **'Quiz me'** to test yourself!"
                )

    return {
        "response": response_text,
        "state": state,
        "detected_gaps": detected_gaps
    }

def matched_keywords(module_id: str) -> list:
    kw_map = {
        "s1_m1": ["antigravity", "agy", "accelerate", "build"],
        "s1_m2": ["adk", "python", "deploy", "agent development kit"],
        "s1_m3": ["hill climbing", "evaluate", "improve", "tuning"],
        "s2_m1": ["model armor", "workspace data", "grounding", "safety"],
        "s2_m2": ["add agents", "workspace", "gmail", "docs"],
        "s2_m3": ["govern", "rbac", "security", "access"]
    }
    return kw_map.get(module_id, [])

# Define the Root Orchestrator Agent for Agent Platform / Reasoning Engine deployment
root_agent = Agent(
    name="L200StudyOrchestrator",
    model="gemini-2.5-flash",
    instruction=(
        "You are the L200 Study Companion Orchestrator. "
        "Direct the user's request to one of your specialized subagents:\n"
        "- CoachingAgent: To analyze and address gaps/struggles\n"
        "- TeachingAgent: To lecture, explain L200 modules and provide links\n"
        "- QuizAgent: To run Assessments/Quizzes\n"
        "Ensure the user gets a supportive and cohesive learning experience."
    ),
    sub_agents=[coaching_agent, teaching_agent, quiz_agent]
)

