import pytest

from a2db.core import Database, DatabaseError


def test_database_init():
    db = Database("postgresql://localhost/test")
    assert db.connection_string == "postgresql://localhost/test"


def test_database_error_is_exception():
    assert issubclass(DatabaseError, Exception)


def test_connect_not_implemented():
    db = Database("postgresql://localhost/test")
    with pytest.raises(NotImplementedError):
        db.connect()


def test_query_not_implemented():
    db = Database("postgresql://localhost/test")
    with pytest.raises(NotImplementedError):
        db.query("SELECT 1")


def test_list_tables_not_implemented():
    db = Database("postgresql://localhost/test")
    with pytest.raises(NotImplementedError):
        db.list_tables()


def test_describe_table_not_implemented():
    db = Database("postgresql://localhost/test")
    with pytest.raises(NotImplementedError):
        db.describe_table("users")
