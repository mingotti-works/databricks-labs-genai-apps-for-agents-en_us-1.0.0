This three-part series covers how to build, deploy, observe, and extend AI agents using Databricks Apps and Databricks Asset Bundles (DABs), reflecting Databricks' recommended shift away from model serving endpoints toward app-based deployment. In this pattern, the app itself is the deployment artifact, with MLflow and Unity Catalog acting as the governance and observability layers rather than the deployment target. The first notebook establishes the foundation: building a simple agent with the OpenAI Agents SDK, hosting it with FastAPI, and deploying it end-to-end via a DAB. The second notebook extends that foundation by integrating MLflow tracing and experiment tracking, so every agent interaction produces structured traces and logged runs visible in the MLflow UI. The third notebook completes the series by connecting the MLflow-traced agent to a Databricks Managed MCP server backed by a Unity Catalog function, enabling the agent to answer questions that require real data lookups — with every tool call captured as a child span in the MLflow Traces UI. Together, the three demos produce a fully deployed, observable, tool-calling agent and establish the mental model for how app-based deployment, Unity Catalog governance, and MLflow observability work together.

Learning Objectives
Explain the difference between deploying agents as Databricks Apps versus model serving endpoints, and articulate why Databricks recommends app-based deployment for agent lifecycles
Describe the "orthogonal deployment" model, in which the app handles execution, Unity Catalog handles governance, and MLflow handles observability
Build a simple agent using the OpenAI Agents SDK configured for a Databricks environment
Wrap an agent in a FastAPI web server to expose it as a deployable web application
Configure a databricks.yml file to define a Databricks Asset Bundle for application deployment, including resource grants for MLflow experiments
Deploy and redeploy an agent as a Databricks App using DABs
Integrate MLflow tracing into an agent using @mlflow.trace and mlflow.start_run
Configure MLflow experiment tracking via environment variables injected through a Databricks Asset Bundle
Verify that agent traces and logged runs appear correctly in the MLflow UI after deployment
Explain the Model Context Protocol (MCP) — its architecture, primitives, and lifecycle
Describe the three MCP server types on Databricks — Managed, External, and Custom
Add MCP imports and an McpServer instance to an existing agent.py file
Wrap Runner.run() in an async MCP context manager so tools are available at call time
Update app.yaml and databricks.yml to expose new environment variables and grant the UC function permission
Redeploy the updated agent and verify tool call spans appear in the MLflow Traces UI
Requirements & Prerequisites
Before starting this lab, ensure you have:

A Databricks workspace
Intermediate knowledge of Python
Knowledge of Databricks Apps and Databricks Asset Bundles are a plus
Knowledge of building apps is useful but not required
Contents
This repository includes:

1 - Demo - Introduction to Deploying Agents on Databricks Apps notebook
2 - Demo - Integrating App-Based Agents with MLflow
3 - Demo - Integrating Databricks MCP with an App-Based Agent
Images and supporting materials
Getting Started
Open the notebook 1 - Demo - Introduction to Deploying Agents on Databricks Apps.
Follow the instructions step by step.
