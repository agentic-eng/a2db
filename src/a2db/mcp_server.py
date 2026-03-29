"""MCP server frontend — thin wrapper around a2db core."""

from __future__ import annotations

import json
from typing import Any, cast

from mcp.server.fastmcp import FastMCP

from a2db.config import DEFAULT_CONFIG_DIR
from a2db.connections import ConnectionInfo, ConnectionStore
from a2db.drivers import DriverRegistry
from a2db.executor import QueryExecutor
from a2db.formatter import format_results
from a2db.schema import SchemaExplorer

server = FastMCP(
    "a2db",
    instructions=(
        "Agent-to-Database — query and explore databases. "
        "Connections are identified by (project, env, db) triple. "
        "Use 'login' to save a connection, then 'execute' to run queries. "
        "Always include LIMIT in your queries or use the limit parameter. "
        "Default output is TSV for token efficiency."
    ),
)


def _store() -> ConnectionStore:
    return ConnectionStore(DEFAULT_CONFIG_DIR)


@server.tool()
async def login(project: str, env: str, db: str, dsn: str) -> str:
    """Save a database connection. Validates by attempting a real connection."""
    info = ConnectionInfo(project=project, env=env, db=db, dsn=dsn)
    DriverRegistry().resolve(info.scheme)

    # Validate by connecting
    conn = await DriverRegistry().connect(info.resolved_dsn)
    await conn.close()

    store = _store()
    path = store.save(project, env, db, dsn)
    return f"Connection saved: {path}"


@server.tool()
def logout(project: str, env: str, db: str) -> str:
    """Remove a saved connection."""
    store = _store()
    store.delete(project, env, db)
    return f"Connection removed: {project}/{env}/{db}"


@server.tool()
def list_connections(project: str | None = None) -> str:
    """List saved connections. Returns project/env/db and database type (no secrets)."""
    store = _store()
    results = store.list_connections(project=project)
    if not results:
        return "No connections found."
    lines = [f"{r.project}/{r.env}/{r.db} ({r.scheme})" for r in results]
    return "\n".join(lines)


def _normalize_queries(
    raw_queries: Any,
    default_connection: dict[str, str] | None = None,
) -> dict[str, dict[str, Any]]:
    """Normalize queries from any format to named dict.

    Accepts dict, list, or JSON string. Lists get auto-named q1, q2, etc.
    If default_connection is provided, it's injected into queries that lack one.
    """
    queries: Any = raw_queries

    # Handle JSON string input
    if isinstance(queries, str):
        queries = json.loads(queries)

    # List → named dict
    if isinstance(queries, list):
        queries = {f"q{i + 1}": q for i, q in enumerate(queries)}

    if not isinstance(queries, dict):
        msg = f"queries must be a dict or list, got {type(queries).__name__}"
        raise TypeError(msg)

    # Inject default connection where missing
    normalized = cast("dict[str, dict[str, Any]]", queries)
    if default_connection:
        for spec in normalized.values():
            if "connection" not in spec:
                spec["connection"] = default_connection

    return normalized


@server.tool()
async def execute(
    queries: Any,
    connection: dict[str, str] | None = None,
    format: str = "tsv",  # noqa: A002
    limit: int = 100,
    offset: int = 0,
) -> dict:
    """Execute named SQL queries. Each query specifies its connection and SQL.

    Example — named dict (preferred):
    {
        "active_users": {
            "connection": {"project": "myapp", "env": "prod", "db": "users"},
            "sql": "SELECT id, name FROM users WHERE active = true"
        }
    }

    Example — list (auto-named q1, q2, ...):
    [
        {"connection": {"project": "myapp", "env": "prod", "db": "users"}, "sql": "SELECT ..."},
        {"connection": {"project": "myapp", "env": "prod", "db": "users"}, "sql": "SELECT ..."}
    ]

    Example — with default connection (avoids repeating connection in each query):
    connection: {"project": "myapp", "env": "prod", "db": "users"}
    queries: {"users": {"sql": "SELECT ..."}, "orders": {"sql": "SELECT ..."}}

    Returns results in TSV (default) or JSON format.
    """
    normalized = _normalize_queries(queries, default_connection=connection)
    store = _store()
    executor = QueryExecutor(store)
    results = await executor.execute(normalized, limit=limit, offset=offset)
    return format_results(results, fmt=format)


@server.tool()
async def search_objects(
    connection: dict[str, str],
    object_type: str,
    pattern: str = "%",
    schema: str | None = None,
    table: str | None = None,
    detail_level: str = "names",
    limit: int = 100,
) -> str:
    """Search database objects.

    object_type: table, column
    detail_level: names (minimal), summary (with metadata), full (complete structure)
    """
    explorer = SchemaExplorer(_store())
    result = await explorer.search_objects(
        connection=connection,
        object_type=object_type,
        pattern=pattern,
        schema=schema,
        table=table,
        detail_level=detail_level,
        limit=limit,
    )
    return json.dumps(result, indent=2)


def main() -> None:
    """Run the MCP server (stdio transport)."""
    server.run()


if __name__ == "__main__":
    main()
