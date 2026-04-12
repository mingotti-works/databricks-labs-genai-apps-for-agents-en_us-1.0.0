# Databricks notebook source
# MAGIC %md
# MAGIC ![DB Academy](./Includes/images/db-academy.png)

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC # Demo - Introduction to Deploying Agents on Databricks Apps
# MAGIC
# MAGIC ## Overview
# MAGIC
# MAGIC This demo will walk through how to build a very simple chat-bot application using Declarative Automation Bundles (DABs) along with Databricks Apps from scratch. By the end of this notebook, you will have an agent deployed as an application, which differs greatly from deploying an agent to a model serving endpoint. 
# MAGIC
# MAGIC After registering your model with MLflow and Unity Catalog, Databricks now recommends the next step for deployment to be as an application instead of deploying the agent to a model serving endpoint. Model-Serving-hosted agents will still work, but with Databricks Apps, the lifecycle is closer to deploying agents as code. That is, the app itself is the deployment artifact with MLflow/UC being the governance and observability layers. 
# MAGIC
# MAGIC ## Learning Objectives
# MAGIC By the end of this notebook, you will be able to:
# MAGIC
# MAGIC - Create a simple agent using the OpenAI Agents SDK configured for Databricks
# MAGIC - Build a FastAPI web server to host the agent as a web application
# MAGIC - Configure Declarative Automation Bundles (DABs) for application deployment
# MAGIC - Deploy an agent as a Databricks App using DABs
# MAGIC - Understand the differences between deploying agents as apps versus model serving endpoints
# MAGIC
# MAGIC <div style="
# MAGIC   border-left: 4px solid #f44336;
# MAGIC   background: #ffebee;
# MAGIC   padding: 14px 18px;
# MAGIC   border-radius: 4px;
# MAGIC   margin: 16px 0;
# MAGIC ">
# MAGIC   <strong style="display:block; color:#c62828; margin-bottom:6px; font-size: 1.1em;">Who is the demo for?</strong>
# MAGIC   <div style="color:#333;">
# MAGIC This demo is for those familiar with Agents but are unfamiliar with deploying agents as apps, in particular Databricks Apps. Those with at least 6 months of SWE experience may find this demo very elementary. Users that are already familiar with deploying agents as apps will also find this demo very elementary. 
# MAGIC   </div>
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
# MAGIC <div style="
# MAGIC   border-left: 4px solid #f44336;
# MAGIC   background: #ffebee;
# MAGIC   padding: 14px 18px;
# MAGIC   border-radius: 4px;
# MAGIC   margin: 16px 0;
# MAGIC ">
# MAGIC   <strong style="display:block; color:#c62828; margin-bottom:6px; font-size: 1.1em;">Select Serverless Compute</strong>
# MAGIC   <div style="color:#333;">
# MAGIC
# MAGIC Before starting this notebook, select the required compute environment listed below.
# MAGIC
# MAGIC - **Serverless Compute, Version 5**  
# MAGIC   - [How to select an environment version](https://docs.databricks.com/aws/en/compute/serverless/dependencies#-select-an-environment-version)
# MAGIC
# MAGIC **NOTE:**  This notebook was **developed and tested using Serverless V5**. Other compute options may work but are not guaranteed to behave the same or support all features demonstrated.
# MAGIC   </div>
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
# MAGIC ### B3. Set Up Your Environment
# MAGIC Run the cell below to create your UC and workspace assets. This will populate your folder **simple-agent** with all the necessary files. Notice these files are blank. The goal of this demo is to understand what exactly goes into each one. 

# COMMAND ----------

