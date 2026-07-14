from pydantic import BaseModel, Field, ValidationError

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
            "Antigravity CLI (agy)",
            "Automated development workflow (AGY)",
            "Agent testing loops",
            "Declarative skill definitions (skill.yaml)"
        ],
        "quiz_question": {
            "question": "What is the primary purpose of Google Antigravity (AGY) in an agentic development lifecycle?",
            "options": [
                "A) Storing VM disk backup snapshots",
                "B) Providing a robust CLI (agy) and agentic workflow loops to build, test, and tune other AI agents",
                "C) Generating client-side CSS stylesheets automatically",
                "D) Running standard Kubernetes cluster horizontal pod autoscaling (HPA)"
            ],
            "correct_answer": "B",
            "explanation": "Antigravity is designed to accelerate agentic development by using a core CLI (agy) and agent-building loops to design and refine other AI workloads."
        }
    },
    "s1_m2": {
        "title": "Deploy Agents with ADK",
        "description": "Formally package and deploy custom enterprise-grade agent runtimes using Google ADK.",
        "skills_path": "https://partner.skills.google/paths/3512",
        "challenge_lab": "https://partner.skills.google/course_templates/1614",
        "topics": [
            "ADK Python Class definitions",
            "Registering ADK Callables/Tools",
            "Container packaging & requirements.txt",
            "GCP Agent Platform deployment commands"
        ],
        "quiz_question": {
            "question": "When defining custom Python functions as tools in the Google Agent Development Kit (ADK), what is the best practice?",
            "options": [
                "A) Avoiding any Python type hints or docstrings",
                "B) Writing complete Sphinx/Google-style parameter docstrings and explicit Pydantic schemas for input validation",
                "C) Hardcoding user database passwords in plain text",
                "D) Loading configuration values directly from local desktop disk files"
            ],
            "correct_answer": "B",
            "explanation": "ADK tools rely heavily on clear parameter type hints, Google/Sphinx style docstrings, and robust Pydantic schemas to validate LLM inputs correctly and handle edge cases."
        }
    },
    "s1_m3": {
        "title": "Evaluate and Improve Agents",
        "description": "Evaluate agent outcomes and iteratively improve performance using optimization algorithms.",
        "skills_path": "https://partner.skills.google/paths/3554",
        "challenge_lab": "https://partner.skills.google/course_templates/1628",
        "topics": [
            "Defining objective evaluation metrics",
            "Hill Climbing optimization algorithm",
            "Prompt tuning and test datasets",
            "Debugging tool and model trace history"
        ],
        "quiz_question": {
            "question": "How does the Hill Climbing optimization algorithm improve an agent's prompt instructions?",
            "options": [
                "A) By randomly deleting half of the code every cycle",
                "B) By evaluating agent outputs against a test dataset and iteratively updating prompt variations to maximize the quality score",
                "C) By increasing the CPU core count on the runner instance",
                "D) By bypassing the LLM completely and using static regex answers"
            ],
            "correct_answer": "B",
            "explanation": "Hill Climbing is an iterative optimization algorithm that evaluates prompt variations against objective scoring metrics to systematically climb toward higher quality scores."
        }
    },
    "s2_m1": {
        "title": "Protect Gemini Workspace Data Grounding with Model Armor",
        "description": "Secure Generative AI queries, filtering content and protecting enterprise boundary layers.",
        "skills_path": "https://partner.skills.google/paths/3580",
        "challenge_lab": "https://partner.skills.google/paths/3580/course_templates/1630",
        "topics": [
            "Model Armor safety filter configurations",
            "Redacting PII and sensitive data",
            "Preventing prompt injection attacks",
            "Enterprise data boundary controls"
        ],
        "quiz_question": {
            "question": "Which security tool serves as the primary inline filter/proxy to inspect and redact sensitive data or prevent prompt injections before they reach the Gemini Model?",
            "options": [
                "A) Cloud DNS",
                "B) Cloud Storage",
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
# 🛠️ Validation Schemas
# ==========================================
class QuerySyllabusSchema(BaseModel):
    """Schema for validating query_syllabus tool input."""
    topic_query: str = Field(
        ...,
        description="The keyword, module ID (e.g., 's1_m1', 's2_m3'), or specific topic to search for in the L200 curriculum."
    )

# ==========================================
# 🛠️ Tools
# ==========================================
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
