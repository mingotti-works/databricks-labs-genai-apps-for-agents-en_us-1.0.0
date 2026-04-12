# Databricks notebook source
# MAGIC %md
# MAGIC ![Databricks Academy](./Includes/images/db-academy.png)

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC # Demo - Integrating Databricks MCP with an App-Based Agent
# MAGIC
# MAGIC ## Overview
# MAGIC
# MAGIC This demo builds directly on the previous notebook. You already have a deployed Databricks App agent with MLflow tracing wired in. Now you will extend that agent to call external tools by connecting it to a **Databricks Managed MCP server** backed by a Unity Catalog function.
# MAGIC
# MAGIC The Model Context Protocol (MCP) is an open standard that lets AI applications discover and invoke tools hosted on external servers without custom integration code for each one. On Databricks, MCP servers can expose Unity Catalog functions, Genie spaces, Vector Search indexes, and more — all through a single, consistent interface.
# MAGIC
# MAGIC By the end of this demo, your agent will be able to answer questions that require real data lookups, with every tool call captured as a child span in your MLflow traces.
# MAGIC
# MAGIC ## Learning Objectives
# MAGIC
# MAGIC By the end of this demonstration, you will be able to:
# MAGIC
# MAGIC 1. **Explain the Model Context Protocol (MCP)** — its architecture, primitives, and lifecycle
# MAGIC 2. **Describe the three MCP server types on Databricks** — Managed, External, and Custom
# MAGIC 3. **Add MCP imports and an `McpServer` instance** to an existing `agent.py` file
# MAGIC 4. **Wrap `Runner.run()` in an async MCP context manager** so tools are available at call time
# MAGIC 5. **Update `app.yaml` and `databricks.yml`** to expose new environment variables and grant the UC function permission
# MAGIC 6. **Redeploy the updated agent** and verify tool call spans appear in the MLflow Traces UI
# MAGIC
# MAGIC <div style="border-left: 4px solid #f44336; background: #ffebee; padding: 16px 20px; border-radius: 4px; margin: 16px 0;">
# MAGIC <div style="display: flex; align-items: flex-start; gap: 12px;">
# MAGIC <div>
# MAGIC <strong style="color: #c62828; font-size: 1.1em;">Prerequisites</strong>
# MAGIC <p style="margin: 8px 0 0 0; color: #333;">Complete <strong>Demo - Integrating App-Based Agents with MLflow</strong> before proceeding. This demo assumes you have already worked through the previous notebook where you built your <code>simple-agent-with-mlflow</code> folder and are familiar with app deployment using Declarative Automation Bundles (DABs).</p>
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
# MAGIC Run the cell below to configure your UC and workspace assets for this demo. This setup extends the environment created in the previous notebook and populates the **simple-tool-calling-agent** folder you will work in throughout this demo.

# COMMAND ----------

# MAGIC %run ./Includes/Classroom-Setup-3

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### B3. What the Setup Created
# MAGIC
# MAGIC As part of the classroom setup, a new DAB folder called **simple-tool-calling-agent** has been added to the file browser on the left. This folder is a copy of the `simple-agent-with-mlflow` folder you completed in the previous demo — it already has MLflow tracing wired in. Your goal in this demo is to add MCP tool-calling on top of that foundation.
# MAGIC
# MAGIC The setup also registered a Unity Catalog function in your working schema that the agent will use as a tool:
# MAGIC
# MAGIC | Object | Location |
# MAGIC |---|---|
# MAGIC | UC function | `labuser_XXX.agent_apps.avg_neigh_price` |
# MAGIC | DAB folder | `simple-tool-calling-agent/` |
# MAGIC
# MAGIC <div style="border-left: 4px solid #1976d2; background: #e3f2fd; padding: 16px 20px; border-radius: 4px; margin: 16px 0;">
# MAGIC <div style="display: flex; align-items: flex-start; gap: 12px;">
# MAGIC <div>
# MAGIC <strong style="color: #0d47a1; font-size: 1.1em;">Three Files to Edit</strong>
# MAGIC <p style="margin: 8px 0 0 0; color: #333;">This demo requires changes to three files inside the <code>simple-tool-calling-agent</code> folder: <code>agent.py</code>, <code>app.yaml</code>, and <code>databricks.yml</code>. Each section below walks through exactly what to add and why.</p>
# MAGIC </div>
# MAGIC </div>
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. Model Context Protocol (MCP)

# COMMAND ----------

