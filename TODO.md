# a2db — TODO

## Features
- [ ] **Write mode (per-connection)** — write support exists in the executor (`read_only=False`) but is not exposed via MCP. Design: store a `writable` flag per connection in the TOML file, set explicitly by the human operator at `login` time (e.g., `login --writable`). The agent can then write only to connections the human marked as writable. Never expose a global write toggle.
- [ ] **Connection reuse in batch** — currently opens/closes a new connection per query in a batch. For 10 queries against the same DB, that's 10 handshakes. Pool or reuse connections sharing the same triple within a batch.
- [ ] Consider removing column header row from TSV data payload — the agent wrote the SQL, so it already knows the columns. Would save tokens on large result sets. Might need a flag (`include_headers=false`) for backward compat.

## Quality
- [ ] **schema.py coverage at 78%** — non-SQLite branches (PostgreSQL `information_schema` paths) have zero test coverage. Add mock-based tests for `_search_tables` and `_search_columns` with PostgreSQL-style responses.
- [ ] **Remote HTTP transport** — OAuth 2.1 per MCP spec for cloud deployment.
