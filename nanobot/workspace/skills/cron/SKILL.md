---
name: cron
description: Use the built-in cron tool to schedule recurring jobs in the current chat
always: true
---

# Cron Skill

You have a built-in `cron` tool to schedule recurring jobs in the current chat session.

## Available Actions

Use the `cron` tool with these actions:

### Add a job
```json
{
  "action": "add",
  "schedule": "*/2 * * * *",
  "command": "your command or question to run"
}
```

### List jobs
```json
{
  "action": "list"
}
```

### Remove a job
```json
{
  "action": "remove",
  "id": "job-id-from-list"
}
```

## Schedule Format

Cron uses standard cron syntax:
- `*/2 * * * *` — every 2 minutes
- `*/5 * * * *` — every 5 minutes
- `0 * * * *` — every hour at minute 0
- `0 0 * * *` — every day at midnight
- `0 9 * * 1-5` — every weekday at 9 AM

Fields: `minute hour day-of-month month day-of-week`

## When to Use

Use cron for **recurring health checks** or **periodic monitoring** in the current chat session.

Example: User asks for a health check every 2 minutes:
```json
{
  "action": "add",
  "schedule": "*/2 * * * *",
  "command": "Check for backend errors in the last 2 minutes using logs_error_count(minutes=2). If errors found, fetch a trace and summarize. If no errors, say 'System looks healthy'."
}
```

## Important Notes

- Jobs are tied to the current chat session
- Jobs persist in `workspace/cron/jobs.json`
- When listing jobs, show the user their scheduled jobs with IDs
- To remove a job, use the exact ID from the list response