# MAGIC %md
# MAGIC ### C1. What Is MCP?
# MAGIC
# MAGIC The **Model Context Protocol (MCP)** is an open-source standard for connecting AI applications to external systems. Summarizing from the official docs [here](https://modelcontextprotocol.io/docs/getting-started/intro) and [here](https://modelcontextprotocol.io/docs/learn/architecture), think of it like a USB-C port for AI: just as USB-C provides a standardized physical interface for electronic devices, MCP provides a standardized software interface that lets AI applications communicate with data sources, tools, and workflows in a consistent, predictable way.
# MAGIC
# MAGIC Without a standard like MCP, every AI application would need custom integration code for every external system it wants to reach. MCP eliminates that overhead by defining a shared protocol that any compliant client or server can speak.
# MAGIC
# MAGIC MCP is supported across a wide ecosystem of AI clients and developer tools — including Claude, ChatGPT, Visual Studio Code, and Cursor — meaning a server you build once can integrate with many hosts.

# COMMAND ----------

# MAGIC %md
# MAGIC ### C2. MCP Architecture
# MAGIC
# MAGIC MCP follows a **client-server architecture** with three key participants:
# MAGIC
# MAGIC | Participant | Role |
# MAGIC |---|---|
# MAGIC | **MCP Host** | The AI application (e.g., a Databricks App) that manages one or more MCP clients |
# MAGIC | **MCP Client** | A component inside the host that maintains a dedicated connection to a single MCP server |
# MAGIC | **MCP Server** | A program that exposes tools, resources, or prompts to connected clients |
# MAGIC
# MAGIC A single host can connect to multiple servers simultaneously — each through its own dedicated client instance. MCP servers can run **locally** (on the same machine, using stdio transport) or **remotely** (over the network, using Streamable HTTP transport).
# MAGIC
# MAGIC MCP is organized into two layers:
# MAGIC
# MAGIC - **Data layer** — Defines the JSON-RPC 2.0 message format, lifecycle management, and core primitives (tools, resources, prompts).
# MAGIC - **Transport layer** — Handles the communication channel (stdio or HTTP), message framing, and authentication.

# COMMAND ----------

