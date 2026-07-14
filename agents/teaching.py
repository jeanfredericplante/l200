from google.adk import Agent
from google.adk.tools import FunctionTool
from utils.syllabus import query_syllabus

teaching_agent = Agent(
    name="TeachingAgent",
    model="gemini-2.5-pro",
    tools=[FunctionTool(query_syllabus, require_confirmation=False)],
    instruction="You are the L200 Teaching Agent. Your job is to lecture and explain L200 syllabus topics, provide links, and prepare students for testing. Keep answers clear and supportive."
)