# MAGIC %run ./Includes/Classroom-Setup-1

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. Define the Agent
# MAGIC
# MAGIC First, let's build an extremely simple agent using Python, which we will store in the file `agent.py`.
# MAGIC
# MAGIC Before building the code, we want to understand various components of the code first.

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### C1. Library and Enivronment Variable Imports
# MAGIC
# MAGIC <div class="code-block-dark" data-language="python">
# MAGIC from agents import Agent, Runner, set_default_openai_api, set_default_openai_client
# MAGIC from databricks_openai import AsyncDatabricksOpenAI
# MAGIC import os
# MAGIC <p>
# MAGIC # Read the endpoint name injected by Databricks Apps
# MAGIC SERVING_ENDPOINT_NAME = os.getenv("SERVING_ENDPOINT_NAME")
# MAGIC </p>
# MAGIC </div>
# MAGIC
# MAGIC <p>These imports provide the core components required to configure and run the agent.</p>
# MAGIC
# MAGIC <p><strong>Key roles:</strong></p>
# MAGIC <ul>
# MAGIC   <li><code>Agent</code> and <code>Runner</code> define and execute the agent workflow.<code>Agent</code> is used to instantiate an AI agent, defining its name, instructions, and the model it uses. <code>Runner</code> provides a mechanism to execute agents asynchronously.</li>
# MAGIC   <li><code>set_default_openai_api</code> and <code>set_default_openai_client</code> configure how model requests are routed.</li>
# MAGIC   <li><code>AsyncDatabricksOpenAI</code> allows the agent to call Databricks-hosted model endpoints using an OpenAI-compatible interface.</li>
# MAGIC   <li> The <code>os</code> module provides a portable way to interact with the operating system: files, directories, environment variables, processes, etc.</li>
# MAGIC </ul>
# MAGIC
# MAGIC <p> We will also be loading the environment variable <code>SERVING_ENDPOINT_NAME</code>, which will be defined later when we configure out Declarative Automation Bundle (DAB).</p>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and paste it into your <code>agent.py</code> file.</p>
# MAGIC
# MAGIC <style id="prism-inline-css">
# MAGIC /* Prism Tomorrow Night theme - inlined */
# MAGIC code[class*="language-"],pre[class*="language-"]{color:#ccc;background:0 0;font-family:Consolas,Monaco,'Andale Mono','Ubuntu Mono',monospace;font-size:1em;text-align:left;white-space:pre;word-spacing:normal;word-break:normal;word-wrap:normal;line-height:1.5;tab-size:4;hyphens:none}pre[class*="language-"]{padding:1em;margin:.5em 0;overflow:auto}:not(pre)>code[class*="language-"],pre[class*="language-"]{background:#2d2d2d}:not(pre)>code[class*="language-"]{padding:.1em;border-radius:.3em;white-space:normal}.token.comment,.token.block-comment,.token.prolog,.token.doctype,.token.cdata{color:#999}.token.punctuation{color:#ccc}.token.tag,.token.attr-name,.token.namespace,.token.deleted{color:#e2777a}.token.function-name{color:#6196cc}.token.boolean,.token.number,.token.function{color:#f08d49}.token.property,.token.class-name,.token.constant,.token.symbol{color:#f8c555}.token.selector,.token.important,.token.atrule,.token.keyword,.token.builtin{color:#cc99cd}.token.string,.token.char,.token.attr-value,.token.regex,.token.variable{color:#7ec699}.token.operator,.token.entity,.token.url{color:#67cdcc}.token.important,.token.bold{font-weight:700}.token.italic{font-style:italic}.token.entity{cursor:help}.token.inserted{color:green}
# MAGIC </style>
# MAGIC
# MAGIC <script>
# MAGIC // Minimal Prism core + Python highlighting
# MAGIC (function(){
# MAGIC function escapeHtml(text) {
# MAGIC     var div = document.createElement('div');
# MAGIC     div.textContent = text;
# MAGIC     return div.innerHTML;
# MAGIC }
# MAGIC
# MAGIC var Prism = window.Prism = {
# MAGIC     languages: {},
# MAGIC     highlight: function(text, grammar) {
# MAGIC         return this.tokenize(text, grammar).map(function(token) {
# MAGIC             if (typeof token === 'string') return escapeHtml(token);
# MAGIC             var type = token.type, content = token.content;
# MAGIC             return '<span class="token ' + type + '">' + escapeHtml(content) + '</span>';
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
# MAGIC         var code = element.textContent;
# MAGIC         var grammar = this.languages.python;
# MAGIC         element.innerHTML = this.highlight(code, grammar);
# MAGIC     }
# MAGIC };
# MAGIC
# MAGIC Prism.languages.python = {
# MAGIC     'comment': /#.*/g,
# MAGIC     'string': /("""[\s\S]*?"""|'''[\s\S]*?'''|"[^"]*"|'[^']*')/g,
# MAGIC     'keyword': /\b(import|from|def|class|return|if|elif|else|for|while|try|except|finally|with|as|pass|break|continue|yield|lambda|async|await|None|True|False)\b/g,
# MAGIC     'function': /\b\w+(?=\()/g,
# MAGIC     'number': /\b\d+\.?\d*\b/g,
# MAGIC     'operator': /[-+*/%=<>!&|^~]+/g,
# MAGIC     'punctuation': /[{}[\];(),.]/g
# MAGIC };
# MAGIC
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
# MAGIC ### C2. Point the OpenAI Agents SDK at Databricks
# MAGIC
# MAGIC <div class="code-block-dark" data-language="python">
# MAGIC # Point the OpenAI Agents SDK at Databricks instead of OpenAI
# MAGIC set_default_openai_client(AsyncDatabricksOpenAI())
# MAGIC set_default_openai_api("chat_completions")
# MAGIC </div>
# MAGIC
# MAGIC <p><code>set_default_openai_client(AsyncDatabricksOpenAI())</code> swaps the underlying client used for agent inference.  
# MAGIC <code>AsyncDatabricksOpenAI</code> is a custom asynchronous client that communicates with Databricks' OpenAI-compatible model endpoints. After this call, all model operations (such as generating completions) are routed through Databricks instead of the public OpenAI service.</p>
# MAGIC
# MAGIC <p><code>set_default_openai_api("chat_completions")</code> instructs the SDK to use the <code>chat_completions</code> API. This is the standard endpoint for conversational LLM workflows and ensures requests are formatted correctly for chat-based interactions.</p>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and paste it into your <code>agent.py</code> file.</p>
# MAGIC
# MAGIC <style id="prism-inline-css">
# MAGIC /* Prism Tomorrow Night theme - inlined */
# MAGIC code[class*="language-"],pre[class*="language-"]{color:#ccc;background:0 0;font-family:Consolas,Monaco,'Andale Mono','Ubuntu Mono',monospace;font-size:1em;text-align:left;white-space:pre;word-spacing:normal;word-break:normal;word-wrap:normal;line-height:1.5;tab-size:4;hyphens:none}pre[class*="language-"]{padding:1em;margin:.5em 0;overflow:auto}:not(pre)>code[class*="language-"],pre[class*="language-"]{background:#2d2d2d}:not(pre)>code[class*="language-"]{padding:.1em;border-radius:.3em;white-space:normal}.token.comment,.token.block-comment,.token.prolog,.token.doctype,.token.cdata{color:#999}.token.punctuation{color:#ccc}.token.tag,.token.attr-name,.token.namespace,.token.deleted{color:#e2777a}.token.function-name{color:#6196cc}.token.boolean,.token.number,.token.function{color:#f08d49}.token.property,.token.class-name,.token.constant,.token.symbol{color:#f8c555}.token.selector,.token.important,.token.atrule,.token.keyword,.token.builtin{color:#cc99cd}.token.string,.token.char,.token.attr-value,.token.regex,.token.variable{color:#7ec699}.token.operator,.token.entity,.token.url{color:#67cdcc}.token.important,.token.bold{font-weight:700}.token.italic{font-style:italic}.token.entity{cursor:help}.token.inserted{color:green}
# MAGIC </style>
# MAGIC
# MAGIC <script>
# MAGIC // Minimal Prism core + Python highlighting
# MAGIC (function(){
# MAGIC function escapeHtml(text) {
# MAGIC     var div = document.createElement('div');
# MAGIC     div.textContent = text;
# MAGIC     return div.innerHTML;
# MAGIC }
# MAGIC
# MAGIC var Prism = window.Prism = {
# MAGIC     languages: {},
# MAGIC     highlight: function(text, grammar) {
# MAGIC         return this.tokenize(text, grammar).map(function(token) {
# MAGIC             if (typeof token === 'string') return escapeHtml(token);
# MAGIC             var type = token.type, content = token.content;
# MAGIC             return '<span class="token ' + type + '">' + escapeHtml(content) + '</span>';
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
# MAGIC         var code = element.textContent;
# MAGIC         var grammar = this.languages.python;
# MAGIC         element.innerHTML = this.highlight(code, grammar);
# MAGIC     }
# MAGIC };
# MAGIC
# MAGIC Prism.languages.python = {
# MAGIC     'comment': /#.*/g,
# MAGIC     'string': /("""[\s\S]*?"""|'''[\s\S]*?'''|"[^"]*"|'[^']*')/g,
# MAGIC     'keyword': /\b(import|from|def|class|return|if|elif|else|for|while|try|except|finally|with|as|pass|break|continue|yield|lambda|async|await|None|True|False)\b/g,
# MAGIC     'function': /\b\w+(?=\()/g,
# MAGIC     'number': /\b\d+\.?\d*\b/g,
# MAGIC     'operator': /[-+*/%=<>!&|^~]+/g,
# MAGIC     'punctuation': /[{}[\];(),.]/g
# MAGIC };
# MAGIC
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
# MAGIC ### C3. Defining the Agent
# MAGIC
# MAGIC <div class="code-block-dark" data-language="python">
# MAGIC # Define the agent
# MAGIC agent = Agent(
# MAGIC     name="Simple Chatbot",
# MAGIC     instructions="You are a helpful assistant. Answer the user's questions clearly and concisely.",
# MAGIC     # Use the serving endpoint name (or fall back to the default FM endpoint)
# MAGIC     model=SERVING_ENDPOINT_NAME,
# MAGIC )
# MAGIC </div>
# MAGIC
# MAGIC <p><code>Agent(...)</code> creates an instance of the OpenAI Agents SDK <code>Agent</code> class.  
# MAGIC This object represents a configured AI assistant that the <code>Runner</code> can execute against user messages.</p>
# MAGIC
# MAGIC <p><strong><code>name="Simple Chatbot"</code></strong><br>
# MAGIC Sets a human-readable name for the agent. This is primarily used for identification in logs, traces, dashboards, or UIs rather than being shown directly to the model.</p>
# MAGIC
# MAGIC <p><strong><code>instructions="You are a helpful assistant..."</code></strong><br>
# MAGIC Defines the agent's system prompt, which controls its behavior. These instructions tell the model to act as a helpful assistant and provide clear, concise responses.  
# MAGIC The Agents SDK inserts this text as the top-level instruction when constructing model requests.</p>
# MAGIC
# MAGIC <p><strong><code>model=SERVING_ENDPOINT_NAME</code></strong><br>
# MAGIC Specifies which foundation model the agent should call.  
# MAGIC Here, the agent uses the model that will be defined by <code>SERVING_ENDPOINT_NAME</code>. Because the default client and API were previously configured to route through Databricks chat-completions, all requests from this agent are sent to the Databricks endpoint rather than the public OpenAI service.</p>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and paste it into your <code>agent.py</code> file.</p>
# MAGIC
# MAGIC <style id="prism-inline-css">
# MAGIC /* Prism Tomorrow Night theme - inlined */
# MAGIC code[class*="language-"],pre[class*="language-"]{color:#ccc;background:0 0;font-family:Consolas,Monaco,'Andale Mono','Ubuntu Mono',monospace;font-size:1em;text-align:left;white-space:pre;word-spacing:normal;word-break:normal;word-wrap:normal;line-height:1.5;tab-size:4;hyphens:none}pre[class*="language-"]{padding:1em;margin:.5em 0;overflow:auto}:not(pre)>code[class*="language-"],pre[class*="language-"]{background:#2d2d2d}:not(pre)>code[class*="language-"]{padding:.1em;border-radius:.3em;white-space:normal}.token.comment,.token.block-comment,.token.prolog,.token.doctype,.token.cdata{color:#999}.token.punctuation{color:#ccc}.token.tag,.token.attr-name,.token.namespace,.token.deleted{color:#e2777a}.token.function-name{color:#6196cc}.token.boolean,.token.number,.token.function{color:#f08d49}.token.property,.token.class-name,.token.constant,.token.symbol{color:#f8c555}.token.selector,.token.important,.token.atrule,.token.keyword,.token.builtin{color:#cc99cd}.token.string,.token.char,.token.attr-value,.token.regex,.token.variable{color:#7ec699}.token.operator,.token.entity,.token.url{color:#67cdcc}.token.important,.token.bold{font-weight:700}.token.italic{font-style:italic}.token.entity{cursor:help}.token.inserted{color:green}
# MAGIC </style>
# MAGIC
# MAGIC <script>
# MAGIC // Minimal Prism core + Python highlighting
# MAGIC (function(){
# MAGIC function escapeHtml(text) {
# MAGIC     var div = document.createElement('div');
# MAGIC     div.textContent = text;
# MAGIC     return div.innerHTML;
# MAGIC }
# MAGIC
# MAGIC var Prism = window.Prism = {
# MAGIC     languages: {},
# MAGIC     highlight: function(text, grammar) {
# MAGIC         return this.tokenize(text, grammar).map(function(token) {
# MAGIC             if (typeof token === 'string') return escapeHtml(token);
# MAGIC             var type = token.type, content = token.content;
# MAGIC             return '<span class="token ' + type + '">' + escapeHtml(content) + '</span>';
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
# MAGIC         var code = element.textContent;
# MAGIC         var grammar = this.languages.python;
# MAGIC         element.innerHTML = this.highlight(code, grammar);
# MAGIC     }
# MAGIC };
# MAGIC
# MAGIC Prism.languages.python = {
# MAGIC     'comment': /#.*/g,
# MAGIC     'string': /("""[\s\S]*?"""|'''[\s\S]*?'''|"[^"]*"|'[^']*')/g,
# MAGIC     'keyword': /\b(import|from|def|class|return|if|elif|else|for|while|try|except|finally|with|as|pass|break|continue|yield|lambda|async|await|None|True|False)\b/g,
# MAGIC     'function': /\b\w+(?=\()/g,
# MAGIC     'number': /\b\d+\.?\d*\b/g,
# MAGIC     'operator': /[-+*/%=<>!&|^~]+/g,
# MAGIC     'punctuation': /[{}[\];(),.]/g
# MAGIC };
# MAGIC
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
# MAGIC ### C4. Running the Agent Asynchronously
# MAGIC
# MAGIC <div class="code-block-dark" data-language="python">
# MAGIC async def run_agent(messages: list[dict]) -> str:
# MAGIC     """Run the agent with a list of messages and return the final reply."""
# MAGIC     result = await Runner.run(agent, messages)
# MAGIC     return result.final_output
# MAGIC </div>
# MAGIC
# MAGIC <p><code>async def run_agent(...)</code> declares an asynchronous function.  
# MAGIC Because it is async, it must be called using <code>await</code> (for example inside <code>asyncio.run()</code> or another async function).</p>
# MAGIC
# MAGIC <p><strong><code>messages: list[dict]</code></strong><br>
# MAGIC This type hint indicates the function expects a list of message dictionaries in standard chat format, such as user and assistant turns.</p>
# MAGIC
# MAGIC <p>Inside the function, <code>Runner.run(agent, messages)</code> executes the configured agent against the provided conversation.  
# MAGIC The result object contains structured outputs from the agent execution, including intermediate steps and the final response. </p>
# MAGIC
# MAGIC <p><code>result.final_output</code> extracts only the final generated reply from the agent, which is then returned as a string.</p>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and paste it into your <code>agent.py</code> file.</p>
# MAGIC
# MAGIC <style id="prism-inline-css">
# MAGIC /* Prism Tomorrow Night theme - inlined */
# MAGIC code[class*="language-"],pre[class*="language-"]{color:#ccc;background:0 0;font-family:Consolas,Monaco,'Andale Mono','Ubuntu Mono',monospace;font-size:1em;text-align:left;white-space:pre;word-spacing:normal;word-break:normal;word-wrap:normal;line-height:1.5;tab-size:4;hyphens:none}pre[class*="language-"]{padding:1em;margin:.5em 0;overflow:auto}:not(pre)>code[class*="language-"],pre[class*="language-"]{background:#2d2d2d}:not(pre)>code[class*="language-"]{padding:.1em;border-radius:.3em;white-space:normal}.token.comment,.token.block-comment,.token.prolog,.token.doctype,.token.cdata{color:#999}.token.punctuation{color:#ccc}.token.tag,.token.attr-name,.token.namespace,.token.deleted{color:#e2777a}.token.function-name{color:#6196cc}.token.boolean,.token.number,.token.function{color:#f08d49}.token.property,.token.class-name,.token.constant,.token.symbol{color:#f8c555}.token.selector,.token.important,.token.atrule,.token.keyword,.token.builtin{color:#cc99cd}.token.string,.token.char,.token.attr-value,.token.regex,.token.variable{color:#7ec699}.token.operator,.token.entity,.token.url{color:#67cdcc}.token.important,.token.bold{font-weight:700}.token.italic{font-style:italic}.token.entity{cursor:help}.token.inserted{color:green}
# MAGIC </style>
# MAGIC
# MAGIC <script>
# MAGIC // Minimal Prism core + Python highlighting
# MAGIC (function(){
# MAGIC function escapeHtml(text) {
# MAGIC     var div = document.createElement('div');
# MAGIC     div.textContent = text;
# MAGIC     return div.innerHTML;
# MAGIC }
# MAGIC
# MAGIC var Prism = window.Prism = {
# MAGIC     languages: {},
# MAGIC     highlight: function(text, grammar) {
# MAGIC         return this.tokenize(text, grammar).map(function(token) {
# MAGIC             if (typeof token === 'string') return escapeHtml(token);
# MAGIC             var type = token.type, content = token.content;
# MAGIC             return '<span class="token ' + type + '">' + escapeHtml(content) + '</span>';
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
# MAGIC         var code = element.textContent;
# MAGIC         var grammar = this.languages.python;
# MAGIC         element.innerHTML = this.highlight(code, grammar);
# MAGIC     }
# MAGIC };
# MAGIC
# MAGIC Prism.languages.python = {
# MAGIC     'comment': /#.*/g,
# MAGIC     'string': /("""[\s\S]*?"""|'''[\s\S]*?'''|"[^"]*"|'[^']*')/g,
# MAGIC     'keyword': /\b(import|from|def|class|return|if|elif|else|for|while|try|except|finally|with|as|pass|break|continue|yield|lambda|async|await|None|True|False)\b/g,
# MAGIC     'function': /\b\w+(?=\()/g,
# MAGIC     'number': /\b\d+\.?\d*\b/g,
# MAGIC     'operator': /[-+*/%=<>!&|^~]+/g,
# MAGIC     'punctuation': /[{}[\];(),.]/g
# MAGIC };
# MAGIC
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
# MAGIC ## D. Create Application Configuration Files
# MAGIC
# MAGIC Next, we need to create several configuration files that define how our agent will be packaged and deployed as a Databricks App. These files work together to create a complete deployment package.

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### D1. Creating the `pyproject.toml` File
# MAGIC
# MAGIC <div class="code-block-dark" data-language="toml">
# MAGIC [project]
# MAGIC name = "simple-chatbot"
# MAGIC version = "0.1.0"
# MAGIC requires-python = ">=3.11"
# MAGIC dependencies = [
# MAGIC     "openai-agents>=0.4.1",
# MAGIC     "databricks-openai>=0.9.0",
# MAGIC     "databricks-sdk",
# MAGIC     "fastapi>=0.115.0",
# MAGIC     "uvicorn>=0.34.0",
# MAGIC     "python-dotenv",
# MAGIC     "uv"
# MAGIC ]
# MAGIC
# MAGIC [build-system]
# MAGIC requires = ["hatchling"]
# MAGIC build-backend = "hatchling.build"
# MAGIC
# MAGIC [tool.hatch.build.targets.wheel]
# MAGIC include = ["agent.py", "server.py"]
# MAGIC
# MAGIC [project.scripts]
# MAGIC start-server = "server:main"
# MAGIC </div>
# MAGIC
# MAGIC <p><code>pyproject.toml</code> is the modern standard configuration file for Python projects.  
# MAGIC It centralizes project metadata, dependencies, packaging settings, and tooling configuration in one place.</p>
# MAGIC
# MAGIC <p><strong><code>[project]</code></strong><br>
# MAGIC Defines core metadata such as the project name, version, Python compatibility, and runtime dependencies required for the chatbot.</p>
# MAGIC
# MAGIC <p><strong><code>dependencies = [...]</code></strong><br>
# MAGIC Lists the packages your application needs to run, including the Agents SDK, Databricks model client, API server framework, and MLflow tracking.</p>
# MAGIC
# MAGIC <p><strong><code>[build-system]</code></strong><br>
# MAGIC Specifies how the package should be built.  
# MAGIC Here we use <code>hatchling</code>, a modern Python build backend.</p>
# MAGIC
# MAGIC <p><strong><code>[tool.hatch.build.targets.wheel]</code></strong><br>
# MAGIC Controls which files are included when your project is packaged into a wheel for installation or deployment.</p>
# MAGIC
# MAGIC <p><strong><code>[project.scripts]</code></strong><br>
# MAGIC Defines command-line entry points installed with the package.  
# MAGIC After installation, running <code>start-server</code> will execute the <code>main()</code> function in <code>server.py</code>.</p>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and paste it into a file named <code>pyproject.toml</code> in your project root.</p>
# MAGIC
# MAGIC <style id="prism-inline-css">
# MAGIC /* Prism Tomorrow Night theme - inlined */
# MAGIC code[class*="language-"],pre[class*="language-"]{color:#ccc;background:0 0;font-family:Consolas,Monaco,'Andale Mono','Ubuntu Mono',monospace;font-size:1em;text-align:left;white-space:pre;word-spacing:normal;word-break:normal;word-wrap:normal;line-height:1.5;tab-size:4;hyphens:none}pre[class*="language-"]{padding:1em;margin:.5em 0;overflow:auto}:not(pre)>code[class*="language-"],pre[class*="language-"]{background:#2d2d2d}:not(pre)>code[class*="language-"]{padding:.1em;border-radius:.3em;white-space:normal}.token.comment,.token.block-comment,.token.prolog,.token.doctype,.token.cdata{color:#999}.token.punctuation{color:#ccc}.token.tag,.token.attr-name,.token.namespace,.token.deleted{color:#e2777a}.token.function-name{color:#6196cc}.token.boolean,.token.number,.token.function{color:#f08d49}.token.property,.token.class-name,.token.constant,.token.symbol{color:#f8c555}.token.selector,.token.important,.token.atrule,.token.keyword,.token.builtin{color:#cc99cd}.token.string,.token.char,.token.attr-value,.token.regex,.token.variable{color:#7ec699}.token.operator,.token.entity,.token.url{color:#67cdcc}.token.important,.token.bold{font-weight:700}.token.italic{font-style:italic}.token.entity{cursor:help}.token.inserted{color:green}
# MAGIC </style>
# MAGIC
# MAGIC <script>
# MAGIC // Minimal Prism core + Python highlighting
# MAGIC (function(){
# MAGIC function escapeHtml(text) {
# MAGIC     var div = document.createElement('div');
# MAGIC     div.textContent = text;
# MAGIC     return div.innerHTML;
# MAGIC }
# MAGIC
# MAGIC var Prism = window.Prism = {
# MAGIC     languages: {},
# MAGIC     highlight: function(text, grammar) {
# MAGIC         return this.tokenize(text, grammar).map(function(token) {
# MAGIC             if (typeof token === 'string') return escapeHtml(token);
# MAGIC             var type = token.type, content = token.content;
# MAGIC             return '<span class="token ' + type + '">' + escapeHtml(content) + '</span>';
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
# MAGIC         var code = element.textContent;
# MAGIC         var grammar = this.languages.python;
# MAGIC         element.innerHTML = this.highlight(code, grammar);
# MAGIC     }
# MAGIC };
# MAGIC
# MAGIC Prism.languages.python = {
# MAGIC     'comment': /#.*/g,
# MAGIC     'string': /("""[\s\S]*?"""|'''[\s\S]*?'''|"[^"]*"|'[^']*')/g,
# MAGIC     'keyword': /\b(import|from|def|class|return|if|elif|else|for|while|try|except|finally|with|as|pass|break|continue|yield|lambda|async|await|None|True|False)\b/g,
# MAGIC     'function': /\b\w+(?=\()/g,
# MAGIC     'number': /\b\d+\.?\d*\b/g,
# MAGIC     'operator': /[-+*/%=<>!&|^~]+/g,
# MAGIC     'punctuation': /[{}[\];(),.]/g
# MAGIC };
# MAGIC
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
# MAGIC ### D2. Create the `app.yaml` File
# MAGIC
# MAGIC <div class="code-block-dark" data-language="yaml">
# MAGIC env:
# MAGIC   - name: SERVING_ENDPOINT_NAME
# MAGIC     valueFrom: serving-endpoint   # resource key you configured
# MAGIC     
# MAGIC command: ["uv", "run", "start-server"]
# MAGIC </div>
# MAGIC <p><code>app.yaml</code> defines how your application is launched inside Databricks.  
# MAGIC It acts as the runtime manifest that tells the platform what command should be executed to start your app.</p>
# MAGIC
# MAGIC <p><strong><code>env: [...]</code></strong><br>
# MAGIC This section injects environment variables into your app's runtime.  
# MAGIC Each entry specifies a <code>name</code> (the variable your code reads) and a <code>valueFrom</code> key that references a resource you configured when setting up the Databricks app — in this case, the model serving endpoint.  
# MAGIC Your <code>agent.py</code> reads <code>SERVING_ENDPOINT_NAME</code> at runtime to know which endpoint to route requests to.</p>
# MAGIC
# MAGIC <p><strong><code>command: [...]</code></strong><br>
# MAGIC This specifies the exact process Databricks should run when the app starts.</p>
# MAGIC
# MAGIC <p>Here, <code>uv run start-server</code> launches the CLI script defined earlier in <code>pyproject.toml</code>.  
# MAGIC Because that script maps to <code>server:main</code>, this command ultimately starts your FastAPI server.</p>
# MAGIC
# MAGIC <p>When a Databricks app is deployed, the platform first installs dependencies, then executes the command defined in <code>app.yaml</code>.  
# MAGIC If no command is provided, Databricks attempts to guess how to start the app based on the detected runtime.</p>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and paste it into your <code>app.yaml</code> file.</p>
# MAGIC
# MAGIC <style id="prism-inline-css">
# MAGIC /* Prism Tomorrow Night theme - inlined */
# MAGIC code[class*="language-"],pre[class*="language-"]{color:#ccc;background:0 0;font-family:Consolas,Monaco,'Andale Mono','Ubuntu Mono',monospace;font-size:1em;text-align:left;white-space:pre;word-spacing:normal;word-break:normal;word-wrap:normal;line-height:1.5;tab-size:4;hyphens:none}pre[class*="language-"]{padding:1em;margin:.5em 0;overflow:auto}:not(pre)>code[class*="language-"],pre[class*="language-"]{background:#2d2d2d}:not(pre)>code[class*="language-"]{padding:.1em;border-radius:.3em;white-space:normal}.token.comment,.token.block-comment,.token.prolog,.token.doctype,.token.cdata{color:#999}.token.punctuation{color:#ccc}.token.tag,.token.attr-name,.token.namespace,.token.deleted{color:#e2777a}.token.function-name{color:#6196cc}.token.boolean,.token.number,.token.function{color:#f08d49}.token.property,.token.class-name,.token.constant,.token.symbol{color:#f8c555}.token.selector,.token.important,.token.atrule,.token.keyword,.token.builtin{color:#cc99cd}.token.string,.token.char,.token.attr-value,.token.regex,.token.variable{color:#7ec699}.token.operator,.token.entity,.token.url{color:#67cdcc}.token.important,.token.bold{font-weight:700}.token.italic{font-style:italic}.token.entity{cursor:help}.token.inserted{color:green}
# MAGIC </style>
# MAGIC
# MAGIC <script>
# MAGIC // Minimal Prism core + Python highlighting
# MAGIC (function(){
# MAGIC function escapeHtml(text) {
# MAGIC     var div = document.createElement('div');
# MAGIC     div.textContent = text;
# MAGIC     return div.innerHTML;
# MAGIC }
# MAGIC
# MAGIC var Prism = window.Prism = {
# MAGIC     languages: {},
# MAGIC     highlight: function(text, grammar) {
# MAGIC         return this.tokenize(text, grammar).map(function(token) {
# MAGIC             if (typeof token === 'string') return escapeHtml(token);
# MAGIC             var type = token.type, content = token.content;
# MAGIC             return '<span class="token ' + type + '">' + escapeHtml(content) + '</span>';
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
# MAGIC         var code = element.textContent;
# MAGIC         var grammar = this.languages.yaml;
# MAGIC         element.innerHTML = this.highlight(code, grammar);
# MAGIC     }
# MAGIC };
# MAGIC
# MAGIC Prism.languages.yaml = {
# MAGIC     'comment': /#.*/g,
# MAGIC     'string': /(["'])(?:\\.|(?!\1)[^\\\r\n])*\1/g,
# MAGIC     'keyword': /\b(true|false|null)\b/g,
# MAGIC     'number': /\b\d+\.?\d*\b/g,
# MAGIC     'punctuation': /[{}[\],]/g,
# MAGIC     'operator': /[:]/g
# MAGIC };
# MAGIC
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
# MAGIC
# MAGIC ### D3. Creating the `databricks.yml` File
# MAGIC
# MAGIC <div class="code-block-dark" data-language="yaml">
# MAGIC bundle:
# MAGIC   name: very_simple_chatbot
# MAGIC
# MAGIC resources:
# MAGIC   apps:
# MAGIC     very_simple_chatbot:
# MAGIC       name: "agent-${workspace.current_user.id}-${bundle.target}-1"
# MAGIC       description: "Simple chatbot agent"
# MAGIC       source_code_path: ./
# MAGIC       # 1) Give the app access to a serving endpoint
# MAGIC       resources:
# MAGIC         - name: serving-endpoint            # resource key visible to the app
# MAGIC           serving_endpoint:
# MAGIC             name: "databricks-gpt-5-2"      # <---- Model Serving endpoint to use
# MAGIC             permission: CAN_QUERY           # or CAN_VIEW / CAN_MANAGE
# MAGIC targets:
# MAGIC   dev:
# MAGIC     mode: development
# MAGIC     default: true
# MAGIC </div>
# MAGIC
# MAGIC <p><code>databricks.yml</code> is the configuration file for a Declarative Automation Bundle (DAB).
# MAGIC It defines how your application is structured, what resources it manages, and where it should be deployed.</p>
# MAGIC
# MAGIC <p><strong><code>bundle</code></strong><br>
# MAGIC The top-level container for the entire bundle.<br>
# MAGIC <code>name: very_simple_chatbot</code> sets the name of the bundle, serving as a logical grouping for all related resources needed to deploy the application.</p>
# MAGIC
# MAGIC <p><strong><code>resources</code></strong><br>
# MAGIC Lists the resources the bundle manages. In this case, it defines an application under the <code>apps</code> subsection and associates it with other Databricks resources.</p>
# MAGIC
# MAGIC <p><strong><code>apps.very_simple_chatbot</code></strong><br>
# MAGIC Defines an application resource within the bundle. Its nested fields control how the app is deployed and what it can access:</p>
# MAGIC
# MAGIC <ul>
# MAGIC   <li><strong><code>name</code></strong> – The workspace name of the app. Using supported bundle substitutions like <code>${bundle.target}</code> allows the name to vary per deployment target. Be careful because there are character limitations.</li>
# MAGIC   <li><strong><code>description</code></strong> – A human-readable description shown in the Databricks UI.</li>
# MAGIC   <li><strong><code>source_code_path</code></strong> – The relative path in your repository that contains the app's source code. Here it is <code>./</code>, meaning the project root.</li>
# MAGIC </ul>
# MAGIC
# MAGIC <p><strong><code>apps.very_simple_chatbot.resources</code></strong><br>
# MAGIC Declares which Databricks resources this app is allowed to use.</p>
# MAGIC
# MAGIC <ul>
# MAGIC   <li>
# MAGIC     <code>- name: serving-endpoint</code><br>
# MAGIC     Defines a resource key called <code>serving-endpoint</code> that the app can reference. This key is also used in <code>app.yaml</code> to bind the <code>SERVING_ENDPOINT_NAME</code> environment variable at runtime.
# MAGIC   </li>
# MAGIC   <li>
# MAGIC     <code>serving_endpoint.name: "databricks-gpt-5-2"</code><br>
# MAGIC     Points this resource key at an existing Mosaic AI Model Serving endpoint named <code>databricks-gpt-5-2</code>. This is how the app "chooses" which model serving endpoint to call.
# MAGIC   </li>
# MAGIC   <li>
# MAGIC     <code>serving_endpoint.permission: CAN_QUERY</code><br>
# MAGIC     Grants the app's service principal permission to send inference requests to that endpoint (read-only, no admin operations).
# MAGIC   </li>
# MAGIC </ul>
# MAGIC
# MAGIC <p><strong><code>targets</code></strong><br>
# MAGIC Defines deployment targets (such as <code>dev</code>, <code>staging</code>, <code>prod</code>). Here, the <code>dev</code> target is marked as <code>mode: development</code> and <code>default: true</code>, meaning local bundle commands will deploy to this target by default.</p>
# MAGIC
# MAGIC <ul>
# MAGIC   <li><strong><code>mode: development</code></strong> — Sets the deployment mode. Development mode allows for faster feedback loops and easier debugging compared to a production deployment.</li>
# MAGIC   <li><strong><code>default: true</code></strong> — Marks this target as the default, so deployments will use the <code>dev</code> configuration unless another target is explicitly specified.</li>
# MAGIC </ul>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and paste it into a file named <code>databricks.yml</code> in your project root.</p>
# MAGIC
# MAGIC <style id="prism-inline-css">
# MAGIC /* Prism Tomorrow Night theme - inlined */
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
# MAGIC
# MAGIC var Prism = window.Prism = {
# MAGIC     languages: {},
# MAGIC     highlight: function(text, grammar) {
# MAGIC         return this.tokenize(text, grammar).map(function(token) {
# MAGIC             if (typeof token === 'string') return escapeHtml(token);
# MAGIC             var type = token.type, content = token.content;
# MAGIC             return '<span class="token ' + type + '">' + escapeHtml(content) + '</span>';
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
# MAGIC         var code = element.textContent;
# MAGIC         var grammar = this.languages.yaml;
# MAGIC         element.innerHTML = this.highlight(code, grammar);
# MAGIC     }
# MAGIC };
# MAGIC
# MAGIC Prism.languages.yaml = {
# MAGIC     'comment': /#.*/g,
# MAGIC     'string': /(["'])(?:\\.|(?!\1)[^\\\r\n])*\1/g,
# MAGIC     'keyword': /\b(true|false|null)\b/g,
# MAGIC     'number': /\b\d+\.?\d*\b/g,
# MAGIC     'punctuation': /[{}[\],]/g,
# MAGIC     'operator': /[:]/g
# MAGIC };
# MAGIC
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
# MAGIC
# MAGIC <div style="
# MAGIC   border-left: 4px solid #1976d2;
# MAGIC   background: #e3f2fd;
# MAGIC   padding: 14px 18px;
# MAGIC   border-radius: 4px;
# MAGIC   margin: 16px 0;
# MAGIC ">
# MAGIC   <strong style="display:block; color:#0d47a1; margin-bottom:6px; font-size: 1.1em;">
# MAGIC     Where can I learn more about DABs?
# MAGIC   </strong>
# MAGIC   <div style="color:#333;">
# MAGIC     This demo does not cover DABs in its entirety. Please see our
# MAGIC     <a href="https://www.databricks.com/training/catalog?search=databricks+asset+bundles" target="_blank" rel="noopener noreferrer">
# MAGIC       additional trainings
# MAGIC     </a>
# MAGIC     on this subject.
# MAGIC   </div>
# MAGIC </div>

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### D4. Creating the `server.py` File
# MAGIC
# MAGIC <div class="code-block-dark" data-language="python">
# MAGIC import uvicorn
# MAGIC from pathlib import Path
# MAGIC
# MAGIC from fastapi import FastAPI
# MAGIC from fastapi.responses import HTMLResponse
# MAGIC from pydantic import BaseModel
# MAGIC
# MAGIC from agent import run_agent
# MAGIC
# MAGIC app = FastAPI()
# MAGIC
# MAGIC CHAT_UI = Path(&#95;&#95;file&#95;&#95;).parent / "chat.html"
# MAGIC
# MAGIC
# MAGIC class ChatRequest(BaseModel):
# MAGIC     input: list[dict]
# MAGIC
# MAGIC
# MAGIC @app.get("/", response_class=HTMLResponse)
# MAGIC async def root():
# MAGIC     return CHAT_UI.read_text()
# MAGIC
# MAGIC
# MAGIC @app.post("/invocations")
# MAGIC async def invocations(request: ChatRequest):
# MAGIC     reply = await run_agent(request.input)
# MAGIC     return {"output": reply}
# MAGIC
# MAGIC
# MAGIC def main():
# MAGIC     uvicorn.run("server:app", host="0.0.0.0", port=8000)
# MAGIC
# MAGIC if &#95;&#95;name&#95;&#95; == "&#95;&#95;main&#95;&#95;":
# MAGIC     main()
# MAGIC </div>
# MAGIC
# MAGIC <p>This file creates a FastAPI web server that hosts a chat UI and connects it to your agent.</p>
# MAGIC
# MAGIC <p><strong>Imports</strong><br>
# MAGIC <code>FastAPI</code> handles routing and request parsing. <code>uvicorn</code> is the ASGI server that runs it.
# MAGIC <code>BaseModel</code> from Pydantic validates incoming request data. <code>run_agent</code> is imported from your <code>agent.py</code>.</p>
# MAGIC
# MAGIC <p><strong><code>CHAT_UI</code></strong><br>
# MAGIC A <code>Path</code> object pointing to <code>chat.html</code>, located in the same directory as <code>server.py</code>. The file is read at request time via <code>.read_text()</code>.</p>
# MAGIC
# MAGIC <p><strong><code>ChatRequest</code></strong><br>
# MAGIC A Pydantic model that validates the request body. It expects <code>input</code> to be a list of message dictionaries representing the conversation history.</p>
# MAGIC
# MAGIC <p><strong><code>GET /</code></strong><br>
# MAGIC Returns the contents of <code>chat.html</code> as an HTML response when a user visits the app in their browser.</p>
# MAGIC
# MAGIC <p><strong><code>POST /invocations</code></strong><br>
# MAGIC Receives the full conversation history, passes it to <code>run_agent()</code>, and returns the agent's reply as <code>{"output": reply}</code>.</p>
# MAGIC
# MAGIC <p><strong><code>main()</code></strong><br>
# MAGIC The entry point that starts the server on <code>0.0.0.0:8000</code>. This is called when you run <code>start-server</code> via the <code>pyproject.toml</code> script entry point, or directly via <code>python server.py</code>.</p>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and paste it into a file named <code>server.py</code> in your project root.</p>
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
# MAGIC
# MAGIC var Prism = window.Prism = {
# MAGIC     languages: {},
# MAGIC     highlight: function(text, grammar) {
# MAGIC         return this.tokenize(text, grammar).map(function(token) {
# MAGIC             if (typeof token === 'string') return escapeHtml(token);
# MAGIC             var type = token.type, content = token.content;
# MAGIC             return '<span class="token ' + type + '">' + escapeHtml(content) + '</span>';
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
# MAGIC         var code = element.textContent;
# MAGIC         var grammar = this.languages.python;
# MAGIC         element.innerHTML = this.highlight(code, grammar);
# MAGIC     }
# MAGIC };
# MAGIC
# MAGIC Prism.languages.python = {
# MAGIC     'comment': /#.*/g,
# MAGIC     'string': /("""[\s\S]*?"""|'''[\s\S]*?'''|"[^"]*"|'[^']*')/g,
# MAGIC     'keyword': /\b(import|from|def|class|return|if|elif|else|for|while|try|except|finally|with|as|pass|break|continue|yield|lambda|async|await|None|True|False)\b/g,
# MAGIC     'function': /\b\w+(?=\()/g,
# MAGIC     'number': /\b\d+\.?\d*\b/g,
# MAGIC     'operator': /[-+*/%=<>!&|^~]+/g,
# MAGIC     'punctuation': /[{}[\];(),.]/g
# MAGIC };
# MAGIC
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
# MAGIC ### D5. Creating the `requirements.txt` File
# MAGIC
# MAGIC <div class="code-block-dark" data-language="python">
# MAGIC uv
# MAGIC </div>
# MAGIC
# MAGIC <p>Databricks Apps do automatically search for a requirements.txt file when deploying. If requirements.txt is present in your app directory, <a href="https://docs.databricks.com/aws/en/dev-tools/databricks-apps/dependencies" target="_blank">Databricks will run <code>pip install -r requirements.txt</code></a> as part of the deployment process, installing all the Python dependencies listed in the file—this applies whether your app is Python-only or a hybrid Python/Node.js app. If you're using Node.js as well and package.json is present, Databricks handles both npm and pip steps; if package.json is not present, only requirements.txt is considered for dependency installation.</p>
# MAGIC
# MAGIC <p>Click <strong>Copy</strong> at the top right of the code block above and paste it into a file named <code>requirements.txt</code> in your project root.</p>
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
# MAGIC
# MAGIC var Prism = window.Prism = {
# MAGIC     languages: {},
# MAGIC     highlight: function(text, grammar) {
# MAGIC         return this.tokenize(text, grammar).map(function(token) {
# MAGIC             if (typeof token === 'string') return escapeHtml(token);
# MAGIC             var type = token.type, content = token.content;
# MAGIC             return '<span class="token ' + type + '">' + escapeHtml(content) + '</span>';
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
# MAGIC         var code = element.textContent;
# MAGIC         var grammar = this.languages.python;
# MAGIC         element.innerHTML = this.highlight(code, grammar);
# MAGIC     }
# MAGIC };
# MAGIC
# MAGIC Prism.languages.python = {
# MAGIC     'comment': /#.*/g,
# MAGIC     'string': /("""[\s\S]*?"""|'''[\s\S]*?'''|"[^"]*"|'[^']*')/g,
# MAGIC     'keyword': /\b(import|from|def|class|return|if|elif|else|for|while|try|except|finally|with|as|pass|break|continue|yield|lambda|async|await|None|True|False)\b/g,
# MAGIC     'function': /\b\w+(?=\()/g,
# MAGIC     'number': /\b\d+\.?\d*\b/g,
# MAGIC     'operator': /[-+*/%=<>!&|^~]+/g,
# MAGIC     'punctuation': /[{}[\];(),.]/g
# MAGIC };
# MAGIC
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
# MAGIC ## E. Deploy the Agent
# MAGIC Next, we will deploy the agent as an application:
# MAGIC 1. Navigate inside the **simple-agent** folder and click on any file (e.g. **databricks.yml**). You will see a small rocket icon appear that is for deployment. Click on it. 
# MAGIC 1. Next, you click on **Deploy** in the **Deployments** section. This DAB has been configured to deploy to **dev** only. You may need to reload the webpage if the **Deploy** button appears grey.
# MAGIC 1. Once the validation clears and you see the app that will be deployed, select **Deploy** again.
# MAGIC
# MAGIC ![dabs-1.png](./Includes/images/dabs-1.png)
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