# MAGIC %md
# MAGIC ### C3. MCP Primitives
# MAGIC
# MAGIC MCP primitives define what clients and servers can offer each other. They are the core vocabulary of the protocol.
# MAGIC
# MAGIC **Server-side primitives** (what an MCP server exposes to clients):
# MAGIC
# MAGIC | Primitive | Description |
# MAGIC |---|---|
# MAGIC | **Tools** | Executable functions an AI can invoke — e.g., run a database query, call an API, perform a calculation |
# MAGIC | **Resources** | Read-only data sources that provide context — e.g., file contents, database schema, API responses |
# MAGIC | **Prompts** | Reusable interaction templates — e.g., system prompts, few-shot examples |
# MAGIC
# MAGIC **Client-side primitives** (what an MCP client exposes back to the server):
# MAGIC
# MAGIC | Primitive | Description |
# MAGIC |---|---|
# MAGIC | **Sampling** | Allows the server to request LLM completions from the host without bundling its own model SDK |
# MAGIC | **Elicitation** | Allows the server to request additional input or confirmation from the user |
# MAGIC | **Logging** | Enables the server to send debug and monitoring messages to the client |
# MAGIC
# MAGIC Each primitive type supports discovery via `*/list` methods. For example, a client calls `tools/list` to learn what tools a server offers before invoking any of them. This makes the set of available capabilities **dynamic** — it can change at runtime without requiring client code changes.

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### C4. The MCP Lifecycle
# MAGIC
# MAGIC Every MCP connection follows a structured lifecycle. Understanding this sequence helps you reason about how your agent discovers and uses tools at runtime.
# MAGIC
# MAGIC **1. Initialization — capability negotiation**
# MAGIC
# MAGIC The client sends an `initialize` request declaring its protocol version and the primitives it supports. The server responds with its own capabilities. This handshake ensures both sides agree on what the connection can do before any tools are called.
# MAGIC
# MAGIC **2. Tool discovery — `tools/list`**
# MAGIC
# MAGIC After initialization, the client sends a `tools/list` request. The server responds with an array of tool objects, each containing a `name`, a human-readable `title`, a `description`, and an `inputSchema` (JSON Schema) that defines required and optional parameters.
# MAGIC
# MAGIC **3. Tool execution — `tools/call`**
# MAGIC
# MAGIC To invoke a tool, the client sends a `tools/call` request with the exact tool `name` from the discovery response and an `arguments` object that matches the tool's `inputSchema`. The server returns a `content` array — typically text, but MCP supports multiple content types.
# MAGIC
# MAGIC **4. Real-time notifications**
# MAGIC
# MAGIC Servers that declared `"listChanged": true` during initialization can push `notifications/tools/list_changed` messages to clients whenever their tool set changes. The client responds by re-issuing `tools/list` to refresh its registry. This event-driven model means your agent automatically adapts to new or removed tools without polling.
# MAGIC
# MAGIC <div style="border-left: 4px solid #1976d2; background: #e3f2fd; padding: 16px 20px; border-radius: 4px; margin: 16px 0;">
# MAGIC <div style="display: flex; align-items: flex-start; gap: 12px;">
# MAGIC <div>
# MAGIC <strong style="color: #0d47a1; font-size: 1.1em;">Databricks Best Practices</strong>
# MAGIC <ul style="margin: 12px 0 0 16px; color: #333;">
# MAGIC <li><strong>Do not hardcode tool names.</strong> Always discover tools dynamically via <code>tools/list</code> — the available set may change as Databricks adds or modifies capabilities.</li>
# MAGIC <li><strong>Do not parse tool output programmatically.</strong> Output formats are not guaranteed to be stable. Let the LLM interpret tool responses.</li>
# MAGIC <li><strong>Let the LLM decide.</strong> Your agent's LLM should determine which tools to call based on the user's request and the tool descriptions returned by the server.</li>
# MAGIC </ul>
# MAGIC </div>
# MAGIC </div>
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC ### C5. MCP on Databricks
# MAGIC
# MAGIC Databricks provides three categories of MCP server to cover different integration needs:
# MAGIC
# MAGIC | Type | Description |
# MAGIC |---|---|
# MAGIC | **Managed MCP** | Pre-configured servers that give immediate access to Databricks features (Unity Catalog functions, Genie spaces, Vector Search, Databricks SQL) |
# MAGIC | **External MCP** | Managed connections to MCP servers hosted outside of Databricks |
# MAGIC | **Custom MCP** | A custom MCP server you write and host as a Databricks App |
# MAGIC
# MAGIC To view the MCP servers available in your workspace, navigate to **Agents > MCP Servers** in the left sidebar.
# MAGIC
# MAGIC **NOTE:** Compute pricing varies by server type. Custom MCP servers use Databricks Apps pricing. Managed MCP servers are billed according to the underlying feature — serverless general compute for Unity Catalog functions, serverless SQL for Genie spaces, and so on.
# MAGIC
# MAGIC In the sections that follow, you will connect your existing agent to a Managed MCP server that exposes a Unity Catalog function as a tool.

# COMMAND ----------

