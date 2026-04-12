# Databricks notebook source
# MAGIC %md
# MAGIC ![DB Academy](./Includes/images/db-academy.png)

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC # Demo - Integrating App-Based Agents with MLflow
# MAGIC
# MAGIC ## Overview
# MAGIC
# MAGIC This demo builds directly on the previous notebook, **Introduction to Deploying Agents on Databricks Apps**. Now that you know how a simple agent can be deployed as a Databricks App, this demo walks through how to integrate MLflow tracing and experiment tracking into that agent. By the end, every conversation your agent handles will produce a structured MLflow trace and a logged run — giving you visibility into inputs, outputs, latency, and execution behavior.
# MAGIC
# MAGIC With app-based deployment, governance is handled at the app level (workspace ACLs, app service principal) and at the Unity Catalog level (what the app is allowed to touch). MLflow sits in between as the observability layer: traces and evaluation data are stored in UC, while the agent itself is deployed alongside the app's code via a DAB.
# MAGIC
# MAGIC ## Learning Objectives
# MAGIC
# MAGIC By the end of this demonstration, you will be able to:
# MAGIC
# MAGIC 1. **Explain orthogonal deployment** and how app-based agents differ from UC-registered model serving deployments
# MAGIC 2. **Integrate MLflow tracing** into an existing agent using `@mlflow.trace` and `mlflow.start_run`
# MAGIC 3. **Configure MLflow experiment tracking** via environment variables injected through a Declarative Automation Bundles
# MAGIC 4. **Update `databricks.yml`** to grant the app access to an MLflow experiment resource
# MAGIC 5. **Redeploy the updated agent** and verify traces appear in the MLflow UI
# MAGIC
# MAGIC <div style="border-left: 4px solid #f44336; background: #ffebee; padding: 16px 20px; border-radius: 4px; margin: 16px 0;">
# MAGIC <div style="display: flex; align-items: flex-start; gap: 12px;">
# MAGIC <div>
# MAGIC <strong style="color: #c62828; font-size: 1.1em;">Prerequisites</strong>
# MAGIC <p style="margin: 8px 0 0 0; color: #333;">Complete <strong>Demo - Introduction to Deploying Agents on Databricks Apps</strong> before proceeding. This demo assumes you have already worked through the previous notebook where you built your <code>simple-agent</code> folder and are familiar with app deployment using Declarative Automation Bundles (DABs).</p>
# MAGIC </div>
# MAGIC </div>
# MAGIC </div>
# MAGIC
# MAGIC <div style="
# MAGIC border-left: 4px solid #F44336;
# MAGIC background: #FFEBEE;
# MAGIC padding: 14px 18px;
# MAGIC border-radius: 4px;
# MAGIC margin: 16px 0;
# MAGIC ">
# MAGIC <strong style="display:block; color:#c62828; margin-bottom:6px; font-size: 1.1em;">GIT FOLDER REQUIREMENT</strong>
# MAGIC <div style="color:#333;">
# MAGIC
# MAGIC The Declarative Automation Bundles (DABs) UI is only available when you are working inside a Git folder in the workspace.
# MAGIC
# MAGIC Before opening the DABs UI, make sure you have:
# MAGIC - Created or cloned a Git folder in the workspace with all associated labs files
# MAGIC - Git is outside the scope of this lab. For more information visit the [Databricks Git folders](https://docs.databricks.com/aws/en/repos/) documentation.
# MAGIC - **If you are working in Vocareum:** Vocareum does not automatically come with a git folder as a part of the workspace creation. Please use the official documentation to set up Git Folders if working in **Vocareum**.
# MAGIC </div>
# MAGIC </div>

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ## A. Required Compute Environment
# MAGIC
# MAGIC <div style="border-left: 4px solid #f44336; background: #ffebee; padding: 16px 20px; border-radius: 4px; margin: 16px 0;">
# MAGIC <div style="display: flex; align-items: flex-start; gap: 12px;">
# MAGIC <div>
# MAGIC <strong style="color: #c62828; font-size: 1.1em;">Select Serverless Compute</strong>
# MAGIC <p style="margin: 8px 0 0 0; color: #333;">Before starting this notebook, select the required compute environment listed below.</p>
# MAGIC <ul style="margin: 12px 0 0 16px; color: #333;">
# MAGIC <li><strong>Serverless Compute, Version 5</strong> — <a href="https://docs.databricks.com/aws/en/compute/serverless/dependencies#-select-an-environment-version" style="color: #1976d2; text-decoration: underline;">How to select an environment version</a></li>
# MAGIC </ul>
# MAGIC <p style="margin: 8px 0 0 0; color: #333;"><strong>NOTE:</strong> This notebook was <strong>developed and tested using Serverless V5</strong>. Other compute options may work but are not guaranteed to behave the same or support all features demonstrated.</p>
# MAGIC </div>
# MAGIC </div>
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC ## B. Classroom Setup

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### B1. Workspace Configuration
# MAGIC
# MAGIC <div style="
# MAGIC   border-left: 4px solid #1976d2;
# MAGIC   background: #e3f2fd;
# MAGIC   padding: 14px 18px;
# MAGIC   border-radius: 4px;
# MAGIC   margin: 16px 0;
# MAGIC ">
# MAGIC   <strong style="display:block; color:#0d47a1; margin-bottom:6px; font-size:1.1em;">
# MAGIC     Option 1 - Databricks Academy Provided Workspace (Vocareum Workspace)
# MAGIC   </strong>
# MAGIC   <details>
# MAGIC   <div style="color:#333;">
# MAGIC
# MAGIC If you are running this notebook in a <strong>Databricks Academy provided Vocareum workspace</strong>, your Unity Catalog catalog is already created for you.
# MAGIC
# MAGIC Your catalog name matches your Vocareum username and looks like: <strong>labuser12345</strong> (series of unique numbers)
# MAGIC   </div>
# MAGIC   </details>
# MAGIC </div>
# MAGIC
# MAGIC
# MAGIC <div style="
# MAGIC   border-left: 4px solid #1976d2;
# MAGIC   background: #e3f2fd;
# MAGIC   padding: 14px 18px;
# MAGIC   border-radius: 4px;
# MAGIC   margin: 16px 0;
# MAGIC ">
# MAGIC   <strong style="display:block; color:#0d47a1; margin-bottom:6px; font-size:1.1em;">
# MAGIC     Option 2 - Other Workspaces or Databricks Free Edition
# MAGIC   </strong>
# MAGIC   <details>
# MAGIC   <div style="color:#333;">
# MAGIC
# MAGIC If you are running this notebook in your own Databricks workspace or Databricks Free Edition, the setup will
# MAGIC <strong>create a Unity Catalog catalog and schema for you</strong>. **Create catalog permission is required.**
# MAGIC
# MAGIC The catalog name is derived from your Databricks username and follows this pattern: <strong>labuser_username</strong>
# MAGIC   </div>
# MAGIC   </details>
# MAGIC </div>
# MAGIC
# MAGIC <div style="
# MAGIC   border-left: 4px solid #f44336;
# MAGIC   background: #ffebee;
# MAGIC   padding: 14px 18px;
# MAGIC   border-radius: 4px;
# MAGIC   margin: 16px 0;
# MAGIC ">
# MAGIC   <strong style="display:block; color:#c62828; margin-bottom:6px; font-size: 1.1em;">Do Not Run in Production Environments</strong>
# MAGIC   <div style="color:#333;">
# MAGIC   <ul>
# MAGIC       <li>Only run this notebook in <strong>development or sandbox workspaces</strong>.</li>
# MAGIC       <li>Do not run this in production environments. The setup script creates a catalog and schemas in your workspace.</li>
# MAGIC   </ul>
# MAGIC   </div>
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC ### B2. Set Up Your Environment
# MAGIC
# MAGIC Run the cell below to configure your UC and workspace assets for this demo. This setup extends the environment created in the previous notebook.

