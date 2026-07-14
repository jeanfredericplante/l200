import os
import json
import requests
from google.adk import Agent

# Import modular telemetry, logs, and redaction utilities
from utils.telemetry import redact_pii, logger, tracer

# Import modular curriculum syllabus details
from utils.syllabus import L200_SYLLABUS, query_syllabus

# Import modular subagents and local database manager
from agents.coaching import coaching_agent
from agents.teaching import teaching_agent
from agents.quiz import quiz_agent, update_learning_progress, db

# ==========================================
# 👑 Unified Multi-Agent Root Orchestrator
# ==========================================
root_agent = Agent(
    name="L200StudyOrchestrator",
    model="gemini-2.5-flash",
    instruction=(
        "You are the L200 Study Companion Orchestrator, coordinating an enterprise-grade education graph consisting of:\n"
        "- CoachingAgent: Inspects struggles and provides motivational correction.\n"
        "- TeachingAgent: Delivers syllabus overviews, lectures, and resources.\n"
        "- QuizAgent: Coordinates assessments and updates user learning progress.\n\n"
        "Ensure the user gets a supportive and cohesive learning experience."
    ),
    sub_agents=[coaching_agent, teaching_agent, quiz_agent]
)

# ==========================================
# 💻 Direct Gemini API Communication Helper
# ==========================================
def _query_gemini_api(prompt: str, api_key: str) -> str:
    """Queries Gemini model directly using REST API for local/hybrid development."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise RuntimeError("Unexpected response structure from Gemini API.")
    else:
        raise RuntimeError(f"Gemini API request failed with status {response.status_code}: {response.text}")

# ==========================================
# 🌊 Combined Multi-Agent Orchestration Loop
# ==========================================
def orchestrate_agents(user_message: str, user_id="default_student", api_key="") -> dict:
    """
    Coordinates Coaching, Teaching, and Quiz subagents.
    Analyzes inputs for struggle keywords to log implicit memories.
    Uses Direct Gemini API if a key is provided; falls back to an intelligent local engine.
    """
    # Redact PII from user inputs to protect user privacy
    clean_message = redact_pii(user_message)
    user_prompt_lower = clean_message.lower()

    # Determine user intent using a dynamic, high-fidelity LLM-based classifier when an API Key is available
    intent = "chat_and_orchestrate"
    is_quiz_request = False
    
    if api_key:
        try:
            logger.info("Classifying student intent dynamically using Gemini LLM...")
            classification_prompt = (
                "You are an expert user-intent classifier for an L200 Study Companion platform.\n"
                "Classify the following student query into exactly one of these categories:\n"
                "- 'request_quiz': If the user wants to take a test, quiz, exam, or practice questions.\n"
                "- 'query_lesson': If the user is asking about a specific syllabus module, topic, or lesson (e.g., s1_m1, Model Armor, ADK).\n"
                "- 'chat_and_orchestrate': For general greetings, motivation, and general study support.\n\n"
                f"Student Query: '{clean_message}'\n\n"
                "Return ONLY the exact category name as a single string, with no additional text or formatting."
            )
            llm_category = _query_gemini_api(classification_prompt, api_key).strip().lower()
            if "request_quiz" in llm_category:
                intent = "request_quiz"
                is_quiz_request = True
            elif "query_lesson" in llm_category:
                intent = "query_lesson"
            else:
                intent = "chat_and_orchestrate"
        except Exception as e:
            logger.warning(f"Fallback to regex classification due to LLM classifier error: {str(e)}")
            is_quiz_request = any(word in user_prompt_lower for word in ["quiz", "test me", "exam", "question", "test"])
            if is_quiz_request:
                intent = "request_quiz"
            elif any(m_id in user_prompt_lower for m_id in L200_SYLLABUS.keys()):
                intent = "query_lesson"
    else:
        # Brittle regex-matching is used only as a local, API-key-free fallback for off-grid prototyping
        is_quiz_request = any(word in user_prompt_lower for word in ["quiz", "test me", "exam", "question", "test"])
        if is_quiz_request:
            intent = "request_quiz"
        elif any(m_id in user_prompt_lower for m_id in L200_SYLLABUS.keys()):
            intent = "query_lesson"

    span = None
    if tracer:
        span = tracer.start_span("orchestrate_agents")
        if span.is_recording():
            span.set_attribute("gen_ai.user_id", redact_pii(user_id))
            span.set_attribute("gen_ai.intent", intent)

    outcome = "unknown_outcome"
    try:
        state = db.get_state(user_id)
        
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

        # 2. Handle live Gemini API or local intelligent routing
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
            
            full_prompt = f"{system_prompt}\n\nStudent Message: {clean_message}\n\nAgent responses:"
            response_text = _query_gemini_api(full_prompt, api_key)
            outcome = "gemini_agent_response"
            
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
                outcome = "local_quiz_question_delivered"
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
                        outcome = f"local_syllabus_lesson_delivered:{m_id}"
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
                    outcome = "local_general_guidance_delivered"

        # Record success telemetry on the active trace span
        if span and span.is_recording():
            span.set_attribute("gen_ai.outcome", outcome)
            from opentelemetry.trace import StatusCode
            span.set_status(StatusCode.OK)

        # Emit High-Fidelity Intent-vs-Outcome Structured JSON Log
        logger.info(
            f"Successfully processed student session. User: {user_id}. Outcome: {outcome}.",
            extra={"intent": intent, "outcome": outcome, "user_id": user_id}
        )

        return {
            "response": response_text,
            "state": state,
            "detected_gaps": detected_gaps
        }

    except Exception as e:
        # Record error telemetry on the active trace span
        outcome = f"failed_with_exception: {str(e)}"
        if span and span.is_recording():
            span.record_exception(e)
            from opentelemetry.trace import StatusCode
            span.set_status(StatusCode.ERROR, str(e))

        logger.error(
            f"Failed to orchestrate agents due to exception.",
            exc_info=True,
            extra={"intent": intent, "outcome": outcome, "user_id": user_id}
        )
        raise e

    finally:
        if span:
            span.end()

def matched_keywords(module_id: str) -> list:
    kw_map = {
        "s1_m1": ["antigravity", "agy", "accelerate", "build", "m1", "module 1", "module1"],
        "s1_m2": ["adk", "python", "deploy", "agent development kit", "m2", "module 2", "module2"],
        "s1_m3": ["hill climbing", "evaluate", "improve", "tuning", "m3", "module 3", "module3"],
        "s2_m1": ["model armor", "workspace data", "grounding", "safety", "m4", "module 4", "module4"],
        "s2_m2": ["add agents", "workspace", "gmail", "docs", "m5", "module 5", "module5"],
        "s2_m3": ["govern", "rbac", "security", "access", "m6", "module 6", "module6"]
    }
    return kw_map.get(module_id, [])
