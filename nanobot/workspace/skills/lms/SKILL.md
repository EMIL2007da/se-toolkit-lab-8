---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Skill

You have access to LMS MCP tools. Use them to answer questions about labs and analytics.

## Available Tools

- `mcp_lms_lms_health` — Check LMS backend health
- `mcp_lms_lms_labs` — Get all available labs
- `mcp_lms_lms_pass_rates` — Get pass rate for a lab
- `mcp_lms_lms_learners` — Get learners for a lab
- `mcp_lms_lms_timeline` — Get timeline for a lab
- `mcp_lms_lms_groups` — Get groups for a lab
- `mcp_lms_lms_top_learners` — Get top learners for a lab
- `mcp_lms_lms_completion_rate` — Get completion rate for a lab
- `mcp_lms_lms_sync_pipeline` — Trigger LMS sync

## Strategy

When user asks about scores, pass rates, or analytics without specifying a lab:
1. Call `mcp_lms_lms_labs` first
2. Ask user to choose a lab
3. Call the appropriate tool with the lab parameter

Format percentages nicely (e.g., "75%" not "0.75").
