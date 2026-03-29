import json

import pytest

from a2db.mcp_server import _normalize_queries


def test_normalize_queries_dict_passthrough():
    queries = {
        "users": {"connection": {"project": "x", "env": "y", "db": "z"}, "sql": "SELECT 1"},
        "orders": {"connection": {"project": "x", "env": "y", "db": "z"}, "sql": "SELECT 2"},
    }
    assert _normalize_queries(queries) is queries


def test_normalize_queries_list_to_named_dict():
    queries = [
        {"connection": {"project": "x", "env": "y", "db": "z"}, "sql": "SELECT 1"},
        {"connection": {"project": "x", "env": "y", "db": "z"}, "sql": "SELECT 2"},
    ]
    result = _normalize_queries(queries)
    assert isinstance(result, dict)
    assert "q1" in result
    assert "q2" in result
    assert result["q1"]["sql"] == "SELECT 1"
    assert result["q2"]["sql"] == "SELECT 2"


def test_normalize_queries_single_list_item():
    queries = [{"connection": {"project": "x", "env": "y", "db": "z"}, "sql": "SELECT 1"}]
    result = _normalize_queries(queries)
    assert result == {"q1": queries[0]}


def test_normalize_queries_json_string():
    queries = json.dumps(
        {
            "q1": {"connection": {"project": "x", "env": "y", "db": "z"}, "sql": "SELECT 1"},
        }
    )
    result = _normalize_queries(queries)
    assert result["q1"]["sql"] == "SELECT 1"


def test_normalize_queries_json_string_list():
    queries = json.dumps(
        [
            {"connection": {"project": "x", "env": "y", "db": "z"}, "sql": "SELECT 1"},
            {"connection": {"project": "x", "env": "y", "db": "z"}, "sql": "SELECT 2"},
        ]
    )
    result = _normalize_queries(queries)
    assert "q1" in result
    assert "q2" in result


def test_normalize_queries_default_connection():
    conn = {"project": "x", "env": "y", "db": "z"}
    queries = {"users": {"sql": "SELECT 1"}, "orders": {"sql": "SELECT 2"}}
    result = _normalize_queries(queries, default_connection=conn)
    assert result["users"]["connection"] == conn
    assert result["orders"]["connection"] == conn


def test_normalize_queries_default_connection_no_override():
    default_conn = {"project": "x", "env": "y", "db": "z"}
    explicit_conn = {"project": "a", "env": "b", "db": "c"}
    queries = {
        "uses_default": {"sql": "SELECT 1"},
        "has_own": {"connection": explicit_conn, "sql": "SELECT 2"},
    }
    result = _normalize_queries(queries, default_connection=default_conn)
    assert result["uses_default"]["connection"] == default_conn
    assert result["has_own"]["connection"] == explicit_conn


def test_normalize_queries_default_connection_with_list():
    conn = {"project": "x", "env": "y", "db": "z"}
    queries = [{"sql": "SELECT 1"}, {"sql": "SELECT 2"}]
    result = _normalize_queries(queries, default_connection=conn)
    assert result["q1"]["connection"] == conn
    assert result["q2"]["connection"] == conn


def test_normalize_queries_invalid_type_raises():
    with pytest.raises(TypeError, match="queries must be a dict or list"):
        _normalize_queries(42)