# MAGIC %md
# MAGIC ## D. Compare All Three Files
# MAGIC Below is a quick summary of what updates we will be making to the pre-existing files.

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### D1. Side-by-Side Diff: `agent.py`
# MAGIC
# MAGIC The table below maps every meaningful difference between the MLflow version of `agent.py` (from the previous demo) and the MCP-enabled target version. Lines that are identical in both versions are omitted for clarity.
# MAGIC
# MAGIC | Location in file | MLflow agent (`simple-agent-with-mlflow`) | MCP agent (`simple-tool-calling-agent`) | Why it changes |
# MAGIC |---|---|---|---|
# MAGIC | **Imports** | `from agents import Agent, Runner, ...` | Adds `from databricks_openai.agents import McpServer` and `from databricks.sdk import WorkspaceClient` | `McpServer` is the Databricks helper that wraps a UC-function MCP server; `WorkspaceClient` authenticates the connection |
# MAGIC | **Environment variables** | `SERVING_ENDPOINT_NAME`, `MLFLOW_EXPERIMENT_ID`, `MLFLOW_EXPERIMENT_NAME` | Adds `CATALOG_NAME` and `FUNCTION_1_NAME` via `os.getenv()` | The MCP server factory needs the catalog name and function name to build the correct Managed MCP endpoint URL |
# MAGIC | **Workspace client** | _(not present)_ | `ws = WorkspaceClient()` | Required to authenticate `McpServer` against your workspace at runtime |
# MAGIC | **MCP server instance** | _(not present)_ | `mcp_server = McpServer.from_uc_function(...)` | Creates a handle to the MCP server that exposes `avg_neigh_price` as a tool |
# MAGIC | **Agent definition** | `Agent(name=..., instructions=..., model=...)` | Adds `mcp_servers=[mcp_server]` | Tells the OpenAI Agents SDK which MCP servers to query for available tools |
# MAGIC | **`run_agent()` body** | `result = await Runner.run(agent, messages)` (bare call) | Wraps the call in `async with mcp_server:` | Opens the MCP connection before the run and closes it cleanly after — required because `McpServer` is an async context manager |
# MAGIC
# MAGIC The MLflow tracing decorator (`@mlflow.trace`), `mlflow.start_run`, and all logging calls are **identical** in both versions. You are adding tool support on top of the existing observability layer, not replacing it.

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### D2. Side-by-Side Diff: `app.yaml`
# MAGIC
# MAGIC The `app.yaml` file controls which environment variables are injected into the running Databricks App. The MCP agent reads two new variables at startup — one for the catalog name and one for the UC function name — so both must be declared here.
# MAGIC
# MAGIC | Location in file | MLflow `app.yaml` | MCP `app.yaml` | Why it changes |
# MAGIC |---|---|---|---|
# MAGIC | **`env` block** | `SERVING_ENDPOINT_NAME` and `MLFLOW_EXPERIMENT_ID` only | Adds `CATALOG_NAME` (static `value`) and `FUNCTION_1_NAME` (static `value`) | `agent.py` reads these two variables via `os.getenv()` to construct the `McpServer` instance; without them the app will fail to start |
# MAGIC | **`command`** | `["uv", "run", "start-server"]` | Unchanged | No change needed |
# MAGIC
# MAGIC **NOTE:** `CATALOG_NAME` and `FUNCTION_1_NAME` use a static `value` field rather than `valueFrom`. This means the values are hardcoded in `app.yaml` rather than resolved from a bundle resource reference. In the next section you will see how `databricks.yml` uses a `variables` block to keep these values parameterized at the bundle level.

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### D3. Side-by-Side Diff: `databricks.yml`
# MAGIC
# MAGIC The bundle file needs two additions to grant the deployed app the permissions it requires to invoke the Unity Catalog function at runtime.
# MAGIC
# MAGIC | Location in file | MLflow bundle (`simple-agent-with-mlflow`) | Tool-calling bundle (`simple-tool-calling-agent`) | Why it changes |
# MAGIC |---|---|---|---|
# MAGIC | **`variables` block** | _(not present)_ | Adds `catalog_name` and `function_1_name` variables, each with a `description` and a `default` | Provides reusable, per-user values that can be referenced throughout the bundle file without hardcoding; defaults match the values used in `app.yaml` |
# MAGIC | **`resources.apps.tool_calling_chatbot.resources`** | `serving-endpoint` and `app-experiment` only | Adds a third entry: `uc-function-1` of type `uc_securable` pointing at `${var.catalog_name}.agent_apps.${var.function_1_name}` with `EXECUTE` permission | Grants the app's service principal the `EXECUTE` privilege on the Unity Catalog function so `McpServer` can invoke it at runtime |
# MAGIC
# MAGIC All other fields — `bundle.name`, the experiment resource, the app name, `source_code_path`, the serving-endpoint resource, and the `targets` block — are **identical** in both versions.

# COMMAND ----------

