#!/usr/bin/env python3
"""MCP Server for VictoriaLogs and VictoriaTraces"""

import asyncio
import httpx
from datetime import datetime, timedelta
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

VICTORIALOGS_URL = "http://victorialogs:9428"
VICTORIATRACES_URL = "http://victoriatraces:10428"

server = Server("mcp-observability")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="logs_search",
            description="Search logs in VictoriaLogs by query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "LogsQL query"},
                    "limit": {"type": "integer", "default": 100}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="logs_error_count",
            description="Count errors per service",
            inputSchema={
                "type": "object",
                "properties": {
                    "hours": {"type": "integer", "default": 1}
                }
            }
        ),
        Tool(
            name="traces_list",
            description="List recent traces for a service",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {"type": "string"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["service"]
            }
        ),
        Tool(
            name="traces_get",
            description="Get a trace by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "trace_id": {"type": "string"}
                },
                "required": ["trace_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    async with httpx.AsyncClient(timeout=30.0) as client:
        if name == "logs_search":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 100)
            url = f"{VICTORIALOGS_URL}/select/logsql/query"
            resp = await client.get(url, params={"query": query, "limit": limit})
            return [TextContent(type="text", text=f"Logs:\n{resp.text[:2000]}")]
        
        elif name == "logs_error_count":
            hours = arguments.get("hours", 1)
            url = f"{VICTORIALOGS_URL}/select/logsql/query"
            resp = await client.get(url, params={"query": "level:error | stats count() by service", "limit": 100})
            return [TextContent(type="text", text=f"Errors (last {hours}h):\n{resp.text[:1000]}")]
        
        elif name == "traces_list":
            service = arguments.get("service", "")
            limit = arguments.get("limit", 10)
            url = f"{VICTORIATRACES_URL}/jaeger/api/traces"
            resp = await client.get(url, params={"service": service, "limit": limit})
            data = resp.json()
            traces = data.get("data", [])
            summary = f"Found {len(traces)} traces for '{service}':\n"
            for t in traces[:5]:
                summary += f"  - {t.get('traceID', '')[:16]}... ({len(t.get('spans', []))} spans)\n"
            return [TextContent(type="text", text=summary)]
        
        elif name == "traces_get":
            trace_id = arguments.get("trace_id", "")
            url = f"{VICTORIATRACES_URL}/jaeger/api/traces/{trace_id}"
            resp = await client.get(url)
            data = resp.json()
            trace = data.get("data", [{}])[0] if data.get("data") else {}
            spans = trace.get("spans", [])
            summary = f"Trace {trace_id}:\n  Spans: {len(spans)}\n"
            for s in spans[:10]:
                summary += f"  - {s.get('operationName', '?')}: {s.get('duration', 0)/1000:.1f}ms\n"
            return [TextContent(type="text", text=summary)]
        
        else:
            raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (rs, ws):
        await server.run(rs, ws)

if __name__ == "__main__":
    asyncio.run(main())
