"""Core database operations shared by CLI and MCP frontends."""

from __future__ import annotations


class DatabaseError(Exception):
    """Raised when a database operation fails."""


class Database:
    """Thin wrapper around a database connection."""

    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string

    def connect(self) -> None:
        """Establish connection to the database."""
        raise NotImplementedError

    def query(self, sql: str) -> list[dict]:
        """Execute a SQL query and return rows as dicts."""
        raise NotImplementedError

    def list_tables(self) -> list[str]:
        """Return all table names in the database."""
        raise NotImplementedError

    def describe_table(self, table_name: str) -> dict:
        """Return schema info for a table."""
        raise NotImplementedError
