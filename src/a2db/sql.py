"""SQL wrapping — pagination via SQLGlot and read-only validation."""

from __future__ import annotations

import sqlglot

MAX_ROWS = 10_000
DEFAULT_LIMIT = 100

# Maps DSN scheme to SQLGlot dialect name
DSN_TO_DIALECT: dict[str, str] = {
    "postgresql": "postgres",
    "postgres": "postgres",
    "mysql": "mysql",
    "mariadb": "mysql",
    "sqlite": "sqlite",
    "oracle": "oracle",
    "mssql": "tsql",
}

_ALLOWED_STATEMENT_TYPES = {
    sqlglot.exp.Select,
    sqlglot.exp.Union,
}

_FORBIDDEN_KEYWORDS = {"INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER", "CREATE", "GRANT", "REVOKE"}


class ReadOnlyViolationError(Exception):
    """Raised when a query contains a write operation."""


class SQLParseError(Exception):
    """Raised when SQL cannot be parsed."""


def validate_read_only(sql: str) -> None:
    """Reject DML/DDL statements. Uses SQLGlot parsing to catch comments and multi-statement bypass."""
    stripped = sql.strip().rstrip(";")
    if not stripped:
        raise ReadOnlyViolationError("Empty query")

    try:
        statements = sqlglot.parse(stripped)
    except sqlglot.errors.ParseError:
        # Fall back to keyword check if SQLGlot can't parse
        first_token = stripped.split()[0].upper()
        if first_token in _FORBIDDEN_KEYWORDS:
            raise ReadOnlyViolationError(f"Write operation not allowed: {first_token}") from None
        return

    if not statements:
        raise ReadOnlyViolationError("Empty query")

    for stmt in statements:
        if stmt is None:
            continue
        stmt_type = type(stmt)
        if stmt_type in _ALLOWED_STATEMENT_TYPES:
            continue
        # Check if it's a Command like EXPLAIN or SHOW
        if isinstance(stmt, sqlglot.exp.Command):
            cmd_name = stmt.this.upper() if isinstance(stmt.this, str) else ""
            if cmd_name in ("EXPLAIN", "SHOW", "DESCRIBE", "PRAGMA"):
                continue
        stmt_name = stmt.key.upper()
        raise ReadOnlyViolationError(f"Write operation not allowed: {stmt_name}")


def wrap_with_pagination(
    sql: str,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
    dialect: str = "sqlite",
) -> str:
    """Wrap a SQL query with LIMIT/OFFSET using SQLGlot dialect transpilation."""
    limit = min(limit, MAX_ROWS)
    sqlglot_dialect = DSN_TO_DIALECT.get(dialect, dialect)

    wrapped = f"SELECT * FROM ({sql}) AS _q LIMIT {limit} OFFSET {offset}"  # noqa: S608
    try:
        transpiled = sqlglot.transpile(wrapped, read=sqlglot_dialect, write=sqlglot_dialect)
    except sqlglot.errors.ParseError as exc:
        raise SQLParseError(f"Failed to parse SQL: {exc}") from exc
    return transpiled[0]
