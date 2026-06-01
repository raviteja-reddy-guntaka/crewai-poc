"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  LOCAL LLM AGENT FRAMEWORK                                                  ║
║  CrewAI + Ollama (Gemma4) — Zero Data Leakage                               ║
║                                                                              ║
║  Architecture:                                                               ║
║    User Query → CrewAI Orchestrator → Researcher → Analyst → Reporter      ║
║    Each agent uses a local knowledge_retriever tool backed by Ollama/Gemma4 ║
║                                                                              ║
║  Prerequisites:                                                              ║
║    pip install crewai crewai-tools langchain-community                      ║
║    ollama pull gemma4:latest                                                 ║
║    ollama serve  (runs on localhost:11434 by default)                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import json
from datetime import datetime
from typing import Optional

# ── Framework imports ─────────────────────────────────────────────────────────
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
# from langchain_community.chat_models import ChatOllama
from crewai import LLM
from pydantic import BaseModel, Field

# ── Configuration ─────────────────────────────────────────────────────────────

# All inference stays local. Point this at your Ollama instance.
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL",    "gemma4:latest")

# Initialise the local LLM — no API key, no external calls.
# local_llm = ChatOllama(
#     model=OLLAMA_MODEL,
#     base_url=OLLAMA_BASE_URL,
#     temperature=0.2,        # Low temp = more deterministic, factual output
#     num_predict=2048,
# )
local_llm = LLM(model='ollama/gemma4:latest', base_url='http://localhost:11434', temperature=0.2)

print(f"[CONFIG] LLM  : {OLLAMA_MODEL} @ {OLLAMA_BASE_URL}")
print(f"[CONFIG] Mode : Fully local — zero external API calls\n")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1: SIMULATED LOCAL KNOWLEDGE BASE
# In production this would be a vector DB, Postgres, or a document store —
# all running inside your secure perimeter.
# ══════════════════════════════════════════════════════════════════════════════

