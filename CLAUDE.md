# a2db — Agent-to-Database

CLI and MCP server for AI agents to query databases. Two frontends (CLI + MCP), one core.

## Architecture

- `src/a2db/core.py` — shared database logic (both frontends use this)
- `src/a2db/cli.py` — Click CLI frontend
- `src/a2db/mcp_server.py` — MCP server frontend

## Dev Commands

- Run tests: `make test`
- Lint: `make lint` or `agent-harness lint` (check only, never modifies files — safe to run anytime)
- Fix: `make fix` or `agent-harness fix` (auto-fix, then runs lint to verify)
- Full gate: `make check` (lint + test)
- Audit: `agent-harness audit` (checks project hygiene)
- Build: `make build`
- Bootstrap: `make bootstrap` (installs deps, requires `agent-harness` CLI)

## Never

- Never commit `.env` files or database credentials
- Never execute destructive SQL (DROP, TRUNCATE, DELETE without WHERE) without explicit user confirmation

## Ask First

- Before changing CLI argument names or command structure (breaking change for users)
- Before adding new dependencies
- Before changing MCP tool signatures (breaking change for MCP clients)
