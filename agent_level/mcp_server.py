"""MCP server for the Agent Level Calculator (stdio, no dependencies).

Speaks newline-delimited JSON-RPC 2.0, the standard MCP stdio transport.
All diagnostics go to stderr so stdout stays a clean protocol stream.

Tools:
  - calculate_level: {"profile": {...}} -> full score report
  - xp_to_level: {"xp": int} -> level, title, thresholds
"""

import json
import sys

from .core import VERSION, calculate, level_for_xp

SERVER_INFO = {"name": "agent-level-calculator", "version": VERSION}
PROTOCOL_VERSION = "2024-11-05"


def _log(message):
    print(message, file=sys.stderr, flush=True)


def _result(request_id, result):
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id, code, message):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


def handle(request):
    method = request.get("method", "")
    request_id = request.get("id")
    params = request.get("params", {}) or {}

    if method == "initialize":
        return _result(
            request_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": SERVER_INFO,
            },
        )
    if method == "ping":
        return _result(request_id, {})
    if method == "tools/list":
        return _result(
            request_id,
            {
                "tools": [
                    {
                        "name": "calculate_level",
                        "description": (
                            "Score an AI agent profile with the Level "
                            "Formula Spec v1: five dimensions, composite, "
                            "INT, XP, level, and title."
                        ),
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "profile": {
                                    "type": "object",
                                    "description": (
                                        "Agent profile following the README "
                                        "input schema."
                                    ),
                                }
                            },
                            "required": ["profile"],
                        },
                    },
                    {
                        "name": "xp_to_level",
                        "description": (
                            "Convert a total XP value into level, title, "
                            "and thresholds."
                        ),
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "xp": {"type": "integer", "minimum": 0}
                            },
                            "required": ["xp"],
                        },
                    },
                ]
            },
        )
    if method == "tools/call":
        name = params.get("name", "")
        arguments = params.get("arguments", {}) or {}
        try:
            if name == "calculate_level":
                if "profile" not in arguments:
                    raise ValueError("calculate_level needs a profile")
                output = calculate(arguments["profile"])
            elif name == "xp_to_level":
                if "xp" not in arguments:
                    raise ValueError("xp_to_level needs xp")
                output = level_for_xp(arguments["xp"])
            else:
                return _error(request_id, -32602, f"unknown tool: {name}")
        except (ValueError, TypeError, KeyError) as exc:
            return _error(request_id, -32602, str(exc))
        return _result(
            request_id,
            {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(output, ensure_ascii=False),
                    }
                ]
            },
        )
    if method.startswith("notifications/"):
        return None
    return _error(request_id, -32601, f"method not found: {method}")


def main():
    _log(f"agent-level-calculator MCP server v{VERSION} listening on stdio")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as exc:
            sys.stdout.write(
                json.dumps(_error(None, -32700, f"parse error: {exc}")) + "\n"
            )
            sys.stdout.flush()
            continue
        try:
            response = handle(request)
        except Exception as exc:  # keep the server alive on bad input
            response = _error(request.get("id"), -32603, f"internal: {exc}")
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
