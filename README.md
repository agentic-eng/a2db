# a2db

Agent-to-Database — query databases from CLI or as an MCP server.

## Install

```bash
pip install a2db
```

## CLI Usage

```bash
a2db connect "postgresql://user:pass@localhost/mydb"
a2db query "SELECT * FROM users LIMIT 10"
```

## MCP Usage

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "a2db": {
      "command": "a2db-mcp",
      "args": []
    }
  }
}
```

## Development

```bash
make bootstrap   # Install deps
make check       # Lint + test
```

## License

MIT
