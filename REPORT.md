# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

**Q1: "What is the agentic loop?"**

The agentic loop is the fundamental cycle that autonomous AI agents follow:

1. **Perceive** — Gather information from the environment
2. **Think/Reason** — Process information and plan next steps
3. **Act** — Execute actions (call tools, send messages, etc.)
4. **Observe** — Receive feedback from actions
5. **Repeat** — Continue until goal is achieved

**Q2: "What labs are available in our LMS?"**

Without MCP tools, the agent cannot access real LMS data. It would search the filesystem and find directory names like se-toolkit-lab-2 through se-toolkit-lab-8, but these are not real LMS labs — just folder names.

## Task 1B — Agent with LMS tools

**Q1: "What labs are available?"**

The agent successfully called the MCP tool `mcp_lms_lms_labs` and returned real data from the LMS backend:

1. Lab 01 – Products, Architecture & Roles
2. Lab 02 — Run, Fix, and Deploy a Backend Service
3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4. Lab 04 — Testing, Front-end, and AI Agents
5. Lab 05 — Data Pipeline and Analytics Dashboard
6. Lab 06 — Build Your Own Agent
7. Lab 07 — Build a Client with an AI Coding Agent
8. lab-08

**Q2: "Is the LMS backend healthy?"**

The agent can now use `mcp_lms_lms_health` tool to check backend health directly.

MCP tools registered:

- `mcp_lms_lms_health`
- `mcp_lms_lms_labs`
- `mcp_lms_lms_learners`
- `mcp_lms_lms_pass_rates`
- `mcp_lms_lms_timeline`
- `mcp_lms_lms_groups`
- `mcp_lms_lms_top_learners`
- `mcp_lms_lms_completion_rate`
- `mcp_lms_lms_sync_pipeline`

## Task 1C — Skill prompt

**Created skill prompt:** `nanobot/workspace/skills/lms/SKILL.md`

The skill prompt teaches the agent:

- Which LMS MCP tools are available (`lms_health`, `lms_labs`, `lms_pass_rates`, etc.)
- To call `lms_labs` first when the user asks about scores without specifying a lab
- To ask the user which lab they want when multiple labs are available
- To format numeric results as percentages (e.g., "75%" not "0.75")

**Test: "Show me the scores"**

Note: The skill prompt is created but nanobot v0.1.4.post5 does not automatically load skills from the workspace directory. The agent currently uses filesystem tools instead of MCP tools for this query.

When MCP tools are explicitly available (as in Task 1B), the agent successfully calls `mcp_lms_lms_labs` and returns real lab data from the backend.

**Expected behavior with skill loaded:**

1. Agent calls `mcp_lms_lms_labs` to get available labs
2. Agent asks user to choose a lab
3. Agent calls `mcp_lms_lms_pass_rates` with the selected lab
4. Agent formats the result as a percentage

## Task 2A — Deployed agent

<!-- Paste a short nanobot startup log excerpt showing the gateway started inside Docker -->

## Task 2B — Web client

<!-- Screenshot of a conversation with the agent in the Flutter web app -->

## Task 3A — Structured logging

<!-- Paste happy-path and error-path log excerpts, VictoriaLogs query screenshot -->

## Task 3B — Traces

<!-- Screenshots: healthy trace span hierarchy, error trace -->

## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->

## Task 3A — Structured logging

**Happy path log excerpt (PostgreSQL running):**
```
request_started → auth_success → db_query → request_completed (200 OK)
trace_id=0b29fc9941e2df1e284fb1e9361761bb
```

**Error path log excerpt (PostgreSQL stopped):**
```
request_started → auth_success → db_query (ERROR) → items_list_failed_as_not_found → request_completed (404)
trace_id=51c80516ec9e21a1889cea2b3b13036b
```

**VictoriaLogs UI:** Available at http://localhost:42002/utils/victorialogs/select/vmui

---

## Task 3B — Traces

**VictoriaTraces UI:** Available at http://localhost:42002/utils/victoriatraces

Traces include span hierarchy showing:
- request_started
- auth_success  
- db_query
- request_completed

---

## Task 3C — Observability MCP tools

**Created MCP tools:**
- `logs_search` — Search VictoriaLogs by LogsQL query
- `logs_error_count` — Count errors per service
- `traces_list` — List recent traces for a service
- `traces_get` — Fetch a specific trace by ID

**Test: "Any errors in the last hour?"**

Normal conditions: Agent should report no errors or show error count from logs.

Failure conditions (PostgreSQL stopped): Agent should report database connection errors from VictoriaLogs.

**Files created:**
- `mcp/mcp-obs/src/mcp_obs/server.py` — MCP observability server
- `nanobot/workspace/skills/observability/SKILL.md` — Observability skill prompt