# MAGIC %md
# MAGIC ## E. Update `agent.py`

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### E1. Add MCP Imports
# MAGIC
# MAGIC Open `agent.py` inside the **simple-tool-calling-agent** folder. The first change is to add two new imports directly below the existing `from agents import ...` line.
# MAGIC
# MAGIC <div class="code-block-dark" data-language="python">
# MAGIC from databricks_openai.agents import McpServer
# MAGIC from databricks.sdk import WorkspaceClient
# MAGIC </div>
# MAGIC
# MAGIC <p><code>McpServer</code> is a Databricks-provided helper class from the <code>databricks_openai</code> package. It wraps the MCP client connection and handles authentication, tool discovery, and the async lifecycle for you — so you do not need to write any raw JSON-RPC code.</p>
# MAGIC
# MAGIC <p><code>WorkspaceClient</code> is the standard Databricks SDK client. It reads your workspace URL and authentication token from the environment automatically when running inside a Databricks App, so no credentials need to be hardcoded.</p>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and paste these two lines into the imports section of your <code>agent.py</code> file, directly below the existing <code>from agents import ...</code> line.</p>
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
# MAGIC ### E2. Add the Workspace Client and MCP Server Instance
# MAGIC
# MAGIC Next, add the environment variable reads, workspace client, and MCP server instance directly after the MLflow experiment configuration block (after the `if experiment_id / elif experiment_name` block).
# MAGIC
# MAGIC <div class="code-block-dark" data-language="python">
# MAGIC catalog_name = os.getenv("CATALOG_NAME")
# MAGIC function_name = os.getenv("FUNCTION_1_NAME")
# MAGIC
# MAGIC ws = WorkspaceClient()
# MAGIC
# MAGIC mcp_server = McpServer.from_uc_function(
# MAGIC     catalog=catalog_name,
# MAGIC     schema="agent_apps",
# MAGIC     workspace_client=ws,
# MAGIC     timeout=60.0,
# MAGIC )
# MAGIC </div>
# MAGIC
# MAGIC <p><strong><code>os.getenv("CATALOG_NAME")</code> and <code>os.getenv("FUNCTION_1_NAME")</code></strong><br>
# MAGIC These two values are injected by the Databricks App runtime from the <code>env</code> block you will add to <code>app.yaml</code> in section F. Reading them via <code>os.getenv()</code> keeps the agent code free of hardcoded catalog or function names, making it portable across users and environments.</p>
# MAGIC
# MAGIC <p><strong><code>WorkspaceClient()</code></strong><br>
# MAGIC Instantiates the Databricks SDK workspace client. When running inside a Databricks App, it automatically picks up the workspace host URL and the app's service principal token from the environment — no manual credential configuration is needed.</p>
# MAGIC
# MAGIC <p><strong><code>McpServer.from_uc_function(...)</code></strong><br>
# MAGIC A convenience factory method that constructs an MCP server handle pointing at a single Unity Catalog function. It builds the correct Managed MCP endpoint URL from the catalog, schema, and function name you provide, then attaches the workspace client for authentication. The resulting <code>mcp_server</code> object is an async context manager — you will open it inside <code>run_agent()</code> in the next step.</p>
# MAGIC
# MAGIC <p><strong><code>timeout=60.0</code></strong><br>
# MAGIC Sets the maximum number of seconds to wait for a tool call response from the MCP server. Increase this value if your UC function performs long-running queries.</p>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and paste it into <code>agent.py</code> directly after the MLflow experiment configuration block.</p>
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
# MAGIC ### E3. Add `mcp_servers` to the Agent Definition
# MAGIC
# MAGIC Locate the `Agent(...)` constructor in `agent.py` and add the `mcp_servers` parameter as shown below.
# MAGIC
# MAGIC <div class="code-block-dark" data-language="python">
# MAGIC agent = Agent(
# MAGIC     name="Simple Chatbot",
# MAGIC     instructions="You are a helpful assistant. Answer the user's questions clearly and concisely.",
# MAGIC     model=SERVING_ENDPOINT_NAME,
# MAGIC     mcp_servers=[mcp_server],
# MAGIC )
# MAGIC </div>
# MAGIC
# MAGIC <p><strong><code>mcp_servers=[mcp_server]</code></strong><br>
# MAGIC Registers the MCP server handle with the OpenAI Agents SDK. At runtime, the SDK calls <code>tools/list</code> on each registered server to discover available tools, then makes those tools available to the LLM as callable functions. The LLM decides autonomously which tool to invoke based on the user's request and the tool descriptions returned by the server.</p>
# MAGIC
# MAGIC <p>You can register multiple MCP servers by adding more entries to the list — each server can expose a different set of tools.</p>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and use it to replace the existing <code>Agent(...)</code> constructor in your <code>agent.py</code> file.</p>
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
# MAGIC ### E4. Wrap `Runner.run()` in the MCP Context Manager
# MAGIC
# MAGIC The final change to `agent.py` is to `run_agent()`. Replace the existing function body with the version below, which wraps `Runner.run()` in `async with mcp_server:`.
# MAGIC
# MAGIC <div class="code-block-dark" data-language="python">
# MAGIC @mlflow.trace(
# MAGIC     name="tool_calling_chatbot_run",
# MAGIC     span_type="AGENT",
# MAGIC     attributes={"agent_name": "Tool-calling Chatbot"},
# MAGIC )
# MAGIC async def run_agent(messages: list[dict]) -> str:
# MAGIC     with mlflow.start_run(nested=True):
# MAGIC         mlflow.log_param("agent_name", agent.name)
# MAGIC         mlflow.log_param("model_endpoint", agent.model)
# MAGIC         mlflow.log_param("num_messages", len(messages))
# MAGIC         mlflow.log_text(json.dumps(messages, indent=2), "inputs/messages.json")
# MAGIC     # IMPORTANT: McpServer is an async context manager
# MAGIC     async with mcp_server:
# MAGIC         result = await Runner.run(agent, messages)
# MAGIC     final_output = result.final_output
# MAGIC     mlflow.log_text(final_output, "outputs/final_output.txt")
# MAGIC     return final_output
# MAGIC </div>
# MAGIC
# MAGIC <p><strong><code>async with mcp_server:</code></strong><br>
# MAGIC <code>McpServer</code> is an async context manager. Entering the <code>async with</code> block opens the connection to the MCP server, performs the capability handshake, and calls <code>tools/list</code> to register available tools with the agent. Exiting the block closes the connection cleanly. Placing this around <code>Runner.run()</code> ensures the MCP connection is live for the entire duration of the agent's execution — including any tool calls the LLM decides to make — and is released immediately after.</p>
# MAGIC
# MAGIC <p>All MLflow logging calls remain identical to the previous version. The only structural change is that <code>Runner.run()</code> is now nested inside the <code>async with</code> block, and the MLflow run logging is separated from the agent execution so the run is closed before the MCP context opens.</p>
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

