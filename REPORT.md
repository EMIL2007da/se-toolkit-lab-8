# Task 4 — Diagnose a Failure and Make the Agent Proactive

## Task 4A — Multi-step investigation

**User Query:** What went wrong?

**Agent Response:**
System Investigation Result:

PostgreSQL is stopped

Database connection refused

Check with: docker compose start postgres

Trace ID: trace-20260329-001

**Status:** ✅ PASS

## Task 4B — Proactive health check

**Cron job created with 2-minute interval**

**Automatic health report:**
⚠️ Health Alert: PostgreSQL is stopped! Database operations will fail.

**After starting PostgreSQL:**
✅ System looks healthy - PostgreSQL is running

**Status:** ✅ PASS

## Task 4C — Bug fix and recovery

**Root Cause:** WebSocket handler didn't support cron jobs

**Fix:** Enhanced ws_server.py with cron job management

**Status:** ✅ PASS - Bug fixed, system recovered

