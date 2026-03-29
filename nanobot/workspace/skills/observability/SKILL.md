---
name: observability
description: Use observability tools to investigate failures and check system health
always: true
---

# Observability Skill

You have access to observability tools for VictoriaLogs and VictoriaTraces.

## Available Tools

**Log tools:**
- `logs_search` — Search logs by LogsQL query (e.g., `level:error`, `service="backend"`)
- `logs_error_count` — Count errors per service in a time window

**Trace tools:**
- `traces_list` — List recent traces for a service
- `traces_get` — Get a specific trace by ID to see full request flow

## Investigation Strategy

### When user asks "What went wrong?" or "Check system health":

Follow this investigation flow **in order**:

1. **Check error count first** — Call `logs_error_count(minutes=5)` to see which services have recent errors
2. **Search error logs** — Call `logs_search` with `level:error` scoped to the failing service (e.g., `service="backend"`)
3. **Extract trace ID** — From the error logs, find `trace_id=xxx` in the log entry
4. **Fetch the trace** — Call `traces_get(trace_id="...")` to see the full request flow and span hierarchy
5. **Synthesize findings** — Combine log evidence and trace evidence into a concise summary

### Response format:

When presenting findings, structure your answer:

```
**Summary:** One-sentence root cause

**Log evidence:**
- Service X logged error Y at time T
- Key error message: "..."

**Trace evidence:**
- Trace shows request failed at span Z
- Duration: Xms (abnormally high/timeout)

**Root cause:** Database connection failed / service unavailable / etc.
```

### Example investigation flow:

User: "What went wrong?"

1. `logs_error_count(minutes=5)` → backend has 15 errors
2. `logs_search(query='level:error AND service="backend"', limit=10)` → finds "db_query failed: connection refused"
3. Extract `trace_id=51c80516...` from log
4. `traces_get(trace_id="51c80516...")` → shows spans: request_started → auth_success → db_query (FAILED)
5. **Response:** "The backend failed to connect to PostgreSQL. Logs show 'connection refused' errors. Trace 51c80516 shows the db_query span failed after 30s timeout."

### Key patterns to recognize:

- `db_query` + `error: connection refused` → PostgreSQL is down
- `db_query` + `error: timeout` → Database overload or network issue
- `items_list_failed_as_not_found` → Backend caught an exception but returned 404 (buggy error handling)
- `request_started` without `request_completed` → Request crashed mid-flight

### Response style:

- **Be concise** — summarize findings, don't dump raw JSON
- **Cite both sources** — mention what logs show AND what traces confirm
- **Name the root cause** — database down, timeout, exception handler bug, etc.
- **Highlight discrepancies** — e.g., "Logs show DB failure but response was 404 — error handler is masking the real issue"
