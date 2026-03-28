import json

from a2db.formatter import QueryResult, format_results


def _make_result(name: str, columns: list[str], rows: list[list], truncated: bool = False) -> QueryResult:
    return QueryResult(name=name, columns=columns, rows=rows, count=len(rows), truncated=truncated)


def test_format_tsv_single_query():
    result = _make_result("users", ["id", "name"], [[1, "Alice"], [2, "Bob"]])
    output = format_results({"users": result}, fmt="tsv")
    lines = output.strip().split("\n")
    assert lines[0] == "query: users"
    assert lines[1] == "id\tname"
    assert lines[2] == "1\tAlice"
    assert lines[3] == "2\tBob"
    assert lines[4] == "rows: 2, truncated: false"


def test_format_tsv_multiple_queries():
    r1 = _make_result("users", ["id", "name"], [[1, "Alice"]])
    r2 = _make_result("orders", ["id", "total"], [[101, 49.99]])
    output = format_results({"users": r1, "orders": r2}, fmt="tsv")
    assert "query: users" in output
    assert "query: orders" in output


def test_format_tsv_truncated():
    result = _make_result("users", ["id"], [[1]], truncated=True)
    output = format_results({"users": result}, fmt="tsv")
    assert "truncated: true" in output


def test_format_json_single_query():
    result = _make_result("users", ["id", "name"], [[1, "Alice"], [2, "Bob"]])
    output = format_results({"users": result}, fmt="json")
    data = json.loads(output)
    assert "users" in data
    assert data["users"]["columns"] == ["id", "name"]
    assert data["users"]["rows"] == [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    assert data["users"]["count"] == 2
    assert data["users"]["truncated"] is False


def test_format_json_multiple_queries():
    r1 = _make_result("users", ["id"], [[1]])
    r2 = _make_result("orders", ["id"], [[101]])
    output = format_results({"users": r1, "orders": r2}, fmt="json")
    data = json.loads(output)
    assert "users" in data
    assert "orders" in data


def test_format_tsv_none_value():
    result = _make_result("users", ["id", "name"], [[1, None]])
    output = format_results({"users": result}, fmt="tsv")
    assert "1\tNULL" in output


def test_format_tsv_long_field_truncated():
    long_text = "x" * 3000
    result = _make_result("data", ["content"], [[long_text]])
    output = format_results({"data": result}, fmt="tsv")
    assert "... [truncated]" in output
    assert len(output) < 3000


def test_format_json_long_field_truncated():
    long_text = "x" * 3000
    result = _make_result("data", ["content"], [[long_text]])
    output = format_results({"data": result}, fmt="json")
    data = json.loads(output)
    assert "... [truncated]" in data["data"]["rows"][0]["content"]
