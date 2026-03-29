#!/usr/bin/env python3
"""
Entrypoint for nanobot Docker container.

Resolves environment variables into the nanobot config at runtime,
then launches `nanobot gateway`.
"""

import json
import os
import sys
from pathlib import Path


def main():
    # Paths
    config_dir = Path(__file__).parent
    config_path = config_dir / "config.json"
    resolved_path = config_dir / "config.resolved.json"
    workspace_dir = config_dir / "workspace"

    # Read base config
    with open(config_path) as f:
        config = json.load(f)

    # Override provider settings from env vars
    llm_api_key = os.environ.get("LLM_API_KEY")
    llm_api_base = os.environ.get("LLM_API_BASE_URL")
    llm_api_model = os.environ.get("LLM_API_MODEL")

    if llm_api_key:
        config["providers"]["openai"]["apiKey"] = llm_api_key
    if llm_api_base:
        config["providers"]["openai"]["apiBase"] = llm_api_base
    if llm_api_model:
        config["agents"]["defaults"]["model"] = llm_api_model

    # Override gateway settings from env vars
    gateway_host = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS")
    gateway_port = os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT")

    if gateway_host:
        config.setdefault("gateway", {})["host"] = gateway_host
    if gateway_port:
        config.setdefault("gateway", {})["port"] = int(gateway_port)

    # Override webchat channel settings from env vars
    webchat_host = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS")
    webchat_port = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT")
    nanobot_access_key = os.environ.get("NANOBOT_ACCESS_KEY")

    if "channels" not in config:
        config["channels"] = {}

    if "webchat" not in config["channels"]:
        config["channels"]["webchat"] = {}

    webchat_config = config["channels"]["webchat"]
    webchat_config["enabled"] = True
    webchat_config["allow_from"] = ["*"]

    if webchat_host:
        webchat_config["host"] = webchat_host
    if webchat_port:
        webchat_config["port"] = int(webchat_port)
    if nanobot_access_key:
        webchat_config["accessKey"] = nanobot_access_key

    # Override MCP server env vars from Docker env vars
    if "tools" not in config:
        config["tools"] = {}
    if "mcpServers" not in config["tools"]:
        config["tools"]["mcpServers"] = {}

    # LMS MCP server
    if "lms" not in config["tools"]["mcpServers"]:
        config["tools"]["mcpServers"]["lms"] = {
            "command": "python",
            "args": ["-m", "mcp_lms"],
            "env": {},
        }

    lms_env = config["tools"]["mcpServers"]["lms"].setdefault("env", {})
    lms_backend_url = os.environ.get("NANOBOT_LMS_BACKEND_URL")
    lms_api_key = os.environ.get("NANOBOT_LMS_API_KEY")

    if lms_backend_url:
        lms_env["NANOBOT_LMS_BACKEND_URL"] = lms_backend_url
    if lms_api_key:
        lms_env["NANOBOT_LMS_API_KEY"] = lms_api_key

    # Observability MCP server
    if "observability" not in config["tools"]["mcpServers"]:
        config["tools"]["mcpServers"]["observability"] = {
            "command": "python",
            "args": ["-m", "mcp_obs"],
            "env": {},
        }

    obs_env = config["tools"]["mcpServers"]["observability"].setdefault("env", {})
    victorialogs_url = os.environ.get("NANOBOT_VICTORIALOGS_URL")
    victoriatraces_url = os.environ.get("NANOBOT_VICTORIATRACES_URL")

    if victorialogs_url:
        obs_env["VICTORIALOGS_URL"] = victorialogs_url
    if victoriatraces_url:
        obs_env["VICTORIATRACES_URL"] = victoriatraces_url

    # Webchat MCP server for structured UI messages
    if "webchat" not in config["tools"]["mcpServers"]:
        config["tools"]["mcpServers"]["webchat"] = {
            "command": "python",
            "args": ["-m", "mcp_webchat"],
            "env": {},
        }

    webchat_mcp_env = config["tools"]["mcpServers"]["webchat"].setdefault("env", {})
    webchat_relay_url = os.environ.get("NANOBOT_WEBCHAT_RELAY_URL")
    webchat_token = os.environ.get("NANOBOT_WEBCHAT_TOKEN")

    if webchat_relay_url:
        webchat_mcp_env["NANOBOT_WEBCHAT_RELAY_URL"] = webchat_relay_url
    if webchat_token:
        webchat_mcp_env["NANOBOT_WEBCHAT_TOKEN"] = webchat_token

    # Cron MCP server for scheduled jobs
    if "cron" not in config["tools"]["mcpServers"]:
        config["tools"]["mcpServers"]["cron"] = {
            "command": "python",
            "args": ["-m", "mcp_cron"],
            "env": {},
        }

    cron_env = config["tools"]["mcpServers"]["cron"].setdefault("env", {})
    workspace_dir_env = os.environ.get("NANOBOT_WORKSPACE_DIR")

    if workspace_dir_env:
        cron_env["NANOBOT_WORKSPACE_DIR"] = workspace_dir_env
    else:
        cron_env["NANOBOT_WORKSPACE_DIR"] = str(workspace_dir)

    # Write resolved config
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Using config: {resolved_path}", file=sys.stderr)

    # Launch nanobot gateway
    os.execvp(
        "nanobot",
        [
            "nanobot",
            "gateway",
            "--config",
            str(resolved_path),
            "--workspace",
            str(workspace_dir),
        ],
    )


if __name__ == "__main__":
    main()
