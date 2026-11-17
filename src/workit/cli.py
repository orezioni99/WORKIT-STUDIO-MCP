"""Command line: workit serve | apps | install | uninstall | config | run | token"""
from __future__ import annotations

import argparse
import json
import sys

from . import __version__


def _serve(args) -> int:
    from .server import serve

    serve(args.transport, args.host, args.port)
    return 0


def _apps(args) -> int:
    from . import adapters

    rows = adapters.all_status()
    if args.json:
        print(json.dumps(rows, indent=1))
        return 0
    width = max(len(row["app"]) for row in rows)
    for row in rows:
        if args.available and row["state"] == "not running":
            continue
        extra = ""
        if row.get("instances"):
            extra = "  ports " + ", ".join(str(item.get("port")) for item in row["instances"])
        elif row.get("next"):
            extra = "  -> " + row["next"]
        print(f"{row['app']:<{width}}  {row['state']:<28}{extra}")
    return 0


def _install(args) -> int:
    from . import installers

    targets = installers.installable() if args.app == "all" else [args.app]
    code = 0
    for target in targets:
        try:
            for line in installers.install(target):
                print(line)
        except installers.InstallError as error:
            print(f"[{target}] {error}")
            code = 0 if args.app == "all" else 1
    return code


def _uninstall(args) -> int:
    from . import installers

    targets = installers.installable() if args.app == "all" else [args.app]
    for target in targets:
        try:
            for line in installers.uninstall(target):
                print(line)
        except installers.InstallError as error:
            print(f"[{target}] {error}")
    return 0


def _config(args) -> int:
    from . import clients

    print(clients.snippet(args.client))
    return 0


def _run(args) -> int:
    from . import adapters
    from .registry import find

    code = sys.stdin.read() if args.code == "-" else args.code
    try:
        reply = adapters.execute(find(args.app), code, "modify" if args.modify else "read",
                                 args.timeout)
    except (adapters.BridgeError, KeyError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(reply, indent=1, default=str))
    return 0 if reply.get("ok") else 1


def _token(args) -> int:
    from . import adapters

    print(adapters.token())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="workit",
        description="One MCP server that connects any AI model to CAD, BIM and 3D apps.",
    )
    parser.add_argument("--version", action="version", version=f"workit {__version__}")
    sub = parser.add_subparsers(dest="command")

    serve = sub.add_parser("serve", help="run the MCP server (default)")
    serve.add_argument("--transport", choices=["stdio", "http", "sse"], default="stdio",
                       help="stdio for local clients, http for ChatGPT and other remote clients")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)
    serve.set_defaults(run=_serve)

    apps = sub.add_parser("apps", help="list supported apps and which are reachable now")
    apps.add_argument("--json", action="store_true")
    apps.add_argument("--available", action="store_true", help="hide apps that are not running")
    apps.set_defaults(run=_apps)

    install = sub.add_parser("install", help="install the bridge add-in into an app")
    install.add_argument("app", help="app id, or 'all' for every app found on this PC")
    install.set_defaults(run=_install)

    uninstall = sub.add_parser("uninstall", help="remove the bridge add-in from an app")
    uninstall.add_argument("app")
    uninstall.set_defaults(run=_uninstall)

    config = sub.add_parser("config", help="print the setup snippet for an AI client")
    config.add_argument("client", nargs="?", default="all",
                        help="claude-desktop, claude-code, chatgpt, gemini, cursor, vscode, "
                             "lmstudio, codex or all")
    config.set_defaults(run=_config)

    run = sub.add_parser("run", help="run a script in an app from the terminal (for testing)")
    run.add_argument("app")
    run.add_argument("code", help="the script, or - to read it from stdin")
    run.add_argument("--modify", action="store_true")
    run.add_argument("--timeout", type=float, default=120)
    run.set_defaults(run=_run)

    token = sub.add_parser("token", help="print the local secret shared with the bridges")
    token.set_defaults(run=_token)

    args = parser.parse_args(argv)
    if not getattr(args, "run", None):
        args = parser.parse_args(["serve"] + (argv or []))
    return args.run(args) or 0


if __name__ == "__main__":
    sys.exit(main())