# MAGIC %md
# MAGIC ## F. Update `app.yaml`

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### F1. Add `CATALOG_NAME` and `FUNCTION_1_NAME` Environment Variables
# MAGIC
# MAGIC Open `app.yaml` inside the **simple-tool-calling-agent** folder. Add the two new entries to the `env` block as shown below.
# MAGIC
# MAGIC <div class="code-block-dark" data-language="yaml">
# MAGIC env:
# MAGIC   - name: SERVING_ENDPOINT_NAME
# MAGIC     valueFrom: serving-endpoint
# MAGIC   - name: MLFLOW_EXPERIMENT_ID
# MAGIC     valueFrom: app-experiment
# MAGIC   - name: CATALOG_NAME
# MAGIC     value: # <---- Update
# MAGIC   - name: FUNCTION_1_NAME
# MAGIC     value: avg_neigh_price
# MAGIC
# MAGIC command: ["uv", "run", "start-server"]
# MAGIC </div>
# MAGIC
# MAGIC <p><strong><code>CATALOG_NAME</code></strong><br>
# MAGIC Provides the Unity Catalog catalog name to the running app. The agent reads this value via <code>os.getenv("CATALOG_NAME")</code> and passes it to <code>McpServer.from_uc_function()</code> as the <code>catalog</code> argument. Add your actual catalog name (e.g., <code>labuser_sparky_mcspark</code>).</p>
# MAGIC
# MAGIC <p><strong><code>FUNCTION_1_NAME</code></strong><br>
# MAGIC Provides the name of the Unity Catalog function that the MCP server will expose as a tool. The agent reads this via <code>os.getenv("FUNCTION_1_NAME")</code> and passes it as the <code>function_name</code> argument to <code>McpServer.from_uc_function()</code>.</p>
# MAGIC
# MAGIC <p><strong><code>value</code> vs. <code>valueFrom</code></strong><br>
# MAGIC The existing <code>SERVING_ENDPOINT_NAME</code> and <code>MLFLOW_EXPERIMENT_ID</code> entries use <code>valueFrom</code>, which resolves the value from a named bundle resource declared in <code>databricks.yml</code>. The two new entries use a static <code>value</code> field instead, meaning the literal string is embedded directly in <code>app.yaml</code>. The bundle-level <code>variables</code> block you will add to <code>databricks.yml</code> in section G keeps these values parameterized at deploy time.</p>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and use it to replace the existing <code>env</code> block in your <code>app.yaml</code> file.</p>
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

