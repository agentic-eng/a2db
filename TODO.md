# a2db — TODO

- [ ] **Write mode (per-connection)** — write support exists in the executor (`read_only=False`) but is not exposed via MCP. Design: store a `writable` flag per connection in the TOML file, set explicitly by the human operator at `login` time (e.g., `login --writable`). The agent can then write only to connections the human marked as writable. Never expose a global write toggle.
- [ ] Consider removing column header row from TSV data payload — the agent wrote the SQL, so it already knows the columns. Would save tokens on large result sets. Might need a flag (`include_headers=false`) for backward compat.
