"""The WORKIT STUDIO MCP server: five tools, every app."""
from __future__ import annotations

import json
from importlib import resources

import anyio
try:  # mcp 2.x
    from mcp.server.mcpserver import Image, MCPServer
    from mcp.server.mcpserver.exceptions import ToolError
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as MCPServer, Image
    from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import ToolAnnotations

from . import adapters
from .adapters import BridgeError
from .registry import APPS, App, find

INSTRUCTIONS = """\
WORKIT STUDIO MCP connects you to the CAD, BIM and 3D apps running on the user's PC.
You work by sending short scripts that run inside (or directly against) the app.

Start every task with cad_apps to see which apps are connected.
Read cad_skill(app) before your first script for an app: it tells you the script
language, the names already defined for you, the units, and the traps.
Use cad_read for scripts that only inspect. Use cad_modify for scripts that change
the model; the user's client may ask them to approve each one.
Keep scripts small, return data with `result = ...`, and check the outcome with a
read or cad_screenshot before you tell the user it is done.
"""

mcp = MCPServer("WORKIT STUDIO MCP", instructions=INSTRUCTIONS)

_COMMON_SKILL = "_common"
_ISRAEL_DIR = "il"


def _skill_text(name: str) -> str:
    return resources.files("workit").joinpath("skills", f"{name}.md").read_text("utf-8")


def _israel_text(name: str) -> str:
    """The Israeli addition for one guide, or "" when that guide has none."""
    path = resources.files("workit").joinpath("skills", _ISRAEL_DIR, f"{name}.md")
    return path.read_text("utf-8") if path.is_file() else ""


def guide_text(app: App) -> str:
    """The full guide for one app: upstream guide, then the Israeli layer."""
    header = f"# {app.name}\n\nApp id: `{app.id}`. Script language: {app.language}.\n\n"
    parts = [_skill_text(app.skill_name), _israel_text(app.skill_name),
             _skill_text(_COMMON_SKILL), _israel_text(_COMMON_SKILL)]
    return header + "\n\n".join(part.strip() for part in parts if part)


def _dump(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=1, default=str)


def _format(app_id: str, reply: dict) -> str:
    if reply.get("ok"):
        out = {"ok": True, "result": reply.get("result")}
        if reply.get("stdout"):
            out["stdout"] = reply["stdout"]
        if reply.get("elapsed_ms") is not None:
            out["elapsed_ms"] = reply["elapsed_ms"]
        return _dump(out)
    parts = [f"The script failed in {app_id}: {reply.get('error', 'unknown error')}"]
    if reply.get("traceback"):
        parts.append(reply["traceback"].strip()[-3000:])
    if reply.get("stdout"):
        parts.append("Output before the failure:\n" + reply["stdout"][-2000:])
    parts.append(f"Fix the script and try again. cad_skill('{app_id}') lists the usual traps.")
    raise ToolError("\n\n".join(parts))


async def _run(app_name: str, code: str, mode: str, timeout_s: int, instance: int | None,
               label: str) -> str:
    try:
        app = find(app_name)
    except KeyError as error:
        raise ToolError(str(error.args[0])) from None
    timeout = float(max(5, min(int(timeout_s or 120), 3600)))
    try:
        reply = await anyio.to_thread.run_sync(
            lambda: adapters.execute(app, code, mode, timeout, instance, label)
        )
    except BridgeError as error:
        raise ToolError(f"Could not reach {app.name}: {error}") from None
    return _format(app.id, reply)


@mcp.tool(annotations=ToolAnnotations(title="List CAD apps", readOnlyHint=True,
                                      idempotentHint=True, openWorldHint=False))
async def cad_apps(only_available: bool = False) -> str:
    """List every app WORKIT STUDIO MCP supports and whether it is reachable right now.

    Call this first. An app is usable when its state is "connected" or "running".
    When the state is "running, bridge not loaded", tell the user the `next` step.
    Set only_available to true to hide apps that are not running.
    """
    rows = await anyio.to_thread.run_sync(adapters.all_status)
    if only_available:
        rows = [row for row in rows if row["state"] != "not running"]
    return _dump(rows)


@mcp.tool(annotations=ToolAnnotations(title="Read an app's scripting guide", readOnlyHint=True,
                                      idempotentHint=True, openWorldHint=False))
async def cad_skill(app: str) -> str:
    """Return the scripting guide for one app: language, predefined names, units,
    how to return data, common recipes and traps. Read it before scripting an app."""
    try:
        found = find(app)
    except KeyError as error:
        raise ToolError(str(error.args[0])) from None
    return guide_text(found)


@mcp.tool(annotations=ToolAnnotations(title="Run a read-only script", readOnlyHint=True,
                                      openWorldHint=False))
async def cad_read(app: str, code: str, timeout_s: int = 120, instance: int | None = None) -> str:
    """Run a script that only INSPECTS the app's open model. Nothing may be changed.

    app: an id from cad_apps, for example "blender", "autocad", "revit".
    code: the script, in the language given by cad_skill(app). Set `result = ...`
          (or end with an expression) to return data; printed text comes back too.
    instance: port of one instance when cad_apps lists several of the same app.
    """
    return await _run(app, code, "read", timeout_s, instance, "WorkitStudio read")


@mcp.tool(annotations=ToolAnnotations(title="Run a script that changes the model",
                                      readOnlyHint=False, destructiveHint=True,
                                      openWorldHint=False))
async def cad_modify(app: str, code: str, summary: str = "", timeout_s: int = 300,
                     instance: int | None = None) -> str:
    """Run a script that CHANGES the app's open model (create, edit, delete, save).

    Where the app supports it the whole script becomes one undo step, named by
    `summary` (a few words the user will see in the app's undo history).
    Same script rules as cad_read. Verify the result afterwards.
    """
    label = ("AI: " + summary.strip())[:60] if summary.strip() else "AI change"
    return await _run(app, code, "modify", timeout_s, instance, label)


@mcp.tool(annotations=ToolAnnotations(title="Capture the app's viewport", readOnlyHint=True,
                                      openWorldHint=False))
async def cad_screenshot(app: str, width: int = 1280, height: int = 800,
                         instance: int | None = None) -> Image:
    """Capture the app's current viewport as an image so you can check your work.

    Not every app supports this. When it fails, export an image with a script instead.
    """
    try:
        found = find(app)
    except KeyError as error:
        raise ToolError(str(error.args[0])) from None
    width = max(320, min(int(width), 3840))
    height = max(240, min(int(height), 2160))
    try:
        data = await anyio.to_thread.run_sync(
            lambda: adapters.screenshot(found, width, height, instance)
        )
    except BridgeError as error:
        raise ToolError(f"Could not capture {found.name}: {error}") from None
    return Image(data=data, format="png")


def supported_ids() -> list[str]:
    return [app.id for app in APPS]


def serve(transport: str = "stdio", host: str = "127.0.0.1", port: int = 8765) -> None:
    if transport == "stdio":
        mcp.run(transport="stdio")
        return
    kind = "streamable-http" if transport in ("http", "streamable-http") else "sse"
    try:  # mcp 2.x takes host and port as run() arguments
        mcp.run(transport=kind, host=host, port=port)
    except TypeError:  # mcp 1.x keeps them in settings
        mcp.settings.host = host
        mcp.settings.port = port
        mcp.run(transport=kind)
