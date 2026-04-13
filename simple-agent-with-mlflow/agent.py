from agents import Agent, Runner, set_default_openai_api, set_default_openai_client
from databricks_openai import AsyncDatabricksOpenAI
import os

# Read the endpoint name injected by Databricks Apps
SERVING_ENDPOINT_NAME = os.getenv("SERVING_ENDPOINT_NAME")

# Point the OpenAI Agents SDK at Databricks instead of OpenAI
set_default_openai_client(AsyncDatabricksOpenAI())
set_default_openai_api("chat_completions")

# Define the agent
agent = Agent(
    name="Simple Chatbot",
    instructions="You are a helpful assistant. Answer the user's questions clearly and concisely.",
    # Use the serving endpoint name (or fall back to the default FM endpoint)
    model=SERVING_ENDPOINT_NAME,
)

async def run_agent(messages: list[dict]) -> str:
    """Run the agent with a list of messages and return the final reply."""
    result = await Runner.run(agent, messages)
    return result.final_output
