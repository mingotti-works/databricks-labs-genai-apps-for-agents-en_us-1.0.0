from agents import Agent, Runner, set_default_openai_api, set_default_openai_client
from databricks_openai import AsyncDatabricksOpenAI
import os

# Read the endpoint name injected by Databricks Apps
SERVING_ENDPOINT_NAME = os.getenv("SERVING_ENDPOINT_NAME")
