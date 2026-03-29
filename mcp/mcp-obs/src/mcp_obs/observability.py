"""Async HTTP client for VictoriaLogs and VictoriaTraces APIs."""

from __future__ import annotations

from typing import Any

import httpx


class VictoriaLogsClient:
    """Client for the VictoriaLogs HTTP API."""

    def __init__(
        self,
        base_url: str,
        *,
        http_client: httpx.AsyncClient | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._owns_client = http_client is None
        self._http_client = http_client or httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
        )

    async def __aenter__(self) -> VictoriaLogsClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._http_client.aclose()

    async def search_logs(
        self,
        query: str,
        limit: int = 100,
    ) -> str:
        """Search logs using LogsQL query."""
        response = await self._http_client.get(
            "/select/logsql/query",
            params={"query": query, "limit": limit},
        )
        response.raise_for_status()
        return response.text

    async def count_errors(
        self,
        hours: int = 1,
    ) -> str:
        """Count errors per service over a time window."""
        query = f"_time:{hours}h severity:ERROR | stats count()"
        response = await self._http_client.get(
            "/select/logsql/query",
            params={"query": query, "limit": 100},
        )
        response.raise_for_status()
        return response.text


class VictoriaTracesClient:
    """Client for the VictoriaTraces HTTP API (Jaeger-compatible)."""

    def __init__(
        self,
        base_url: str,
        *,
        http_client: httpx.AsyncClient | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._owns_client = http_client is None
        self._http_client = http_client or httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
        )

    async def __aenter__(self) -> VictoriaTracesClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._http_client.aclose()

    async def list_traces(
        self,
        service: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """List recent traces for a service."""
        response = await self._http_client.get(
            "/select/jaeger/api/traces",
            params={"service": service, "limit": limit},
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])

    async def get_trace(
        self,
        trace_id: str,
    ) -> dict[str, Any]:
        """Get a specific trace by ID."""
        response = await self._http_client.get(
            f"/select/jaeger/api/traces/{trace_id}",
        )
        response.raise_for_status()
        data = response.json()
        traces = data.get("data", [])
        return traces[0] if traces else {}