# MAGIC %md
# MAGIC ## F. Inspect the Agent App
# MAGIC
# MAGIC 1. Under **Bundle resource**, you will see a link to your app called **agent-user_id-dev-1**. You will also see in the console window under **Deployment output** that your deployment has been successful.
# MAGIC
# MAGIC 2. Click on the apps link (**agent-userid-dev-1**) to be taken to the **Apps** section in **Compute**.
# MAGIC
# MAGIC ![dabs-2.png](./Includes/images/dabs-2.png)
# MAGIC
# MAGIC 3. Click **Start** to spin up the compute required for our app.
# MAGIC
# MAGIC 4. After a few moments, the **Start** button will be replaced by **Deploy** and your **App status** will update with an endpoint showing **Unavailable**. Additionally, you will see the model serving details under **App resources**. 
# MAGIC
# MAGIC 5. Click **Deploy** at the top right to deploy the app.
# MAGIC
# MAGIC 6. Copy the full path of the **simple-agent** folder. Navigate to the **simple-agent** folder (located in the same parent folder as this notebook), click the 3 vertical dots, select **Copy URL/path**, and choose **Full path**.
# MAGIC
# MAGIC 7. Paste the full path into the **Create deployment** text box on the **App** page.
# MAGIC
# MAGIC 8. Click **Deploy**. After a few seconds, your app will show a **Running** status.
# MAGIC
# MAGIC 9. Click on the endpoint to open the app. You will see a simple chatbot that you can start chatting with!
# MAGIC
# MAGIC 10. Navigate to **Databricks One** by clicking the waffle at the top right of your workspace next to your user icon. There you will see your application or you can click on **apps** and see it listed there if it doesn't appear on the front page. You can click on it and open the app directly from **Databricks One**. 
# MAGIC
# MAGIC ![dabs-3.png](./Includes/images/dabs-3.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ## G. Clean Up
# MAGIC Navigate back to your application in **Apps** and select the 3 vertical dots and select **Delete** when you are finished with your app. 

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusion
# MAGIC In this demo, you successfully built and deployed a simple chatbot agent as a Databricks App using Declarative Automation Bundles (DABs). This approach demonstrates a fundamentally different deployment pattern compared to traditional model serving endpoints. It's important to note that our agent does not yet have any tools equipped nor do we have an observability layer or governance layer (beyond app-based permissions). 
# MAGIC
# MAGIC Key accomplishments:
# MAGIC
# MAGIC - **Agent Creation**: Built a simple agent using the OpenAI Agents SDK configured to work with Databricks-hosted models
# MAGIC - **Web Application Development**: Created a FastAPI server that hosts both the chat interface and agent logic
# MAGIC - **Infrastructure as Code**: Used DABs to define and manage the deployment configuration declaratively
# MAGIC - **End-to-End Deployment**: Successfully deployed the agent as a running web application accessible via a public endpoint

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
# MAGIC
# MAGIC