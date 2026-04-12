# Databricks notebook source
# MAGIC %md
# MAGIC # Deploying Agents on Databricks Apps
# MAGIC
# MAGIC ## Overview
# MAGIC This course contains training materials for using Databricks Apps with AI Agents. This space is evolving and The Curriculum Team will continue to build content in this space. 
# MAGIC
# MAGIC ## Terminal Objectives
# MAGIC - Introduction to Deploying Agents on Databricks Apps
# MAGIC - Integrating App-Based Agents with MLflow
# MAGIC - Attaching Tools to an App-Based Agent

# COMMAND ----------

# MAGIC %md
# MAGIC ## A. Prerequisites
# MAGIC
# MAGIC The following are either recommended or required.
# MAGIC
# MAGIC - A **Databricks** workspace  
# MAGIC - Write access to a catalog you own in Unity Catalog  
# MAGIC - Familiarity with Databricks Apps
# MAGIC - Familiarity with AI agents
# MAGIC - Familiarity with Declarative Automation Bundles (formerly known as Databricks Asset Bundles) or DABs
# MAGIC - Git folder setup

# COMMAND ----------

# MAGIC %md
# MAGIC ## B. Workspace Setup Information
# MAGIC

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### B1. Databricks Provided Vocareum Workspace (Recommended)
# MAGIC
# MAGIC <div style="
# MAGIC   border-left: 4px solid #1976d2;
# MAGIC   background: #e3f2fd;
# MAGIC   padding: 14px 18px;
# MAGIC   border-radius: 4px;
# MAGIC   margin: 16px 0;
# MAGIC ">
# MAGIC   <div style="color:#333;">
# MAGIC
# MAGIC - If you are running this notebook in a <strong>Databricks Academy provided Vocareum workspace</strong>, your Unity Catalog catalog is already created for you.
# MAGIC
# MAGIC - Your catalog name matches your Vocareum username and looks like: <strong>labuser12345</strong> (series of unique numbers)
# MAGIC
# MAGIC - If a <strong>Marketplace</strong> dataset is required, the share is already installed and available in the workspace.
# MAGIC
# MAGIC   </div>
# MAGIC </div>

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### B2. Databricks Free Edition (*as is*)
# MAGIC
# MAGIC ##### Databricks Free Edition may work for this course, but it is provided **as is** and support is not guaranteed.  
# MAGIC
# MAGIC Some features may not be available depending on the capabilities of Databricks Free Edition.
# MAGIC
# MAGIC Please read below to setup your environment for Databricks Free Edition
# MAGIC
# MAGIC <div style="
# MAGIC   border-left: 4px solid #1976d2;
# MAGIC   background: #e3f2fd;
# MAGIC   padding: 14px 18px;
# MAGIC   border-radius: 4px;
# MAGIC   margin: 16px 0;
# MAGIC ">
# MAGIC <div style="color:#333;">
# MAGIC
# MAGIC #### Catalog Information
# MAGIC
# MAGIC - If you are running this notebook in your own Databricks workspace or Databricks Free Edition, the setup will <strong>create a Unity Catalog catalog and schema for you</strong>. 
# MAGIC
# MAGIC - The <strong>Create Catalog</strong> permission is required.
# MAGIC
# MAGIC - The catalog name is derived from your Databricks username and follows this pattern: <strong>labuser_username</strong>
# MAGIC
# MAGIC <br></br>
# MAGIC #### Access Marketplace Data
# MAGIC
# MAGIC If you are running this in Databricks Free Edition, complete the steps below to obtain the Marketplace dataset required for this lab.
# MAGIC
# MAGIC If you already have access to this share, simply set the variable below to the name of your existing catalog.
# MAGIC
# MAGIC 1. Open <strong>Databricks Marketplace</strong> in a new tab.
# MAGIC
# MAGIC 2. Search for <code>Airbnb Sample Data</code>.
# MAGIC
# MAGIC 3. Select the tile titled <strong>Airbnb Sample Data (Databricks provided)</strong>.
# MAGIC
# MAGIC 4. Click <strong>Get instant access</strong>.
# MAGIC
# MAGIC 5. Enter a <strong>unique catalog name</strong> for your share to avoid duplicate catalog errors in shared workspaces.  
# MAGIC    Example: <code>dbacademy_retail_yourname</code>.
# MAGIC
# MAGIC 6. Review and accept the terms, then click <strong>Get instant access</strong>.
# MAGIC
# MAGIC 7. Update the variable in the necessary notebooks when referencing your **Marketplace catalog**.
# MAGIC
# MAGIC </div>
# MAGIC </div>
# MAGIC
# MAGIC <div style="
# MAGIC   border-left: 4px solid #f44336;
# MAGIC   background: #ffebee;
# MAGIC   padding: 14px 18px;
# MAGIC   border-radius: 4px;
# MAGIC   margin: 16px 0;
# MAGIC ">
# MAGIC <strong style="display:block; color:#c62828; margin-bottom:6px; font-size: 1.1em;">Do Not Run in Production Environments</strong>
# MAGIC
# MAGIC <div style="color:#333;">
# MAGIC <ul>
# MAGIC <li>Only run this course in <strong>development or sandbox workspaces</strong>.</li>
# MAGIC <li>Do not run in production environments. The setup scripts creates catalogs, schemas and pipelines in your workspace.</li>
# MAGIC </ul>
# MAGIC </div>
# MAGIC </div>

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC # ADDITIONAL REQUIRED SETUP
# MAGIC In order to have the set of demos properly run in your workspace, you must have a Git Folder in your workspace. It can be any git folder, but this base folder **genai-apps-for-agents** must be in one. Bundles themselves are not limited to Git folders overall—you can still build and deploy bundles from a local dev environment with the Databricks CLI without using the workspace UI.
# MAGIC
# MAGIC ### Helpful Links
# MAGIC - [Installation requirements for bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/workspace#what-are-the-installation-requirements-of-bundles-in-the-workspace)
# MAGIC - [Create and manage git folders](https://docs.databricks.com/aws/en/repos/git-operations-with-repos)
# MAGIC - [Add Git credentials in Databricks](https://docs.databricks.com/aws/en/repos/repos-setup#add-git-credentials)
# MAGIC
# MAGIC Every notebook will have the following message to help remind you that you must be in a git folder in order for the app deployment to work as intended. 
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
# MAGIC &copy; <span id="dbx-year"></span> Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="_blank">Apache Software Foundation</a>.<br/><br/><a href="https://databricks.com/privacy-policy" target="_blank">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use" target="_blank">Terms of Use</a> | <a href="https://help.databricks.com/" target="_blank">Support</a>
# MAGIC <script>
# MAGIC   document.getElementById("dbx-year").textContent = new Date().getFullYear();
# MAGIC </script>
# MAGIC