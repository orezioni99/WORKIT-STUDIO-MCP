# Connecting an AI client

`workit config <client>` prints the snippet with the right path for your machine.
This page explains what each client can and cannot do. Config locations were checked
against each vendor's documentation in November 2026; they change, so trust the
vendor's page if it disagrees.

## Clients that start WORKIT STUDIO MCP themselves (easiest)

These run on your PC and launch the server as a local program (stdio). Nothing is
exposed to the network.

| Client | Where the entry goes |
|---|---|
| Claude Desktop | `%APPDATA%\Claude\claude_desktop_config.json` (Settings > Developer > Edit Config) |
| Claude Code | `claude mcp add workit -- workit` |
| Cursor | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code + GitHub Copilot | `.mcp.json` in the workspace root |
| Gemini CLI | `%USERPROFILE%\.gemini\settings.json` |
| Antigravity | `%USERPROFILE%\.gemini\config\mcp_config.json` |
| Codex CLI | `%USERPROFILE%\.codex\config.toml` |
| LM Studio (local models) | Program tab > Install > Edit mcp.json |

All except Codex use the same JSON shape:

```json
{
  "mcpServers": {
    "workit": { "command": "workit", "args": [] }
  }
}
```

Codex uses TOML:

```toml
[mcp_servers.workit]
command = "workit"
args = []
```

If the client cannot find `workit`, use the full path that
`workit config <client>` prints.

## Clients that need a URL

ChatGPT, the Gemini app, Claude.ai custom connectors and Open WebUI cannot start a
program on your PC. Run the server in HTTP mode:

```bash
workit serve --transport http --port 8765
```

It is then at `http://127.0.0.1:8765/mcp`.

- **Open WebUI and other tools on the same PC** can use that address directly
  (from Docker: `http://host.docker.internal:8765/mcp`).
- **ChatGPT, the Gemini app and Claude.ai connectors** run in the vendor's cloud, so
  they need a public HTTPS address that forwards to your PC: OpenAI's Secure MCP
  Tunnel, or a tunnel such as cloudflared or ngrok. Add the resulting
  `https://.../mcp` address as a custom MCP server in the client.

**Read this before opening a tunnel.** WORKIT STUDIO MCP's HTTP mode has no login. Anyone who
can reach the address can run scripts in your CAD apps. Use a tunnel that enforces
authentication, never post the address, and stop the tunnel when you finish. For daily
work prefer a client from the first table.

## Local models

Any local model works through a client that speaks MCP: LM Studio, or Ollama behind
Open WebUI or `ollmcp`. Results depend heavily on the model: scripting a CAD API needs
a strong coding model. `cad_skill` exists to give smaller models the facts they lack.
