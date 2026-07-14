import pytest
from utils.telemetry import redact_pii
from utils.syllabus import query_syllabus
from agent_definition import orchestrate_agents

# Benchmarks for Intent Classification Regression Testing
CLASSIFICATION_BENCHMARKS = [
    # (user_message, expected_is_quiz)
    ("I want to take a quiz, please", True),
    ("Give me some questions on module 1", True),
    ("Test my knowledge of Model Armor", True),
    ("Can I do an exam on ADK?", True),
    ("Let's do a test me on s2_m3", True),
    ("What is s1_m1?", False),
    ("Explain the Hill Climbing algorithm", False),
    ("Tell me about s2_m1, Model Armor", False),
    ("How do I govern access in s2_m3?", False),
    ("Hello, how are you doing today?", False),
]

# Benchmarks for Factual Grounding Evaluation
FACTUAL_BENCHMARKS = [
    # (query, substring_expected)
    ("s1_m1", "Accelerate Development with Antigravity"),
    ("s1_m2", "Deploy Agents with ADK"),
    ("s1_m3", "Evaluate and Improve Agents"),
    ("s2_m1", "Protect Gemini Workspace Data Grounding with Model Armor"),
    ("s2_m2", "Add Agents to Gemini Enterprise"),
    ("s2_m3", "Govern Agent Access with Gemini Enterprise Agent Platform"),
    ("Antigravity CLI", "agy"),
    ("Hill Climbing", "optimization algorithm"),
    ("Model Armor", "safety filter configurations"),
]

# Benchmarks for Struggle Capturing Evaluation
STRUGGLE_BENCHMARKS = [
    # (user_message, expected_struggle_topic)
    ("I am failing to set up my antigravity environment", "Antigravity CLI (agy)"),
    ("I don't understand the skill.yaml formatting rules", "Declarative skill configs"),
    ("How do I write ADK class definitions?", "ADK Python Class definitions"),
    ("What are ADK tool registration details?", "ADK Tool registration"),
    ("I am stuck on the hill climbing optimization model", "Hill Climbing prompt optimization"),
    ("Our team needs better evaluation rubrics & validation methods", "Grading rubrics & validation"),
    ("The model armor config keeps rejecting normal inputs", "Model Armor config"),
    ("We need workspace data grounding for our workspace", "Workspace data grounding"),
    ("How do I configure RBAC and access governance policies?", "Access governance & service accounts"),
]


def test_pii_redaction_evaluation():
    """
    Evaluation Test: Verifies that sensitive user information (PII) is redacted correctly
    to guarantee data security and compliance.
    """
    test_cases = [
        ("My email is student123@google.com", "My email is [REDACTED_EMAIL]"),
        ("Call me at +1 555-019-2834, thanks", "Call me at +[REDACTED_PHONE], thanks"),
        ("My SSN is 000-12-3456", "My SSN is [REDACTED_SSN]"),
        ("Charge to card 1234-5678-9012-3456", "Charge to card [REDACTED_CREDIT_CARD]"),
    ]
    for inp, expected in test_cases:
        assert redact_pii(inp) == expected


def test_intent_classification_regression():
    """
    Evaluation Test: Verifies that the intent classification routing engine remains robust and correct.
    This acts as a regression safety suite for the local intelligent route handler.
    """
    for user_message, expects_quiz in CLASSIFICATION_BENCHMARKS:
        res = orchestrate_agents(user_message)
        # If expects_quiz is True, response should contain the Quiz Agent question,
        # otherwise it should provide general guidance or the Teaching Agent lesson.
        is_quiz_delivered = "Quiz Agent Question" in res["response"]
        assert is_quiz_delivered == expects_quiz, (
            f"Classification mismatch for: '{user_message}'. "
            f"Expected is_quiz={expects_quiz}, got is_quiz={is_quiz_delivered}"
        )


def test_factual_grounding_evaluation():
    """
    Evaluation Test: Verifies that the factual grounding knowledge base (syllabus tools)
    returns highly accurate and relevant content for curriculum inquiries.
    """
    for query, expected_sub in FACTUAL_BENCHMARKS:
        response = query_syllabus(query)
        assert expected_sub.lower() in response.lower(), (
            f"Factual grounding error for: '{query}'. "
            f"Expected substring '{expected_sub}' was not found in response: '{response}'"
        )


def test_struggle_capturing_evaluation(db_mgr):
    """
    Evaluation Test: Verifies that the Coaching Agent correctly scans user inputs,
    identifies cognitive gaps, and automatically persists them in the study database.
    """
    for message, expected_topic in STRUGGLE_BENCHMARKS:
        # Clear database struggles first
        state = db_mgr.get_state()
        state["active_struggles"] = []
        db_mgr.save_state(state)

        # Run orchestration
        res = orchestrate_agents(message)
        
        # Verify struggle was captured
        active_struggles = [s["topic"] for s in res["state"]["active_struggles"] if s["status"] == "active"]
        assert expected_topic in active_struggles, (
            f"Struggle not captured for input: '{message}'. "
            f"Expected topic '{expected_topic}' not in active struggles {active_struggles}"
        )


def test_adk_evalset_and_judge_config():
    """
    Evaluation Test: Verifies that the ADK EvalSet and LLM-as-Judge criteria configuration
    files exist, conform to the official ADK Pydantic schemas, and are ready for CI/CD execution.
    """
    import os
    import json
    import pytest
    from google.adk.evaluation.eval_set import EvalSet

    # Define paths
    evalset_path = "tests/evaluation/l200_study.evalset.json"
    config_path = "tests/evaluation/test_config.json"

    # Assert files exist
    assert os.path.exists(evalset_path), f"EvalSet file {evalset_path} does not exist."
    assert os.path.exists(config_path), f"Test configuration file {config_path} does not exist."

    # Validate EvalSet structure using ADK Pydantic validation
    with open(evalset_path, "r") as f:
        evalset_data = json.load(f)
    try:
        evalset = EvalSet.model_validate(evalset_data)
    except Exception as e:
        pytest.fail(f"EvalSet failed Pydantic schema validation: {e}")

    assert evalset.eval_set_id == "l200_study_hub_evalset"
    assert len(evalset.eval_cases) >= 2

    # Validate test_config criteria structure
    with open(config_path, "r") as f:
        config_data = json.load(f)

    assert "criteria" in config_data, "test_config.json must define 'criteria'."
    criteria = config_data["criteria"]
    assert "tool_trajectory_avg_score" in criteria, "Missing 'tool_trajectory_avg_score' metric."
    assert "final_response_match_v2" in criteria, "Missing LLM-as-Judge 'final_response_match_v2' metric."
    assert "rubric_based_final_response_quality_v1" in criteria, "Missing LLM-as-Judge 'rubric_based_final_response_quality_v1' rubric metric."
