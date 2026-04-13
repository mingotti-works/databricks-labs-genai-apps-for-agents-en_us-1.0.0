from agents import Agent, Runner, set_default_openai_api, set_default_openai_client
from databricks_openai import AsyncDatabricksOpenAI

import json
import mlflow
import os


mlflow.set_tracking_uri("databricks")


# Read the endpoint name injected by Databricks Apps
SERVING_ENDPOINT_NAME = os.getenv("SERVING_ENDPOINT_NAME")


experiment_id = os.getenv("MLFLOW_EXPERIMENT_ID")
experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME")


if experiment_id:
    mlflow.set_experiment(experiment_id=experiment_id)
elif experiment_name:
    mlflow.set_experiment(experiment_name)


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


@mlflow.trace(name="mlflow_chatbot_run", span_type="AGENT", attributes={"agent_name": "MLflow Chatbot"})
async def run_agent(messages: list[dict]) -> str:
    """
    Run the agent with a list of messages and return the final reply.
    - @mlflow.trace creates a trace + root span with inputs/outputs.
    - mlflow.start_run still logs params/artifacts to the experiment.
    """
    with mlflow.start_run(nested=True):
        # Classic run logging (shows up in Runs/Evaluations)
        mlflow.log_param("agent_name", agent.name)
        mlflow.log_param("model_endpoint", agent.model)
        mlflow.log_param("num_messages", len(messages))
        mlflow.log_text(json.dumps(messages, indent=2), "inputs/messages.json")
        # Actual agent call
        result = await Runner.run(agent, messages)
        final_output = result.final_output
        mlflow.log_text(final_output, "outputs/final_output.txt")
        return final_output
