"""Schema explorer — progressive database schema discovery."""

from __future__ import annotations

from typing import TYPE_CHECKING

from a2db.drivers import DriverRegistry

if TYPE_CHECKING:
    from a2db.connections import ConnectionStore


class SchemaExplorer:
    """Explores database schemas at varying detail levels."""

    def __init__(self, store: ConnectionStore) -> None:
        self.store = store
        self.registry = DriverRegistry()

    def search_objects(
        self,
        connection: dict[str, str],
        object_type: str,
        pattern: str = "%",
        schema: str | None = None,  # noqa: ARG002
        table: str | None = None,
        detail_level: str = "names",
        limit: int = 100,
    ) -> dict:
        """Search database objects with progressive detail levels."""
        info = self.store.load(connection["project"], connection["env"], connection["db"])
        conn = self.registry.connect(info.dsn)

        try:
            if object_type == "table":
                results = self._search_tables(conn, info.scheme, pattern, detail_level)
            elif object_type == "column":
                results = self._search_columns(conn, info.scheme, table, pattern, detail_level)
            else:
                results = []
        finally:
            conn.close()

        truncated = len(results) > limit
        if truncated:
            results = results[:limit]

        return {
            "object_type": object_type,
            "pattern": pattern,
            "detail_level": detail_level,
            "count": len(results),
            "truncated": truncated,
            "results": results,
        }

    def _search_tables(self, conn, scheme: str, pattern: str, detail_level: str) -> list[dict]:
        """Search tables using SQLite-compatible queries."""
        cursor = conn.cursor()

        if scheme == "sqlite":
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ? ORDER BY name",
                (pattern,),
            )
        else:
            cursor.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE %s ORDER BY table_name",
                (pattern,),
            )

        tables = [row[0] for row in cursor.fetchall()]
        results = []

        for table_name in tables:
            entry: dict = {"name": table_name}

            if detail_level in ("summary", "full"):
                if scheme == "sqlite":
                    cursor.execute(f"PRAGMA table_info('{table_name}')")
                else:
                    cursor.execute(
                        "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s",
                        (table_name,),
                    )
                columns_info = cursor.fetchall()
                entry["column_count"] = len(columns_info)

            if detail_level == "full":
                if scheme == "sqlite":
                    entry["columns"] = [
                        {"name": col[1], "type": col[2], "nullable": not col[3], "pk": bool(col[5])} for col in columns_info
                    ]
                else:
                    entry["columns"] = [{"name": col[0], "type": col[1]} for col in columns_info]

            results.append(entry)

        return results

    def _search_columns(self, conn, scheme: str, table: str | None, pattern: str, detail_level: str) -> list[dict]:
        """Search columns within a table."""
        cursor = conn.cursor()

        if scheme == "sqlite":
            if table:
                cursor.execute(f"PRAGMA table_info('{table}')")
            else:
                return []
            columns = cursor.fetchall()
            results = []
            for col in columns:
                name = col[1]
                if pattern == "%" or pattern.replace("%", "") in name:
                    entry: dict = {"name": name}
                    if detail_level in ("summary", "full"):
                        entry["type"] = col[2]
                        entry["nullable"] = not col[3]
                        entry["pk"] = bool(col[5])
                    results.append(entry)
            return results

        cursor.execute(
            "SELECT column_name, data_type, is_nullable "
            "FROM information_schema.columns "
            "WHERE table_name = %s AND column_name LIKE %s "
            "ORDER BY ordinal_position",
            (table, pattern),
        )
        results = []
        for col in cursor.fetchall():
            entry = {"name": col[0]}
            if detail_level in ("summary", "full"):
                entry["type"] = col[1]
                entry["nullable"] = col[2] == "YES"
            results.append(entry)
        return results