# COMMAND ----------

# MAGIC %run ./Includes/Classroom-Setup-2

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. Orthogonal Deployment
# MAGIC
# MAGIC Before modifying any code, it is important to understand how app-based agent deployment differs from the traditional model serving pattern.

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### C1. App-Based vs. Model Serving Deployment
# MAGIC
# MAGIC Typically, the lifecycle of an agent built with code in Databricks means the agent and any additional artifacts are registered and governed with Unity Catalog. Deployment to a model serving endpoint normally uses a UC‑registered agent model as the deployment artifact.
# MAGIC
# MAGIC With **Databricks Apps**, registering an agent model to UC is _optional_. The agent can be deployed alongside the app’s code, which is deployed via a DAB. Though the app itself is not a UC securable, the data and most resources it touches are governed objects (often UC securables) that you declare as App resources. In the app’s configuration you explicitly add these as **App resources** and implement identity via the app’s dedicated service principal and/or the end user’s identity (user authorization).
# MAGIC
# MAGIC The table below summarizes the two patterns:
# MAGIC
# MAGIC | Concern              | Model Serving Endpoint                                           | Databricks App (DAB)                                                                 |
# MAGIC |----------------------|------------------------------------------------------------------|--------------------------------------------------------------------------------------|
# MAGIC | Agent registration   | UC registration recommended for agents                          | Optional (agent can run from app source only)                                       |
# MAGIC | Deployment artifact  | UC-registered model (logged with MLflow)                        | App source code + config deployed via DAB                                           |
# MAGIC | Governance layer     | UC model permissions **and** serving endpoint ACLs              | App permissions (CAN USE / CAN MANAGE) **and** UC permissions on declared resources |
# MAGIC | Observability        | MLflow traces + inference tables when using Agent Framework     | MLflow traces (if instrumented) stored in UC-backed experiments                     |
# MAGIC | Resource access      | Endpoint ACLs + UC permissions on data/models/functions         | App’s SP / user scopes + UC permissions on App resources                            |
# MAGIC
# MAGIC <div style="border-left: 4px solid #1976d2; background: #e3f2fd; padding: 16px 20px; border-radius: 4px; margin: 16px 0;">
# MAGIC <div style="display: flex; align-items: flex-start; gap: 12px;">
# MAGIC <div>
# MAGIC <strong style="color: #0d47a1; font-size: 1.1em;">Summary</strong>
# MAGIC <p style="margin: 8px 0 0 0; color: #333;">At the app level, we control who can view, run, and manage the agent (app ACLs and the app service principal). At the Unity Catalog level, we control what the agent can touch (tables, functions, indexes, connections, etc.) and where its traces and evaluation data are stored.</p>
# MAGIC </div>
# MAGIC </div>
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC ## D. Integrate MLflow into the Agent
# MAGIC
# MAGIC As a part of the workspace setup, you will find a new folder called `simple-agent-with-mlflow` has been populated for you (think of this as the solution folder to the previous notebook). This is the folder to add MLflow tracing and experiment tracking. There are three files to update: `agent.py`, `databricks.yml`, and `app.yaml`

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### D1. Update Imports and Tracking URI in `agent.py`
# MAGIC
# MAGIC The first change is to add `mlflow` and `json` to the imports at the top of `agent.py`, and to set the MLflow tracking URI so that traces are sent to Databricks.
# MAGIC
# MAGIC Add the following lines to the top of your `agent.py` file, directly below the existing imports:
# MAGIC
# MAGIC <div class="code-block-dark" data-language="python">
# MAGIC import json
# MAGIC import mlflow
# MAGIC
# MAGIC mlflow.set_tracking_uri("databricks")
# MAGIC </div>
# MAGIC
# MAGIC <p><code>import json</code> is needed to serialize the conversation messages to a JSON artifact for each run.</p>
# MAGIC
# MAGIC <p><code>import mlflow</code> brings in the MLflow tracking and tracing APIs.</p>
# MAGIC
# MAGIC <p><code>mlflow.set_tracking_uri("databricks")</code> tells MLflow to log all traces and runs to your Databricks workspace rather than a local directory. This is required for traces to appear in the Databricks MLflow UI.</p>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and paste it into the imports section of your <code>agent.py</code> file.</p>
# MAGIC
# MAGIC <style id="prism-inline-css">
# MAGIC code[class*="language-"],pre[class*="language-"]{color:#ccc;background:0 0;font-family:Consolas,Monaco,'Andale Mono','Ubuntu Mono',monospace;font-size:1em;text-align:left;white-space:pre;word-spacing:normal;word-break:normal;word-wrap:normal;line-height:1.5;tab-size:4;hyphens:none}pre[class*="language-"]{padding:1em;margin:.5em 0;overflow:auto}:not(pre)>code[class*="language-"],pre[class*="language-"]{background:#2d2d2d}:not(pre)>code[class*="language-"]{padding:.1em;border-radius:.3em;white-space:normal}.token.comment,.token.block-comment,.token.prolog,.token.doctype,.token.cdata{color:#999}.token.punctuation{color:#ccc}.token.tag,.token.attr-name,.token.namespace,.token.deleted{color:#e2777a}.token.function-name{color:#6196cc}.token.boolean,.token.number,.token.function{color:#f08d49}.token.property,.token.class-name,.token.constant,.token.symbol{color:#f8c555}.token.selector,.token.important,.token.atrule,.token.keyword,.token.builtin{color:#cc99cd}.token.string,.token.char,.token.attr-value,.token.regex,.token.variable{color:#7ec699}.token.operator,.token.entity,.token.url{color:#67cdcc}.token.important,.token.bold{font-weight:700}.token.italic{font-style:italic}.token.entity{cursor:help}.token.inserted{color:green}
# MAGIC </style>
# MAGIC
# MAGIC <script>
# MAGIC (function(){
# MAGIC function escapeHtml(text) {
# MAGIC     var div = document.createElement('div');
# MAGIC     div.textContent = text;
# MAGIC     return div.innerHTML;
# MAGIC }
# MAGIC var Prism = window.Prism = {
# MAGIC     languages: {},
# MAGIC     highlight: function(text, grammar) {
# MAGIC         return this.tokenize(text, grammar).map(function(token) {
# MAGIC             if (typeof token === 'string') return escapeHtml(token);
# MAGIC             return '<span class="token ' + token.type + '">' + escapeHtml(token.content) + '</span>';
# MAGIC         }).join('');
# MAGIC     },
# MAGIC     tokenize: function(text, grammar) {
# MAGIC         var tokens = [text];
# MAGIC         for (var key in grammar) {
# MAGIC             var pattern = grammar[key];
# MAGIC             for (var i = 0; i < tokens.length; i++) {
# MAGIC                 if (typeof tokens[i] !== 'string') continue;
# MAGIC                 var match, matches = [];
# MAGIC                 pattern.lastIndex = 0;
# MAGIC                 while ((match = pattern.exec(tokens[i])) !== null) {
# MAGIC                     matches.push({index: match.index, length: match[0].length, value: match[0]});
# MAGIC                 }
# MAGIC                 if (!matches.length) continue;
# MAGIC                 var newTokens = [];
# MAGIC                 var lastIndex = 0;
# MAGIC                 matches.forEach(function(m) {
# MAGIC                     if (m.index > lastIndex) newTokens.push(tokens[i].substring(lastIndex, m.index));
# MAGIC                     newTokens.push({type: key, content: m.value});
# MAGIC                     lastIndex = m.index + m.length;
# MAGIC                 });
# MAGIC                 if (lastIndex < tokens[i].length) newTokens.push(tokens[i].substring(lastIndex));
# MAGIC                 tokens.splice.apply(tokens, [i, 1].concat(newTokens));
# MAGIC             }
# MAGIC         }
# MAGIC         return tokens;
# MAGIC     },
# MAGIC     highlightElement: function(element) {
# MAGIC         element.innerHTML = this.highlight(element.textContent, this.languages.python);
# MAGIC     }
# MAGIC };
# MAGIC Prism.languages.python = {
# MAGIC     'comment': /#.*/g,
# MAGIC     'string': /("""[\s\S]*?"""|'''[\s\S]*?'''|"[^"]*"|'[^']*')/g,
# MAGIC     'keyword': /\b(import|from|def|class|return|if|elif|else|for|while|try|except|finally|with|as|pass|break|continue|yield|lambda|async|await|None|True|False)\b/g,
# MAGIC     'function': /\b\w+(?=\()/g,
# MAGIC     'number': /\b\d+\.?\d*\b/g,
# MAGIC     'operator': /[-+*/%=<>!&|^~]+/g,
# MAGIC     'punctuation': /[{}[\];(),.]/g
# MAGIC };
# MAGIC document.querySelectorAll('.code-block-dark').forEach(function(block) {
# MAGIC     if (block.getAttribute('data-processed')) return;
# MAGIC     block.setAttribute('data-processed', 'true');
# MAGIC     var code = block.textContent.trim();
# MAGIC     var id = 'code-dark-' + Math.random().toString(36).substr(2, 9);
# MAGIC     block.innerHTML =
# MAGIC         '<div style="position:relative;margin:16px 0;">' +
# MAGIC             '<button class="copy-btn" style="position:absolute;top:8px;right:8px;padding:4px 12px;font-size:12px;background:#555;color:#fff;border:1px solid #666;border-radius:4px;cursor:pointer;">Copy</button>' +
# MAGIC             '<pre style="background:#2d2d2d;border-radius:8px;padding:16px;padding-top:40px;overflow-x:auto;margin:0;border:1px solid #444;"><code id="' + id + '" class="language-python"></code></pre>' +
# MAGIC         '</div>';
# MAGIC     var codeEl = document.getElementById(id);
# MAGIC     codeEl.textContent = code;
# MAGIC     Prism.highlightElement(codeEl);
# MAGIC     block.querySelector('.copy-btn').onclick = function() {
# MAGIC         var t = document.createElement('textarea');
# MAGIC         t.value = code;
# MAGIC         document.body.appendChild(t);
# MAGIC         t.select();
# MAGIC         document.execCommand('copy');
# MAGIC         document.body.removeChild(t);
# MAGIC         this.textContent = '✓ Copied!';
# MAGIC         var btn = this;
# MAGIC         setTimeout(function(){ btn.textContent='Copy'; },2000);
# MAGIC     };
# MAGIC });
# MAGIC })();
# MAGIC </script>

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### D2. Configure the MLflow Experiment in `agent.py`
# MAGIC
# MAGIC Next, add the experiment configuration block to `agent.py`, directly after the `SERVING_ENDPOINT_NAME` environment variable read. This block reads the experiment ID and name injected by the DAB at deploy time and sets the active MLflow experiment.
# MAGIC
# MAGIC <div class="code-block-dark" data-language="python">
# MAGIC experiment_id = os.getenv("MLFLOW_EXPERIMENT_ID")
# MAGIC experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME")
# MAGIC
# MAGIC if experiment_id:
# MAGIC     mlflow.set_experiment(experiment_id=experiment_id)
# MAGIC elif experiment_name:
# MAGIC     mlflow.set_experiment(experiment_name)
# MAGIC </div>
# MAGIC
# MAGIC <p><code>os.getenv("MLFLOW_EXPERIMENT_ID")</code> and <code>os.getenv("MLFLOW_EXPERIMENT_NAME")</code> read environment variables that will be injected by the DAB configuration you will add in a later step. This keeps the experiment reference out of your source code.</p>
# MAGIC
# MAGIC <p>The conditional block prefers the experiment ID (more stable) but falls back to the experiment name if only the name is available. Calling <code>mlflow.set_experiment(...)</code> ensures all subsequent runs and traces are logged to the correct experiment.</p>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and paste it into <code>agent.py</code> directly after the <code>SERVING_ENDPOINT_NAME</code> line.</p>
# MAGIC
# MAGIC <style id="prism-inline-css">
# MAGIC code[class*="language-"],pre[class*="language-"]{color:#ccc;background:0 0;font-family:Consolas,Monaco,'Andale Mono','Ubuntu Mono',monospace;font-size:1em;text-align:left;white-space:pre;word-spacing:normal;word-break:normal;word-wrap:normal;line-height:1.5;tab-size:4;hyphens:none}pre[class*="language-"]{padding:1em;margin:.5em 0;overflow:auto}:not(pre)>code[class*="language-"],pre[class*="language-"]{background:#2d2d2d}:not(pre)>code[class*="language-"]{padding:.1em;border-radius:.3em;white-space:normal}.token.comment,.token.block-comment,.token.prolog,.token.doctype,.token.cdata{color:#999}.token.punctuation{color:#ccc}.token.tag,.token.attr-name,.token.namespace,.token.deleted{color:#e2777a}.token.function-name{color:#6196cc}.token.boolean,.token.number,.token.function{color:#f08d49}.token.property,.token.class-name,.token.constant,.token.symbol{color:#f8c555}.token.selector,.token.important,.token.atrule,.token.keyword,.token.builtin{color:#cc99cd}.token.string,.token.char,.token.attr-value,.token.regex,.token.variable{color:#7ec699}.token.operator,.token.entity,.token.url{color:#67cdcc}.token.important,.token.bold{font-weight:700}.token.italic{font-style:italic}.token.entity{cursor:help}.token.inserted{color:green}
# MAGIC </style>
# MAGIC
# MAGIC <script>
# MAGIC (function(){
# MAGIC function escapeHtml(text) {
# MAGIC     var div = document.createElement('div');
# MAGIC     div.textContent = text;
# MAGIC     return div.innerHTML;
# MAGIC }
# MAGIC var Prism = window.Prism = {
# MAGIC     languages: {},
# MAGIC     highlight: function(text, grammar) {
# MAGIC         return this.tokenize(text, grammar).map(function(token) {
# MAGIC             if (typeof token === 'string') return escapeHtml(token);
# MAGIC             return '<span class="token ' + token.type + '">' + escapeHtml(token.content) + '</span>';
# MAGIC         }).join('');
# MAGIC     },
# MAGIC     tokenize: function(text, grammar) {
# MAGIC         var tokens = [text];
# MAGIC         for (var key in grammar) {
# MAGIC             var pattern = grammar[key];
# MAGIC             for (var i = 0; i < tokens.length; i++) {
# MAGIC                 if (typeof tokens[i] !== 'string') continue;
# MAGIC                 var match, matches = [];
# MAGIC                 pattern.lastIndex = 0;
# MAGIC                 while ((match = pattern.exec(tokens[i])) !== null) {
# MAGIC                     matches.push({index: match.index, length: match[0].length, value: match[0]});
# MAGIC                 }
# MAGIC                 if (!matches.length) continue;
# MAGIC                 var newTokens = [];
# MAGIC                 var lastIndex = 0;
# MAGIC                 matches.forEach(function(m) {
# MAGIC                     if (m.index > lastIndex) newTokens.push(tokens[i].substring(lastIndex, m.index));
# MAGIC                     newTokens.push({type: key, content: m.value});
# MAGIC                     lastIndex = m.index + m.length;
# MAGIC                 });
# MAGIC                 if (lastIndex < tokens[i].length) newTokens.push(tokens[i].substring(lastIndex));
# MAGIC                 tokens.splice.apply(tokens, [i, 1].concat(newTokens));
# MAGIC             }
# MAGIC         }
# MAGIC         return tokens;
# MAGIC     },
# MAGIC     highlightElement: function(element) {
# MAGIC         element.innerHTML = this.highlight(element.textContent, this.languages.python);
# MAGIC     }
# MAGIC };
# MAGIC Prism.languages.python = {
# MAGIC     'comment': /#.*/g,
# MAGIC     'string': /("""[\s\S]*?"""|'''[\s\S]*?'''|"[^"]*"|'[^']*')/g,
# MAGIC     'keyword': /\b(import|from|def|class|return|if|elif|else|for|while|try|except|finally|with|as|pass|break|continue|yield|lambda|async|await|None|True|False)\b/g,
# MAGIC     'function': /\b\w+(?=\()/g,
# MAGIC     'number': /\b\d+\.?\d*\b/g,
# MAGIC     'operator': /[-+*/%=<>!&|^~]+/g,
# MAGIC     'punctuation': /[{}[\];(),.]/g
# MAGIC };
# MAGIC document.querySelectorAll('.code-block-dark').forEach(function(block) {
# MAGIC     if (block.getAttribute('data-processed')) return;
# MAGIC     block.setAttribute('data-processed', 'true');
# MAGIC     var code = block.textContent.trim();
# MAGIC     var id = 'code-dark-' + Math.random().toString(36).substr(2, 9);
# MAGIC     block.innerHTML =
# MAGIC         '<div style="position:relative;margin:16px 0;">' +
# MAGIC             '<button class="copy-btn" style="position:absolute;top:8px;right:8px;padding:4px 12px;font-size:12px;background:#555;color:#fff;border:1px solid #666;border-radius:4px;cursor:pointer;">Copy</button>' +
# MAGIC             '<pre style="background:#2d2d2d;border-radius:8px;padding:16px;padding-top:40px;overflow-x:auto;margin:0;border:1px solid #444;"><code id="' + id + '" class="language-python"></code></pre>' +
# MAGIC         '</div>';
# MAGIC     var codeEl = document.getElementById(id);
# MAGIC     codeEl.textContent = code;
# MAGIC     Prism.highlightElement(codeEl);
# MAGIC     block.querySelector('.copy-btn').onclick = function() {
# MAGIC         var t = document.createElement('textarea');
# MAGIC         t.value = code;
# MAGIC         document.body.appendChild(t);
# MAGIC         t.select();
# MAGIC         document.execCommand('copy');
# MAGIC         document.body.removeChild(t);
# MAGIC         this.textContent = '✓ Copied!';
# MAGIC         var btn = this;
# MAGIC         setTimeout(function(){ btn.textContent='Copy'; },2000);
# MAGIC     };
# MAGIC });
# MAGIC })();
# MAGIC </script>

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### D3. Replace `run_agent()` with a Traced Version in `agent.py`
# MAGIC
# MAGIC Replace the existing `run_agent()` function in `agent.py` with the version below. This updated function adds both an MLflow trace (for per-request execution visibility) and an MLflow run (for experiment-style bookkeeping and artifacts).
# MAGIC
# MAGIC <div class="code-block-dark" data-language="python">
# MAGIC @mlflow.trace(name="mlflow_chatbot_run", span_type="AGENT", attributes={"agent_name": "MLflow Chatbot"})
# MAGIC async def run_agent(messages: list[dict]) -> str:
# MAGIC     """
# MAGIC     Run the agent with a list of messages and return the final reply.
# MAGIC     - @mlflow.trace creates a trace + root span with inputs/outputs.
# MAGIC     - mlflow.start_run still logs params/artifacts to the experiment.
# MAGIC     """
# MAGIC     with mlflow.start_run(nested=True):
# MAGIC         # Classic run logging (shows up in Runs/Evaluations)
# MAGIC         mlflow.log_param("agent_name", agent.name)
# MAGIC         mlflow.log_param("model_endpoint", agent.model)
# MAGIC         mlflow.log_param("num_messages", len(messages))
# MAGIC         mlflow.log_text(json.dumps(messages, indent=2), "inputs/messages.json")
# MAGIC         # Actual agent call
# MAGIC         result = await Runner.run(agent, messages)
# MAGIC         final_output = result.final_output
# MAGIC         mlflow.log_text(final_output, "outputs/final_output.txt")
# MAGIC         return final_output
# MAGIC </div>
# MAGIC
# MAGIC <p><strong><code>@mlflow.trace(...)</code></strong><br>
# MAGIC This decorator wraps the function in an MLflow trace. Every time <code>run_agent()</code> is called, MLflow automatically records a root span named <code>mlflow_chatbot_run</code> of type <code>AGENT</code>. The span captures the function's inputs, outputs, execution time, and any exceptions — all visible in the MLflow Traces UI.</p>
# MAGIC
# MAGIC <p><strong><code>mlflow.start_run(nested=True)</code></strong><br>
# MAGIC Opens a nested MLflow run inside the trace context. <code>nested=True</code> ensures this run is a child of any active parent run rather than creating a new top-level run. This is the standard pattern when tracing and run logging are used together. If there’s an active run, this becomes its child; otherwise it starts a new top-level run with <code>nested=True</code> ignored.</p>
# MAGIC
# MAGIC <p><strong><code>mlflow.log_param(...)</code></strong><br>
# MAGIC Logs key-value parameters to the run: the agent's name, the model serving endpoint it is using, and the number of messages in the conversation. These appear in the Runs and Evaluations UI and can be used to filter or compare runs.</p>
# MAGIC
# MAGIC <p><strong><code>mlflow.log_text(...)</code></strong><br>
# MAGIC Saves the full conversation input as <code>inputs/messages.json</code> and the agent's final reply as <code>outputs/final_output.txt</code>. These artifacts are attached to the run and can be downloaded or inspected from the MLflow UI.</p>
# MAGIC
# MAGIC <p>In summary: <code>@mlflow.trace</code> gives you rich, per-request execution visibility; <code>mlflow.start_run</code> gives you experiment-style bookkeeping and artifacts for that same request.</p>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and use it to replace the existing <code>run_agent()</code> function in your <code>agent.py</code> file.</p>
# MAGIC
# MAGIC <style id="prism-inline-css">
# MAGIC code[class*="language-"],pre[class*="language-"]{color:#ccc;background:0 0;font-family:Consolas,Monaco,'Andale Mono','Ubuntu Mono',monospace;font-size:1em;text-align:left;white-space:pre;word-spacing:normal;word-break:normal;word-wrap:normal;line-height:1.5;tab-size:4;hyphens:none}pre[class*="language-"]{padding:1em;margin:.5em 0;overflow:auto}:not(pre)>code[class*="language-"],pre[class*="language-"]{background:#2d2d2d}:not(pre)>code[class*="language-"]{padding:.1em;border-radius:.3em;white-space:normal}.token.comment,.token.block-comment,.token.prolog,.token.doctype,.token.cdata{color:#999}.token.punctuation{color:#ccc}.token.tag,.token.attr-name,.token.namespace,.token.deleted{color:#e2777a}.token.function-name{color:#6196cc}.token.boolean,.token.number,.token.function{color:#f08d49}.token.property,.token.class-name,.token.constant,.token.symbol{color:#f8c555}.token.selector,.token.important,.token.atrule,.token.keyword,.token.builtin{color:#cc99cd}.token.string,.token.char,.token.attr-value,.token.regex,.token.variable{color:#7ec699}.token.operator,.token.entity,.token.url{color:#67cdcc}.token.important,.token.bold{font-weight:700}.token.italic{font-style:italic}.token.entity{cursor:help}.token.inserted{color:green}
# MAGIC </style>
# MAGIC
# MAGIC <script>
# MAGIC (function(){
# MAGIC function escapeHtml(text) {
# MAGIC     var div = document.createElement('div');
# MAGIC     div.textContent = text;
# MAGIC     return div.innerHTML;
# MAGIC }
# MAGIC var Prism = window.Prism = {
# MAGIC     languages: {},
# MAGIC     highlight: function(text, grammar) {
# MAGIC         return this.tokenize(text, grammar).map(function(token) {
# MAGIC             if (typeof token === 'string') return escapeHtml(token);
# MAGIC             return '<span class="token ' + token.type + '">' + escapeHtml(token.content) + '</span>';
# MAGIC         }).join('');
# MAGIC     },
# MAGIC     tokenize: function(text, grammar) {
# MAGIC         var tokens = [text];
# MAGIC         for (var key in grammar) {
# MAGIC             var pattern = grammar[key];
# MAGIC             for (var i = 0; i < tokens.length; i++) {
# MAGIC                 if (typeof tokens[i] !== 'string') continue;
# MAGIC                 var match, matches = [];
# MAGIC                 pattern.lastIndex = 0;
# MAGIC                 while ((match = pattern.exec(tokens[i])) !== null) {
# MAGIC                     matches.push({index: match.index, length: match[0].length, value: match[0]});
# MAGIC                 }
# MAGIC                 if (!matches.length) continue;
# MAGIC                 var newTokens = [];
# MAGIC                 var lastIndex = 0;
# MAGIC                 matches.forEach(function(m) {
# MAGIC                     if (m.index > lastIndex) newTokens.push(tokens[i].substring(lastIndex, m.index));
# MAGIC                     newTokens.push({type: key, content: m.value});
# MAGIC                     lastIndex = m.index + m.length;
# MAGIC                 });
# MAGIC                 if (lastIndex < tokens[i].length) newTokens.push(tokens[i].substring(lastIndex));
# MAGIC                 tokens.splice.apply(tokens, [i, 1].concat(newTokens));
# MAGIC             }
# MAGIC         }
# MAGIC         return tokens;
# MAGIC     },
# MAGIC     highlightElement: function(element) {
# MAGIC         element.innerHTML = this.highlight(element.textContent, this.languages.python);
# MAGIC     }
# MAGIC };
# MAGIC Prism.languages.python = {
# MAGIC     'comment': /#.*/g,
# MAGIC     'string': /("""[\s\S]*?"""|'''[\s\S]*?'''|"[^"]*"|'[^']*')/g,
# MAGIC     'keyword': /\b(import|from|def|class|return|if|elif|else|for|while|try|except|finally|with|as|pass|break|continue|yield|lambda|async|await|None|True|False)\b/g,
# MAGIC     'function': /\b\w+(?=\()/g,
# MAGIC     'number': /\b\d+\.?\d*\b/g,
# MAGIC     'operator': /[-+*/%=<>!&|^~]+/g,
# MAGIC     'punctuation': /[{}[\];(),.]/g
# MAGIC };
# MAGIC document.querySelectorAll('.code-block-dark').forEach(function(block) {
# MAGIC     if (block.getAttribute('data-processed')) return;
# MAGIC     block.setAttribute('data-processed', 'true');
# MAGIC     var code = block.textContent.trim();
# MAGIC     var id = 'code-dark-' + Math.random().toString(36).substr(2, 9);
# MAGIC     block.innerHTML =
# MAGIC         '<div style="position:relative;margin:16px 0;">' +
# MAGIC             '<button class="copy-btn" style="position:absolute;top:8px;right:8px;padding:4px 12px;font-size:12px;background:#555;color:#fff;border:1px solid #666;border-radius:4px;cursor:pointer;">Copy</button>' +
# MAGIC             '<pre style="background:#2d2d2d;border-radius:8px;padding:16px;padding-top:40px;overflow-x:auto;margin:0;border:1px solid #444;"><code id="' + id + '" class="language-python"></code></pre>' +
# MAGIC         '</div>';
# MAGIC     var codeEl = document.getElementById(id);
# MAGIC     codeEl.textContent = code;
# MAGIC     Prism.highlightElement(codeEl);
# MAGIC     block.querySelector('.copy-btn').onclick = function() {
# MAGIC         var t = document.createElement('textarea');
# MAGIC         t.value = code;
# MAGIC         document.body.appendChild(t);
# MAGIC         t.select();
# MAGIC         document.execCommand('copy');
# MAGIC         document.body.removeChild(t);
# MAGIC         this.textContent = '✓ Copied!';
# MAGIC         var btn = this;
# MAGIC         setTimeout(function(){ btn.textContent='Copy'; },2000);
# MAGIC     };
# MAGIC });
# MAGIC })();
# MAGIC </script>

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### D4. Update `databricks.yml` to Add the MLflow Experiment Resource
# MAGIC
# MAGIC Next, add the MLflow experiment as a declared app resource and inject its ID and name as environment variables. Replace the contents of your `databricks.yml` with the version below.
# MAGIC
# MAGIC <div class="code-block-dark" data-language="yaml">
# MAGIC bundle:
# MAGIC   name: mlflow_chatbot
# MAGIC
# MAGIC resources:
# MAGIC   experiments:
# MAGIC     chatbot_experiment:
# MAGIC       name: /Users/${workspace.current_user.userName}/simple-chatbot-experiment
# MAGIC   apps:
# MAGIC     mlflow_chatbot:
# MAGIC       name: agent-${workspace.current_user.id}-${bundle.target}-2
# MAGIC       description: "Simple chatbot agent with MLflow tracing"
# MAGIC       source_code_path: ./
# MAGIC       resources:
# MAGIC         - name: serving-endpoint
# MAGIC           serving_endpoint:
# MAGIC             name: databricks-gpt-5-2
# MAGIC             permission: CAN_QUERY
# MAGIC         - name: app-experiment
# MAGIC           experiment:
# MAGIC             experiment_id: ${resources.experiments.chatbot_experiment.id}
# MAGIC             permission: CAN_EDIT
# MAGIC targets:
# MAGIC   dev:
# MAGIC     mode: development
# MAGIC     default: true
# MAGIC </div>
# MAGIC
# MAGIC <p><strong><code>resources.experiments.chatbot_experiment</code></strong><br>
# MAGIC Declares a new MLflow experiment as a bundle-managed resource. When the bundle is deployed, DABs will create this experiment in your workspace if it does not already exist. The experiment path is constructed using the <code>${workspace.current_user.userName}</code> substitution so each user gets their own experiment.</p>
# MAGIC
# MAGIC <p><strong><code>apps.mlflow_chatbot.resources</code> — new <code>app-experiment</code> entry</strong><br>
# MAGIC Grants the app's service principal <code>CAN_EDIT</code> permission on the experiment. This is the minimum permission required for the app to create runs and log traces to it at runtime. Without this declaration, the app would be denied access when it calls <code>mlflow.start_run()</code>.</p>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and use it to replace the contents of your <code>databricks.yml</code> file.</p>
# MAGIC
# MAGIC <style id="prism-inline-css">
# MAGIC code[class*="language-"],pre[class*="language-"]{color:#ccc;background:0 0;font-family:Consolas,Monaco,'Andale Mono','Ubuntu Mono',monospace;font-size:1em;text-align:left;white-space:pre;word-spacing:normal;word-break:normal;word-wrap:normal;line-height:1.5;tab-size:4;hyphens:none}pre[class*="language-"]{padding:1em;margin:.5em 0;overflow:auto}:not(pre)>code[class*="language-"],pre[class*="language-"]{background:#2d2d2d}:not(pre)>code[class*="language-"]{padding:.1em;border-radius:.3em;white-space:normal}.token.comment,.token.block-comment,.token.prolog,.token.doctype,.token.cdata{color:#999}.token.punctuation{color:#ccc}.token.tag,.token.attr-name,.token.namespace,.token.deleted{color:#e2777a}.token.function-name{color:#6196cc}.token.boolean,.token.number,.token.function{color:#f08d49}.token.property,.token.class-name,.token.constant,.token.symbol{color:#f8c555}.token.selector,.token.important,.token.atrule,.token.keyword,.token.builtin{color:#cc99cd}.token.string,.token.char,.token.attr-value,.token.regex,.token.variable{color:#7ec699}.token.operator,.token.entity,.token.url{color:#67cdcc}.token.important,.token.bold{font-weight:700}.token.italic{font-style:italic}.token.entity{cursor:help}.token.inserted{color:green}
# MAGIC </style>
# MAGIC
# MAGIC <script>
# MAGIC (function(){
# MAGIC function escapeHtml(text) {
# MAGIC     var div = document.createElement('div');
# MAGIC     div.textContent = text;
# MAGIC     return div.innerHTML;
# MAGIC }
# MAGIC var Prism = window.Prism = {
# MAGIC     languages: {},
# MAGIC     highlight: function(text, grammar) {
# MAGIC         return this.tokenize(text, grammar).map(function(token) {
# MAGIC             if (typeof token === 'string') return escapeHtml(token);
# MAGIC             return '<span class="token ' + token.type + '">' + escapeHtml(token.content) + '</span>';
# MAGIC         }).join('');
# MAGIC     },
# MAGIC     tokenize: function(text, grammar) {
# MAGIC         var tokens = [text];
# MAGIC         for (var key in grammar) {
# MAGIC             var pattern = grammar[key];
# MAGIC             for (var i = 0; i < tokens.length; i++) {
# MAGIC                 if (typeof tokens[i] !== 'string') continue;
# MAGIC                 var match, matches = [];
# MAGIC                 pattern.lastIndex = 0;
# MAGIC                 while ((match = pattern.exec(tokens[i])) !== null) {
# MAGIC                     matches.push({index: match.index, length: match[0].length, value: match[0]});
# MAGIC                 }
# MAGIC                 if (!matches.length) continue;
# MAGIC                 var newTokens = [];
# MAGIC                 var lastIndex = 0;
# MAGIC                 matches.forEach(function(m) {
# MAGIC                     if (m.index > lastIndex) newTokens.push(tokens[i].substring(lastIndex, m.index));
# MAGIC                     newTokens.push({type: key, content: m.value});
# MAGIC                     lastIndex = m.index + m.length;
# MAGIC                 });
# MAGIC                 if (lastIndex < tokens[i].length) newTokens.push(tokens[i].substring(lastIndex));
# MAGIC                 tokens.splice.apply(tokens, [i, 1].concat(newTokens));
# MAGIC             }
# MAGIC         }
# MAGIC         return tokens;
# MAGIC     },
# MAGIC     highlightElement: function(element) {
# MAGIC         element.innerHTML = this.highlight(element.textContent, this.languages.yaml);
# MAGIC     }
# MAGIC };
# MAGIC Prism.languages.yaml = {
# MAGIC     'comment': /#.*/g,
# MAGIC     'string': /(["'])(?:\\.|(?!\1)[^\\\r\n])*\1/g,
# MAGIC     'keyword': /\b(true|false|null)\b/g,
# MAGIC     'number': /\b\d+\.?\d*\b/g,
# MAGIC     'punctuation': /[{}[\],]/g,
# MAGIC     'operator': /[:]/g
# MAGIC };
# MAGIC document.querySelectorAll('.code-block-dark').forEach(function(block) {
# MAGIC     if (block.getAttribute('data-processed')) return;
# MAGIC     block.setAttribute('data-processed', 'true');
# MAGIC     var code = block.textContent.trim();
# MAGIC     var id = 'code-dark-' + Math.random().toString(36).substr(2, 9);
# MAGIC     block.innerHTML =
# MAGIC         '<div style="position:relative;margin:16px 0;">' +
# MAGIC             '<button class="copy-btn" style="position:absolute;top:8px;right:8px;padding:4px 12px;font-size:12px;background:#555;color:#fff;border:1px solid #666;border-radius:4px;cursor:pointer;">Copy</button>' +
# MAGIC             '<pre style="background:#2d2d2d;border-radius:8px;padding:16px;padding-top:40px;overflow-x:auto;margin:0;border:1px solid #444;"><code id="' + id + '" class="language-yaml"></code></pre>' +
# MAGIC         '</div>';
# MAGIC     var codeEl = document.getElementById(id);
# MAGIC     codeEl.textContent = code;
# MAGIC     Prism.highlightElement(codeEl);
# MAGIC     block.querySelector('.copy-btn').onclick = function() {
# MAGIC         var t = document.createElement('textarea');
# MAGIC         t.value = code;
# MAGIC         document.body.appendChild(t);
# MAGIC         t.select();
# MAGIC         document.execCommand('copy');
# MAGIC         document.body.removeChild(t);
# MAGIC         this.textContent = '✓ Copied!';
# MAGIC         var btn = this;
# MAGIC         setTimeout(function(){ btn.textContent='Copy'; },2000);
# MAGIC     };
# MAGIC });
# MAGIC })();
# MAGIC </script>
# MAGIC

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### D5. Update `app.yaml` to Add the MLflow Experiment Resource ID Environment Variable
# MAGIC
# MAGIC The final file change is to `app.yaml`. Add the MLflow experiment ID under `env`:
# MAGIC
# MAGIC <div class="code-block-dark" data-language="yaml">
# MAGIC env:
# MAGIC   - name: SERVING_ENDPOINT_NAME
# MAGIC     valueFrom: serving-endpoint          # already correct
# MAGIC   - name: MLFLOW_EXPERIMENT_ID
# MAGIC     valueFrom: app-experiment            # experiment app resource key
# MAGIC     
# MAGIC command: ["uv", "run", "start-server"]
# MAGIC </div>
# MAGIC
# MAGIC <p><code>app.yaml</code> defines how your application is launched inside Databricks.  
# MAGIC It acts as the runtime manifest that tells the platform what command should be executed to start your app.</p>
# MAGIC
# MAGIC <p><strong><code>env: [...]</code></strong><br>
# MAGIC This section injects environment variables into your app's runtime.  
# MAGIC Each entry specifies a <code>name</code> (the variable your code reads) and a <code>valueFrom</code> key that references a resource you configured when setting up the Databricks app — in this case, the model serving endpoint.  
# MAGIC Your <code>agent.py</code> reads <code>SERVING_ENDPOINT_NAME</code> and <code>MLFLOW_EXPERIMENT_ID</code> at runtime to know which endpoint and MLflow experiment to route requests to.</p>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and use it to replace the contents of your <code>app.yaml</code> file.</p>
# MAGIC
# MAGIC <style id="prism-inline-css">
# MAGIC code[class*="language-"],pre[class*="language-"]{color:#ccc;background:0 0;font-family:Consolas,Monaco,'Andale Mono','Ubuntu Mono',monospace;font-size:1em;text-align:left;white-space:pre;word-spacing:normal;word-break:normal;word-wrap:normal;line-height:1.5;tab-size:4;hyphens:none}pre[class*="language-"]{padding:1em;margin:.5em 0;overflow:auto}:not(pre)>code[class*="language-"],pre[class*="language-"]{background:#2d2d2d}:not(pre)>code[class*="language-"]{padding:.1em;border-radius:.3em;white-space:normal}.token.comment,.token.block-comment,.token.prolog,.token.doctype,.token.cdata{color:#999}.token.punctuation{color:#ccc}.token.tag,.token.attr-name,.token.namespace,.token.deleted{color:#e2777a}.token.function-name{color:#6196cc}.token.boolean,.token.number,.token.function{color:#f08d49}.token.property,.token.class-name,.token.constant,.token.symbol{color:#f8c555}.token.selector,.token.important,.token.atrule,.token.keyword,.token.builtin{color:#cc99cd}.token.string,.token.char,.token.attr-value,.token.regex,.token.variable{color:#7ec699}.token.operator,.token.entity,.token.url{color:#67cdcc}.token.important,.token.bold{font-weight:700}.token.italic{font-style:italic}.token.entity{cursor:help}.token.inserted{color:green}
# MAGIC </style>
# MAGIC
# MAGIC <script>
# MAGIC (function(){
# MAGIC function escapeHtml(text) {
# MAGIC     var div = document.createElement('div');
# MAGIC     div.textContent = text;
# MAGIC     return div.innerHTML;
# MAGIC }
# MAGIC var Prism = window.Prism = {
# MAGIC     languages: {},
# MAGIC     highlight: function(text, grammar) {
# MAGIC         return this.tokenize(text, grammar).map(function(token) {
# MAGIC             if (typeof token === 'string') return escapeHtml(token);
# MAGIC             return '<span class="token ' + token.type + '">' + escapeHtml(token.content) + '</span>';
# MAGIC         }).join('');
# MAGIC     },
# MAGIC     tokenize: function(text, grammar) {
# MAGIC         var tokens = [text];
# MAGIC         for (var key in grammar) {
# MAGIC             var pattern = grammar[key];
# MAGIC             for (var i = 0; i < tokens.length; i++) {
# MAGIC                 if (typeof tokens[i] !== 'string') continue;
# MAGIC                 var match, matches = [];
# MAGIC                 pattern.lastIndex = 0;
# MAGIC                 while ((match = pattern.exec(tokens[i])) !== null) {
# MAGIC                     matches.push({index: match.index, length: match[0].length, value: match[0]});
# MAGIC                 }
# MAGIC                 if (!matches.length) continue;
# MAGIC                 var newTokens = [];
# MAGIC                 var lastIndex = 0;
# MAGIC                 matches.forEach(function(m) {
# MAGIC                     if (m.index > lastIndex) newTokens.push(tokens[i].substring(lastIndex, m.index));
# MAGIC                     newTokens.push({type: key, content: m.value});
# MAGIC                     lastIndex = m.index + m.length;
# MAGIC                 });
# MAGIC                 if (lastIndex < tokens[i].length) newTokens.push(tokens[i].substring(lastIndex));
# MAGIC                 tokens.splice.apply(tokens, [i, 1].concat(newTokens));
# MAGIC             }
# MAGIC         }
# MAGIC         return tokens;
# MAGIC     },
# MAGIC     highlightElement: function(element) {
# MAGIC         element.innerHTML = this.highlight(element.textContent, this.languages.yaml);
# MAGIC     }
# MAGIC };
# MAGIC Prism.languages.yaml = {
# MAGIC     'comment': /#.*/g,
# MAGIC     'string': /(["'])(?:\\.|(?!\1)[^\\\r\n])*\1/g,
# MAGIC     'keyword': /\b(true|false|null)\b/g,
# MAGIC     'number': /\b\d+\.?\d*\b/g,
# MAGIC     'punctuation': /[{}[\],]/g,
# MAGIC     'operator': /[:]/g
# MAGIC };
# MAGIC document.querySelectorAll('.code-block-dark').forEach(function(block) {
# MAGIC     if (block.getAttribute('data-processed')) return;
# MAGIC     block.setAttribute('data-processed', 'true');
# MAGIC     var code = block.textContent.trim();
# MAGIC     var id = 'code-dark-' + Math.random().toString(36).substr(2, 9);
# MAGIC     block.innerHTML =
# MAGIC         '<div style="position:relative;margin:16px 0;">' +
# MAGIC             '<button class="copy-btn" style="position:absolute;top:8px;right:8px;padding:4px 12px;font-size:12px;background:#555;color:#fff;border:1px solid #666;border-radius:4px;cursor:pointer;">Copy</button>' +
# MAGIC             '<pre style="background:#2d2d2d;border-radius:8px;padding:16px;padding-top:40px;overflow-x:auto;margin:0;border:1px solid #444;"><code id="' + id + '" class="language-yaml"></code></pre>' +
# MAGIC         '</div>';
# MAGIC     var codeEl = document.getElementById(id);
# MAGIC     codeEl.textContent = code;
# MAGIC     Prism.highlightElement(codeEl);
# MAGIC     block.querySelector('.copy-btn').onclick = function() {
# MAGIC         var t = document.createElement('textarea');
# MAGIC         t.value = code;
# MAGIC         document.body.appendChild(t);
# MAGIC         t.select();
# MAGIC         document.execCommand('copy');
# MAGIC         document.body.removeChild(t);
# MAGIC         this.textContent = '✓ Copied!';
# MAGIC         var btn = this;
# MAGIC         setTimeout(function(){ btn.textContent='Copy'; },2000);
# MAGIC     };
# MAGIC });
# MAGIC })();
# MAGIC </script>

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ## E. Redeploy the Updated Agent
# MAGIC
# MAGIC With all three files updated, redeploy the bundle using the same DABs UI workflow you used in the previous demo.
# MAGIC
# MAGIC 1. Navigate inside the **simple-agent-with-mlflow** folder and click on any file (e.g., **databricks.yml**). Click the rocket icon to open the **Deployments** panel.
# MAGIC 2. Click **Deploy** in the **Deployments** section.
# MAGIC 3. Once validation completes and the deployment summary appears, click **Deploy** again to confirm.
# MAGIC 4. After the deployment succeeds, navigate to your app in **Apps** under **Compute** and click **Deploy** to push the updated source code to the running app.
# MAGIC 5. Wait for the app status to return to **Running**.
# MAGIC
# MAGIC <div style="border-left: 4px solid #1976d2; background: #e3f2fd; padding: 16px 20px; border-radius: 4px; margin: 16px 0;">
# MAGIC <div style="display: flex; align-items: flex-start; gap: 12px;">
# MAGIC <div>
# MAGIC <strong style="color: #0d47a1; font-size: 1.1em;">What the DAB Creates</strong>
# MAGIC <p style="margin: 8px 0 0 0; color: #333;">On this deployment, DABs will also create the MLflow experiment at the path defined in <code>databricks.yml</code> if it does not already exist, and grant the app's service principal the declared permissions on it.</p>
# MAGIC </div>
# MAGIC </div>
# MAGIC </div>

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ## F. Verify Traces in the MLflow UI
# MAGIC
# MAGIC Once the app is running, send a few messages through the chat interface to generate traces.
# MAGIC
# MAGIC 1. Open the app endpoint from the **Apps** page.
# MAGIC 2. Send one or more messages in the chat UI.
# MAGIC 3. In your Databricks workspace, navigate to **Experiments** and open the experiment named **simple-chatbot-experiment** (under your user path).
# MAGIC 4. Click the **Traces** tab. You should see a trace entry for each message you sent, labeled **mlflow_chatbot_run** (you might need to enable the column in the UI by clicking on the **Columns** filter and selecting **Trace name**).
# MAGIC 5. Click a trace to expand it. You will see the root span with its inputs (the messages list), the final output string, execution duration, and any nested spans produced by the Agents SDK runner.
# MAGIC 6. Back in the experiment landing page, click on the **Evaluation runs** tab. Each invocation also appears as a nested run with the logged parameters (`agent_name`, `model_endpoint`, `num_messages`) and the artifact files (`inputs/messages.json`, `outputs/final_output.txt`). Click on one of the runs and view the **Overview** tab to see logged **Parameters** and **Artifacts**.
# MAGIC
# MAGIC <div style="border-left: 4px solid #1976d2; background: #e3f2fd; padding: 16px 20px; border-radius: 4px; margin: 16px 0;">
# MAGIC <div style="display: flex; align-items: flex-start; gap: 12px;">
# MAGIC <div>
# MAGIC <strong style="color: #0d47a1; font-size: 1.1em;">Traces vs. Runs</strong>
# MAGIC <ul style="margin: 12px 0 0 16px; color: #333;">
# MAGIC <li><strong>Traces</strong> capture the execution graph of a single request — spans, timing, inputs, and outputs — and are best for debugging individual interactions.</li>
# MAGIC <li><strong>Runs</strong> capture experiment-level metadata — parameters, metrics, and artifacts — and are best for comparing behavior across many interactions over time.</li>
# MAGIC </ul>
# MAGIC </div>
# MAGIC </div>
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC ## G. Clean Up
# MAGIC
# MAGIC When you are finished with this demo, remove the resources created during deployment.
# MAGIC
# MAGIC 1. Navigate to **Apps** under **Compute** and select the 3 vertical dots next to your app. Select **Delete** to stop and remove the app.
# MAGIC 2. Navigate to **Experiments**, open **simple-chatbot-experiment**, and delete it if you no longer need the trace and run history.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusion
# MAGIC
# MAGIC In this demo, you extended a deployed Databricks App agent with MLflow observability by making targeted changes to two files and redeploying via DABs.
# MAGIC
# MAGIC Key accomplishments:
# MAGIC
# MAGIC - **Orthogonal deployment** — understood how app-based agents differ from UC-registered model serving deployments, and why UC registration is optional in this pattern
# MAGIC - **MLflow tracing** — added `@mlflow.trace` to `run_agent()` to capture per-request execution spans, inputs, outputs, and timing in the MLflow Traces UI
# MAGIC - **Experiment tracking** — used `mlflow.start_run(nested=True)` to log parameters and artifacts to a named MLflow experiment for each agent invocation
# MAGIC - **Environment-driven configuration** — kept all experiment references out of source code by reading `MLFLOW_EXPERIMENT_NAME` from an environment variable injected by the DAB
# MAGIC - **DAB resource declaration** — updated `databricks.yml` to declare the MLflow experiment as a bundle-managed resource and grant the app's service principal the permissions it needs at runtime
# MAGIC
# MAGIC ### Next Steps
# MAGIC
# MAGIC With tracing and experiment tracking in place, the next step is to add tools to the agent so it can take actions beyond answering questions. The following demo introduces tool use with the OpenAI Agents SDK and shows how tool calls appear as child spans within your MLflow traces.

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; <span id="dbx-year"></span> Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the
# MAGIC <a href="https://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy">Privacy Policy</a> |
# MAGIC <a href="https://databricks.com/terms-of-use">Terms of Use</a> |
# MAGIC <a href="https://help.databricks.com/">Support</a>
# MAGIC <script>
# MAGIC   document.getElementById("dbx-year").textContent = new Date().getFullYear();
# MAGIC </script>