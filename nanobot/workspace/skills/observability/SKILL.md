---
name: observability
description: Use observability tools to query logs and traces
always: true
---

# Observability Skill

You have access to observability tools for VictoriaLogs and VictoriaTraces.

## Available Tools

**Log tools:**
- `logs_search` — Search logs by LogsQL query
- `logs_error_count` — Count errors per service

**Trace tools:**
- `traces_list` — List recent traces for a service
- `traces_get` — Get a specific trace by ID

## Strategy

### When user asks about errors or problems:

1. **Search logs first** — Use `logs_search` with query like `level:error` or `service="backend"`
2. **Check error count** — Use `logs_error_count` to see which services have errors
3. **Find trace ID in logs** — Look for `trace_id=xxx` in log entries
4. **Fetch the trace** — Use `traces_get` with the trace ID to see full request flow
5. **Summarize** — Explain what went wrong concisely

### Example queries:

- "Any errors in the last hour?" → `logs_error_count(hours=1)`
- "Show backend errors" → `logs_search(query='level:error AND service="backend"')`
- "What happened in trace abc123?" → `traces_get(trace_id="abc123")`

### Response style:

- Be concise — summarize findings, don't dump raw JSON
- Highlight key errors and their causes
- If you find a trace ID, offer to fetch the full trace
- Mention which service is affected