KNOWLEDGE_BASE: dict[str, dict] = {
    "project_alpha": {
        "name": "Project Alpha",
        "status": "Active",
        "budget": "$2.4M",
        "team_lead": "Sarah Chen",
        "deadline": "Q3 2025",
        "risk_level": "Medium",
        "description": (
            "Next-generation payment processing microservice. "
            "Targets 99.99% uptime SLA. Currently in integration testing phase. "
            "Key dependency on legacy Oracle DB migration still outstanding."
        ),
        "compliance_flags": ["PCI-DSS", "SOC2"],
    },
    "employee_satisfaction": {
        "name": "Employee Satisfaction Survey — Q2 2025",
        "overall_score": 7.8,
        "response_rate": "84%",
        "top_positives": ["Flexible working", "Engineering culture", "Learning budget"],
        "top_concerns": ["Career path clarity", "Cross-team communication", "On-call rotation burden"],
        "benchmark": "Industry average: 7.2 — we are above benchmark",
    },
    "infrastructure_costs": {
        "name": "Infrastructure Cost Report — H1 2025",
        "total_spend": "$1.82M",
        "cloud_provider": "AWS (60%) / GCP (40%)",
        "yoy_change": "+18% vs H1 2024",
        "top_cost_drivers": ["EC2 compute (45%)", "RDS storage (22%)", "Data transfer (15%)"],
        "optimisation_opportunities": [
            "Reserved instance coverage only 34% — target 70%",
            "3 orphaned RDS instances identified ($4,200/month)",
            "Data egress fees reducible by 60% via regional caching",
        ],
        "projected_savings": "$280K/year if optimisations implemented",
    },
    "security_audit": {
        "name": "Security Audit Summary — June 2025",
        "audit_firm": "Internal Red Team",
        "critical_findings": 0,
        "high_findings": 2,
        "medium_findings": 7,
        "high_details": [
            "Outdated TLS 1.1 still enabled on 3 internal services",
            "Service account with over-provisioned IAM permissions in staging",
        ],
        "remediation_deadline": "2025-07-31",
        "overall_posture": "Satisfactory — no critical issues, remediation on track",
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2: CUSTOM TOOL — LOCAL KNOWLEDGE RETRIEVER
# This is the bridge between the agents and the secure local data store.
# ══════════════════════════════════════════════════════════════════════════════

class KnowledgeQueryInput(BaseModel):
    """Input schema for the knowledge retriever tool."""
    topic: str = Field(
        description=(
            "The specific topic to look up. "
            "Valid topics: 'project_alpha', 'employee_satisfaction', "
            "'infrastructure_costs', 'security_audit'"
        )
    )


class KnowledgeRetrieverTool(BaseTool):
    """
    Retrieves structured data from the local, secure corporate knowledge base.
    All data access is local — nothing is transmitted externally.
    """
    name: str = "knowledge_retriever"
    description: str = (
        "Look up specific corporate data from the secure local knowledge base. "
        "Use this for: project_alpha (project status & risks), "
        "employee_satisfaction (HR survey results), "
        "infrastructure_costs (cloud spend analysis), "
        "security_audit (security posture & findings). "
        "Input must be one of those exact topic keys."
    )
    args_schema: type[BaseModel] = KnowledgeQueryInput

    def _run(self, topic: str) -> str:
        print(f"  [TOOL] knowledge_retriever called → topic='{topic}'")
        data = KNOWLEDGE_BASE.get(topic.strip().lower())

        if not data:
            available = ", ".join(KNOWLEDGE_BASE.keys())
            return (
                f"Topic '{topic}' not found in knowledge base. "
                f"Available topics: {available}"
            )

        # Return structured JSON — agents can reason over this precisely
        result = json.dumps(data, indent=2)
        print(f"  [TOOL] Returned {len(result)} chars from local knowledge base")
        return result

    async def _arun(self, topic: str) -> str:
        return self._run(topic)


knowledge_tool = KnowledgeRetrieverTool()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3: CREW MEMBERS (AGENTS)
# Each agent has a distinct role, goal, and backstory.
# The specialisation mirrors a real human analyst team.
# ══════════════════════════════════════════════════════════════════════════════

researcher = Agent(
    role="Senior Research Analyst",
    goal=(
        "Retrieve all raw, factual data relevant to the query "
        "from the secure local knowledge base. "
        "Do not interpret or summarise — present facts accurately."
    ),
    backstory=(
        "You are a meticulous data analyst with 10 years of experience in "
        "corporate intelligence. You are obsessive about accuracy and always "
        "cite your sources. You have exclusive access to the company's "
        "secure internal knowledge base."
    ),
    tools=[knowledge_tool],
    llm=local_llm,
    verbose=True,
    allow_delegation=False,
    max_iter=4,
)

analyst = Agent(
    role="Strategic Business Analyst",
    goal=(
        "Analyse the raw data provided by the Researcher. "
        "Identify patterns, risks, opportunities, and key insights. "
        "Be specific — quantify impact wherever possible."
    ),
    backstory=(
        "You are a strategic analyst who transforms raw data into actionable "
        "business intelligence. You excel at connecting dots across different "
        "data sources and surfacing non-obvious risks. "
        "You can also query additional data if you spot a gap."
    ),
    tools=[knowledge_tool],
    llm=local_llm,
    verbose=True,
    allow_delegation=False,
    max_iter=4,
)

reporter = Agent(
    role="Executive Report Writer",
    goal=(
        "Compile the researcher's findings and analyst's insights into a "
        "clear, structured executive report. "
        "The report must be actionable, concise, and suitable for senior leadership."
    ),
    backstory=(
        "You are a seasoned communications specialist who writes briefings for "
        "C-suite executives. You are skilled at distilling complex technical and "
        "financial data into clear narratives with concrete recommendations. "
        "You write in plain English, not corporate jargon."
    ),
    tools=[],          # Reporter synthesises — no raw data access needed
    llm=local_llm,
    verbose=True,
    allow_delegation=False,
    max_iter=3,
)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4: TASK DEFINITIONS
# Each task has a clear description, expected output, and assigned agent.
# The sequential process ensures outputs chain correctly.
# ══════════════════════════════════════════════════════════════════════════════

def build_tasks(user_query: str) -> list:
    """
    Dynamically builds the task chain based on the user's query.
    Each task's context feeds into the next — this is the agentic chain.
    """

    task_research = Task(
        description=(
            f"The user has asked: '{user_query}'\n\n"
            "Your job: retrieve ALL relevant raw data from the knowledge base "
            "that could help answer this question. "
            "Use the knowledge_retriever tool for each relevant topic. "
            "Return the raw data in full — do not summarise or interpret. "
            "If multiple topics are relevant, retrieve them all."
        ),
        expected_output=(
            "A complete collection of raw data records from the local knowledge base, "
            "clearly labelled by topic, with all fields intact."
        ),
        agent=researcher,
    )

    task_analysis = Task(
        description=(
            "Using the raw data collected by the Senior Research Analyst, "
            "perform a thorough analysis to answer the user's original question: "
            f"'{user_query}'\n\n"
            "Your analysis must:\n"
            "1. Identify the key facts directly relevant to the question\n"
            "2. Surface any risks, dependencies, or red flags in the data\n"
            "3. Quantify impact where numbers are available\n"
            "4. Note any data gaps that should be flagged to leadership\n"
            "5. Produce 3-5 ranked, specific recommendations"
        ),
        expected_output=(
            "A structured analysis with: key findings, identified risks, "
            "quantified impacts, and 3-5 prioritised recommendations."
        ),
        agent=analyst,
        context=[task_research],     # receives researcher output as context
    )

    task_report = Task(
        description=(
            "Using the analyst's findings, write a polished executive briefing "
            f"that fully answers: '{user_query}'\n\n"
            "Format requirements:\n"
            "- Executive Summary (3-4 sentences)\n"
            "- Key Findings (bullet points, quantified)\n"
            "- Risks & Dependencies (ranked by severity)\n"
            "- Recommended Actions (numbered, owner-assignable)\n"
            "- Confidentiality notice (all data sourced from local systems only)\n\n"
            "Tone: Direct, factual, senior-leadership appropriate. No jargon."
        ),
        expected_output=(
            "A complete, formatted executive briefing in Markdown, "
            "ready to present to senior leadership."
        ),
        agent=reporter,
        context=[task_research, task_analysis],   # full chain context
    )

    return [task_research, task_analysis, task_report]


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5: CREW ASSEMBLY & EXECUTION
# ══════════════════════════════════════════════════════════════════════════════

def run_crew(user_query: str) -> str:
    """
    Assembles the crew, kicks off the sequential workflow,
    and returns the final executive report.
    All processing is local — no data leaves this machine.
    """
    print("\n" + "═" * 70)
    print("  LOCAL LLM AGENT FRAMEWORK — CREW KICKOFF")
    print("═" * 70)
    print(f"  Query  : {user_query}")
    print(f"  Model  : {OLLAMA_MODEL} (local)")
    print(f"  Time   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Agents : Researcher → Analyst → Reporter")
    print("═" * 70 + "\n")

    tasks = build_tasks(user_query)

    crew = Crew(
        agents=[researcher, analyst, reporter],
        tasks=tasks,
        process=Process.sequential,   # Researcher → Analyst → Reporter
        verbose=True,
        memory=False,     # Set True to enable cross-run memory (requires embeddings)
        max_rpm=None,     # No rate limiting — we're running locally
    )

    result = crew.kickoff()

    print("\n" + "═" * 70)
    print("  FINAL REPORT (generated entirely on local infrastructure)")
    print("═" * 70)
    print(result)
    print("═" * 70)

    return result


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6: DEMO ENTRY POINT
# Swap the DEMO_QUERY for different demo scenarios.
# ══════════════════════════════════════════════════════════════════════════════

# ── Demo queries — uncomment the one you want to run ─────────────────────────

DEMO_QUERIES = {
    "A": (
        "Give me a comprehensive health assessment of our engineering organisation. "
        "Cover: active project risks, team morale, infrastructure costs, "
        "and security posture. What are the top 3 things leadership should act on now?"
    ),
    "B": (
        "We are preparing for a board presentation next week. "
        "Summarise our current financial exposure across projects and infrastructure, "
        "and highlight any compliance or security risks that the board should be aware of."
    ),
    "C": (
        "I need a full status report on Project Alpha: "
        "current health, blockers, budget position, and risk assessment. "
        "Also flag any team or security issues that might impact delivery."
    ),
}

# ── Run the demo ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Change "A" to "B" or "C" to demo different scenarios
    selected_query = DEMO_QUERIES["A"]

    final_report = run_crew(selected_query)

    # Optionally save to file
    output_path = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(output_path, "w") as f:
        f.write(f"# Executive Briefing\n\n")
        f.write(f"**Query:** {selected_query}\n\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
        f.write(f"**Infrastructure:** Local (Ollama/{OLLAMA_MODEL}) — zero external calls\n\n")
        f.write("---\n\n")
        f.write(str(final_report))

    print(f"\n[OUTPUT] Report saved to: {output_path}")