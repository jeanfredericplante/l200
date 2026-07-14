from google.adk import Agent

coaching_agent = Agent(
    name="CoachingAgent",
    model="gemini-2.5-pro",
    tools=[],
    instruction="You are the L200 Coaching Agent. Your job is to analyze conversations, identify student doubts or struggles, and suggest adjustments. You help them overcome cognitive gaps."
)