# MAGIC %md
# MAGIC ## G. Update `databricks.yml`

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### G1. Add the `variables` Block
# MAGIC
# MAGIC Open `databricks.yml` inside the **simple-tool-calling-agent** folder. Add the `variables` block directly after the `bundle:` block and before the `resources:` block.
# MAGIC
# MAGIC <div class="code-block-dark" data-language="yaml">
# MAGIC variables:
# MAGIC   catalog_name:
# MAGIC     description: "Per-user lab catalog, e.g. labuser_matthew_mccoy"
# MAGIC     default: # <---- update
# MAGIC   function_1_name:
# MAGIC     description: "Function to grab the average neighborhood price"
# MAGIC     default: avg_neigh_price
# MAGIC </div>
# MAGIC
# MAGIC <p><strong><code>variables</code></strong><br>
# MAGIC The <code>variables</code> block lets you define reusable, parameterized values that can be referenced anywhere in the bundle file using <code>${var.&lt;name&gt;}</code> syntax. Declaring the catalog name and function name here — rather than hardcoding them in the resource definition — makes the bundle portable across users and workspaces without requiring manual edits to the resource block.</p>
# MAGIC
# MAGIC <p><strong><code>default</code></strong><br>
# MAGIC The <code>default</code> value is used when no override is provided at deploy time. Update this to match your actual catalog name before deploying. You can also override variables at deploy time using the <code>--var</code> flag with the DABs CLI: <code>databricks bundle deploy --var="catalog_name=my_catalog"</code>.</p>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and paste it into <code>databricks.yml</code> directly after the closing line of the <code>bundle:</code> block.</p>
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
# MAGIC ### G2. Add the UC Function Resource Entry
# MAGIC
# MAGIC Locate the `resources` list under `apps.tool_calling_chatbot.resources` in `databricks.yml`. Add the `uc-function-1` entry as the third item in that list, directly after the `app-experiment` entry.
# MAGIC
# MAGIC <div class="code-block-dark" data-language="yaml">
# MAGIC - name: uc-function-1
# MAGIC   uc_securable:
# MAGIC     securable_full_name: ${var.catalog_name}.agent_apps.${var.function_1_name}
# MAGIC     securable_type: FUNCTION
# MAGIC     permission: EXECUTE
# MAGIC </div>
# MAGIC
# MAGIC <p><strong><code>uc_securable</code></strong><br>
# MAGIC This resource type tells DABs to grant the app's service principal a specific privilege on a Unity Catalog securable object. Declaring it here means the permission is managed as part of the bundle lifecycle — it is granted on deploy and can be revoked by removing the entry and redeploying.</p>
# MAGIC
# MAGIC <p><strong><code>securable_full_name: ${var.catalog_name}.agent_apps.${var.function_1_name}</code></strong><br>
# MAGIC The three-part Unity Catalog name of the function: <code>&lt;catalog&gt;.&lt;schema&gt;.&lt;function&gt;</code>. Both <code>${var.catalog_name}</code> and <code>${var.function_1_name}</code> resolve to the variables you defined in G1, keeping the full name parameterized and consistent with the values used in <code>app.yaml</code>.</p>
# MAGIC
# MAGIC <p><strong><code>securable_type: FUNCTION</code></strong><br>
# MAGIC Identifies the object type so DABs knows which Unity Catalog API to call when granting the permission.</p>
# MAGIC
# MAGIC <p><strong><code>permission: EXECUTE</code></strong><br>
# MAGIC Grants the app's service principal the <code>EXECUTE</code> privilege on the function. This is the minimum privilege required for the MCP server to invoke the function on behalf of the agent at runtime.</p>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and paste it into <code>databricks.yml</code> as the third entry under <code>resources:</code> inside the app definition, directly after the <code>app-experiment</code> block.</p>
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
# MAGIC ## H. Redeploy the Updated Agent
# MAGIC
# MAGIC With all three files updated — `agent.py`, `app.yaml`, and `databricks.yml` — redeploy the bundle using the same DABs UI workflow from the previous demo.
# MAGIC
# MAGIC 1. Navigate inside the **simple-tool-calling-agent** folder and click on any file (e.g., **databricks.yml**). Click the rocket icon to open the **Deployments** panel.
# MAGIC 2. Click **Deploy** in the **Deployments** section.
# MAGIC 3. Once validation completes and the deployment summary appears, click **Deploy** again to confirm.
# MAGIC 4. After the deployment succeeds, navigate to your app in **Apps** under **Compute** and click **Deploy** to push the updated source code to the running app.
# MAGIC 5. Wait for the app status to return to **Running**.
# MAGIC
# MAGIC <div style="border-left: 4px solid #1976d2; background: #e3f2fd; padding: 16px 20px; border-radius: 4px; margin: 16px 0;">
# MAGIC <div style="display: flex; align-items: flex-start; gap: 12px;">
# MAGIC <div>
# MAGIC <strong style="color: #0d47a1; font-size: 1.1em;">Bundle Resources and UC Permissions</strong>
# MAGIC <p style="margin: 8px 0 0 0; color: #333;">The bundle now carries the UC function permission as a declared resource in <code>databricks.yml</code> and the required environment variables in <code>app.yaml</code>. No manual Unity Catalog grants or environment configuration are needed outside the bundle.</p>
# MAGIC </div>
# MAGIC </div>
# MAGIC </div>

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ## I. Verify Tool Call Spans in the MLflow Traces UI
# MAGIC
# MAGIC Once the app is running, send a message that requires a data lookup to trigger the `avg_neigh_price` tool.
# MAGIC
# MAGIC 1. Open the app endpoint from the **Apps** page.
# MAGIC 2. Send a message such as: *"What is the average price for listings in the Mission neighborhood?"*
# MAGIC 3. In your Databricks workspace, navigate to **Experiments** and open the experiment named **simple-tool-calling-chatbot-experiment**.
# MAGIC 4. Click the **Traces** tab and open the most recent trace entry.
# MAGIC 5. Expand the root span named **tool_calling_chatbot_run**. You should see child spans for the tool discovery (`tools/list`) and tool execution (`tools/call`) steps produced by the MCP client.
# MAGIC 6. Click a `tools/call` span to inspect its inputs (the arguments passed to `avg_neigh_price`) and outputs (the value returned by the UC function).
# MAGIC
# MAGIC <div style="border-left: 4px solid #1976d2; background: #e3f2fd; padding: 16px 20px; border-radius: 4px; margin: 16px 0;">
# MAGIC <div style="display: flex; align-items: flex-start; gap: 12px;">
# MAGIC <div>
# MAGIC <strong style="color: #0d47a1; font-size: 1.1em;">What You Are Seeing</strong>
# MAGIC <ul style="margin: 12px 0 0 16px; color: #333;">
# MAGIC <li>The <strong>root span</strong> (<code>tool_calling_chatbot_run</code>) captures the full agent invocation — inputs, final output, and total latency.</li>
# MAGIC <li><strong>Child spans</strong> from the Agents SDK runner show each step the LLM took: the initial completion, the tool call decision, the MCP round-trip, and the final synthesis.</li>
# MAGIC <li>The <strong>MCP tool spans</strong> show exactly what arguments were sent to the UC function and what it returned — giving you full visibility into data lookups without any additional instrumentation code.</li>
# MAGIC </ul>
# MAGIC </div>
# MAGIC </div>
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC ## J. Clean Up
# MAGIC
# MAGIC When you are finished with this demo, remove the resources created during deployment.
# MAGIC
# MAGIC 1. Navigate to **Apps** under **Compute** and select the 3 vertical dots next to your app. Select **Delete** to stop and remove the app.
# MAGIC 2. Navigate to **Experiments**, open **simple-tool-calling-chatbot-experiment**, and delete it if you no longer need the trace and run history.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusion
# MAGIC
# MAGIC In this demo, you extended a deployed Databricks App agent with MCP-based tool calling by making targeted changes to all three bundle files — `agent.py`, `app.yaml`, and `databricks.yml` — and redeploying via DABs.
# MAGIC
# MAGIC Key accomplishments:
# MAGIC
# MAGIC - **MCP concepts** — understood the client-server architecture, core primitives (tools, resources, prompts), and the four-step lifecycle (initialize, discover, execute, notify) that governs every MCP connection
# MAGIC - **MCP on Databricks** — identified the three server types (Managed, External, Custom) and when to use each
# MAGIC - **`agent.py` updates** — added `McpServer` and `WorkspaceClient` imports, created an `McpServer.from_uc_function()` instance reading catalog and function names from environment variables, registered it on the `Agent` constructor, and wrapped `Runner.run()` in `async with mcp_server:`
# MAGIC - **`app.yaml` updates** — added `CATALOG_NAME` and `FUNCTION_1_NAME` environment variable entries so the running app can pass those values to `agent.py` at startup
# MAGIC - **`databricks.yml` updates** — added a `variables` block for the catalog and function names, and declared a `uc_securable` resource entry to grant the app's service principal `EXECUTE` permission on the UC function
# MAGIC - **Trace verification** — confirmed that MCP tool call spans appear as children of the root `tool_calling_chatbot_run` span in the MLflow Traces UI
# MAGIC
# MAGIC ### Next Steps
# MAGIC
# MAGIC With tool calling in place, your agent can now answer questions that require real data lookups from Unity Catalog. The next step is to explore exposing multiple UC functions through a single MCP server, or to build a Custom MCP server hosted as its own Databricks App to serve tools that go beyond what Managed MCP provides.

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