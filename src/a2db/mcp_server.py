from mcp.server.fastmcp import FastMCP

server = FastMCP("a2db", instructions="Agent-to-Database — query and explore databases.")


@server.tool()
def query(sql: str, connection_string: str) -> str:
    """Execute a SQL query against a database and return results."""
    return f"TODO: execute '{sql}' against '{connection_string}'"


@server.tool()
def list_tables(connection_string: str) -> str:
    """List all tables in the database."""
    return f"TODO: list tables for '{connection_string}'"


@server.tool()
def describe_table(table_name: str, connection_string: str) -> str:
    """Describe the schema of a specific table."""
    return f"TODO: describe '{table_name}' in '{connection_string}'"
