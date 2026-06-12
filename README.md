# Local LLM Agent Workflow Demo using CrewAI

A proof-of-concept project demonstrating how local LLMs can be used with multi-agent orchestration to automate structured engineering and leadership workflows without sending data to external AI APIs.

This project uses:

* **CrewAI** for multi-agent workflow orchestration
* **Ollama** for locally hosted LLM inference
* **Gemma / local open-source models** as the reasoning engine
* **Python tools** as secure local data access bridges
* **Markdown reports and local notes** as persistent workflow artifacts

The goal of this project is to explore how AI can support day-to-day engineering work beyond code completion. While tools like GitHub Copilot are useful for developer productivity, this demo focuses on a different layer: using local LLMs to coordinate multi-step reasoning workflows over private internal data.

---

## Why This Project Exists

Many enterprise AI productivity discussions focus on code generation and autocomplete. However, engineering teams also spend significant time on:

* Status reporting
* Release readiness reviews
* Risk assessment
* Incident summaries
* Infrastructure cost analysis
* Security and compliance follow-ups
* Leadership briefings
* Cross-team coordination

This project demonstrates how a local agentic workflow can assist with those tasks while keeping data inside the local environment.

The core idea is:

```
Use local LLMs not just as chatbots, but as secure workflow engines that can coordinate specialized agents, call approved tools, and produce structured work artifacts.
```

---

## Demo Scenario

The demo simulates an engineering leadership analysis workflow.

A user asks a high-level question such as:

```
Give me a comprehensive health assessment of our engineering organization. Cover active project risks, team morale, infrastructure costs, and security posture. What are the top things leadership should act on now?
```

The system then runs a multi-agent workflow:

```text
User Query
   ↓
CrewAI Orchestrator
   ↓
Researcher Agent
   ↓
Analyst Agent
   ↓
Reporter Agent
   ↓
Local Markdown Report + Notes
```

---

## Agent Workflow

### 1. Researcher Agent

The Researcher retrieves factual information from a local knowledge base.

Responsibilities:

* Query local data sources
* Retrieve raw facts
* Avoid summarizing too early
* Preserve source structure

In the demo, this knowledge base is simulated as a local Python dictionary. In a production version, this could be replaced with:

* Internal wiki exports
* Postgres
* ChromaDB or another vector database
* SharePoint or Confluence documents
* Build and deployment metadata
* Incident management systems
* Security audit records

---

### 2. Analyst Agent

The Analyst takes the retrieved data and identifies:

* Risks
* Dependencies
* Trends
* Cost opportunities
* Security concerns
* Delivery blockers
* Leadership-level recommendations

This agent connects information across different data domains instead of treating each source independently.

---

### 3. Reporter Agent

The Reporter converts the analysis into a clear executive briefing.

The output is formatted as a Markdown report with sections such as:

* Executive Summary
* Key Findings
* Risks and Dependencies
* Recommended Actions
* Confidentiality Notice

---

## Local Knowledge Retriever Tool

The project includes a custom CrewAI tool called `knowledge_retriever`.

This tool acts as the bridge between the agents and the local data store.

In the current demo, it supports topics such as:

* `project_alpha`
* `employee_satisfaction`
* `infrastructure_costs`
* `security_audit`

The important design pattern is that agents do not directly access arbitrary files or systems. They use an approved tool interface.

This makes the workflow easier to secure, audit, and extend.

---

## Local-First Design

This project is intentionally designed around local execution.

The LLM is served through Ollama on:

```text
http://localhost:11434
```

No OpenAI, Anthropic, or external model API is required for the base demo.

Benefits of this approach:

* Keeps prompts and retrieved data local
* Avoids external API dependencies
* Reduces per-token cost concerns
* Supports experimentation with open-source models
* Creates a safer path for internal enterprise workflows

---

## Multi-Step Workflow Mode

The expanded demo can run multiple analysis tasks automatically.

Instead of running one prompt, the script can run a sequence of leadership-style questions and generate local artifacts after each run.

Example output structure:

```text
local_agent_workspace/
  reports/
    run_01_report.md
    run_02_report.md
    run_03_report.md
  notes/
    cumulative_notes.md
  state/
    latest_state.json
  RUN_INDEX.md
```

This demonstrates a simple local memory/artifact pattern:

* Each run produces a report
* Notes are updated over time
* A run index tracks what happened
* State can be inspected after the workflow finishes

---

## Example Use Cases

This pattern could be extended for:

* Engineering weekly status reports
* Release readiness reviews
* Incident postmortem generation
* Security audit summaries
* Infrastructure cost reviews
* Internal documentation Q&A
* Dependency risk analysis
* Sprint planning support
* Leadership briefing preparation

---

## Requirements

* Python 3.10+
* Ollama installed locally
* A local Ollama model pulled and available
* CrewAI Python dependencies

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install crewai crewai-tools pydantic
```

If your version uses additional packages, install them from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Install Ollama

Download and install Ollama from:

```text
https://ollama.com
```

### 5. Pull a local model

Example:

```bash
ollama pull gemma3:4b
```

Other options:

```bash
ollama pull llama3.1:8b
ollama pull mistral
```

### 6. Confirm Ollama is running

```bash
ollama list
```

Optional test:

```bash
ollama run gemma3:4b
```

### 7. Update the model name in the Python script

Make sure the model name in the script matches exactly what appears in:

```bash
ollama list
```

Example:

```python
local_llm = LLM(
    model="ollama/gemma3:4b",
    base_url="http://localhost:11434",
    temperature=0.2
)
```

### 8. Run the demo

```bash
python local_llm_agent_15_run_demo.py
```

For a shorter test run:

```bash
DEMO_RUN_COUNT=3 python local_llm_agent_15_run_demo.py
```

On Windows Command Prompt:

```cmd
set DEMO_RUN_COUNT=3
python local_llm_agent_15_run_demo.py
```

On Windows PowerShell:

```powershell
$env:DEMO_RUN_COUNT="3"
python local_llm_agent_15_run_demo.py
```

---

## Important Note About Model Names

The model name in the Python script must match the model installed in Ollama.

For example, if this command shows:

```bash
ollama list
```

```text
gemma3:4b
```

Then the CrewAI LLM config should use:

```python
model="ollama/gemma3:4b"
```

If you use a custom model such as `gemma4:latest`, make sure it exists locally in Ollama before running the script.

---

## Current Limitations

This is a proof of concept, not a production system.

Current limitations:

* Knowledge base is simulated
* No user authentication or authorization layer
* No role-based data access
* No production observability
* No formal model evaluation
* No prompt injection hardening
* No long-term database-backed memory

---

## Future Improvements

Planned extensions:

* Replace simulated knowledge base with real internal data sources
* Add vector search over local documents
* Add structured logging for each agent step
* Add evaluation tests for report quality
* Add model benchmarking across Gemma, Llama, Mistral, and other local models
* Add role-based access controls
* Add a lightweight UI for running workflows
* Add Docker-based local deployment
* Add support for exporting reports to PDF or Slack-ready summaries

---

## Project Takeaway

GitHub Copilot helps developers write code faster.

This project explores the next layer of AI productivity:

```
Local agents that can reason across internal context, use approved tools, coordinate multi-step workflows, and generate useful work artifacts without sending private data outside the environment.
```
