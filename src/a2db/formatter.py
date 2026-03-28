"""Output formatting — TSV and JSON renderers for query results."""

from __future__ import annotations

import json
from dataclasses import dataclass

FIELD_MAX_LENGTH = 2000


@dataclass
class QueryResult:
    """Result of a single named query."""

    name: str
    columns: list[str]
    rows: list[list]
    count: int
    truncated: bool


def _truncate_field(value: object) -> str:
    """Truncate a field value to FIELD_MAX_LENGTH chars."""
    if value is None:
        return "NULL"
    text = str(value)
    if len(text) <= FIELD_MAX_LENGTH:
        return text
    return text[:FIELD_MAX_LENGTH] + "... [truncated]"


def _format_tsv(results: dict[str, QueryResult]) -> str:
    """Format results as TSV with query headers."""
    parts = []
    for name, result in results.items():
        lines = [f"query: {name}"]
        lines.append("\t".join(result.columns))
        lines.extend("\t".join(_truncate_field(v) for v in row) for row in result.rows)
        truncated_str = "true" if result.truncated else "false"
        lines.append(f"rows: {result.count}, truncated: {truncated_str}")
        parts.append("\n".join(lines))
    return "\n\n".join(parts) + "\n"


def _format_json(results: dict[str, QueryResult]) -> str:
    """Format results as JSON."""
    output = {}
    for name, result in results.items():
        rows_as_dicts = []
        for row in result.rows:
            row_dict = {}
            for col, val in zip(result.columns, row, strict=False):
                if isinstance(val, str) and len(val) > FIELD_MAX_LENGTH:
                    val = val[:FIELD_MAX_LENGTH] + "... [truncated]"
                row_dict[col] = val
            rows_as_dicts.append(row_dict)
        output[name] = {
            "columns": result.columns,
            "rows": rows_as_dicts,
            "count": result.count,
            "truncated": result.truncated,
        }
    return json.dumps(output, indent=2, default=str)


def format_results(results: dict[str, QueryResult], fmt: str = "tsv") -> str:
    """Format query results in the specified format."""
    if fmt == "json":
        return _format_json(results)
    return _format_tsv(results)
