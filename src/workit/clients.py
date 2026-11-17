"""Setup snippets for each AI client (`workit config <client>`)."""
from __future__ import annotations

import json
import shutil
import sys


def _command() -> tuple[str, list[str]]:
    """The most reliable way to start this install of WorkitStudio."""
    found = shutil.which("workit")
    if found:
        return found, []
    return sys.executable, ["-m", "workit"]


def _stdio_entry() -> dict:
    command, args = _command()
    return {"command": command, "args": args}


def _json(value) -> str:
    return json.dumps(value, indent=2)


def _claude_desktop() -> str:
    return ("Claude Desktop: Settings > Developer > Edit Config "
            "(%APPDATA%\\Claude\\claude_desktop_config.json), then restart Claude:\n"
            + _json({"mcpServers": {"workit": _stdio_entry()}}))


def _claude_code() -> str:
    command, args = _command()
    return ("Claude Code, in a terminal:\n"
            f'claude mcp add workit -- "{command}" {" ".join(args)}'.rstrip())


def _cursor() -> str:
    return ("Cursor: %USERPROFILE%\\.cursor\\mcp.json\n"
            + _json({"mcpServers": {"workit": _stdio_entry()}}))


def _vscode() -> str:
    return ("VS Code + GitHub Copilot: .mcp.json in the workspace root\n"
            + _json({"mcpServers": {"workit": dict(_stdio_entry(), type="stdio")}}))


def _gemini() -> str:
    return ("Gemini CLI: %USERPROFILE%\\.gemini\\settings.json\n"
            + _json({"mcpServers": {"workit": _stdio_entry()}})
            + "\n\nAntigravity: %USERPROFILE%\\.gemini\\config\\mcp_config.json (same shape).")


def _codex() -> str:
    command, args = _command()
    arg_list = ", ".join(json.dumps(arg) for arg in args)
    return ("Codex CLI: %USERPROFILE%\\.codex\\config.toml\n"
            "[mcp_servers.workit]\n"
            f"command = {json.dumps(command)}\n"
            f"args = [{arg_list}]")


def _lmstudio() -> str:
    return ("LM Studio (local models): Program tab > Install > Edit mcp.json\n"
            + _json({"mcpServers": {"workit": _stdio_entry()}}))


def _chatgpt() -> str:
    return (
        "ChatGPT (and the Gemini app, Claude.ai web connectors, Open WebUI) cannot start a\n"
        "program on your PC. They need a URL:\n"
        "  1. workit serve --transport http --port 8765\n"
        "       -> the server is now at http://127.0.0.1:8765/mcp\n"
        "  2. Open WebUI and other local tools can use that URL directly.\n"
        "  3. ChatGPT and the Gemini app run in the cloud, so they need a public HTTPS\n"
        "     address that forwards to it: OpenAI's Secure MCP Tunnel, or a tunnel such as\n"
        "     cloudflared or ngrok. Then add the https://.../mcp URL as a custom MCP server.\n"
        "  WARNING: anyone who can reach that URL can run scripts in your CAD apps.\n"
        "  Only use a tunnel that requires a login, and stop it when you are done."
    )


_CLIENTS = {
    "claude-desktop": _claude_desktop, "claude-code": _claude_code, "cursor": _cursor,
    "vscode": _vscode, "gemini": _gemini, "codex": _codex, "lmstudio": _lmstudio,
    "chatgpt": _chatgpt,
}


def snippet(client: str) -> str:
    key = (client or "all").lower()
    if key == "all":
        return "\n\n".join(builder() for builder in _CLIENTS.values())
    if key not in _CLIENTS:
        raise SystemExit(f"Unknown client {client!r}. Choose from: {', '.join(_CLIENTS)}, all")
    return _CLIENTS[key]()
