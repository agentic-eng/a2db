from pathlib import Path

import pytest

from a2db.drivers import DriverNotFoundError, DriverRegistry


def test_resolve_sqlite():
    reg = DriverRegistry()
    driver = reg.resolve("sqlite")
    assert driver.scheme == "sqlite"
    assert driver.module_name == "sqlite3"


def test_resolve_postgresql():
    reg = DriverRegistry()
    driver = reg.resolve("postgresql")
    assert driver.scheme == "postgresql"
    assert driver.module_name == "psycopg2"


def test_resolve_unknown_raises():
    reg = DriverRegistry()
    with pytest.raises(DriverNotFoundError, match="Unknown database scheme: 'nosql'"):
        reg.resolve("nosql")


def test_connect_sqlite(sqlite_db: Path):
    reg = DriverRegistry()
    conn = reg.connect(f"sqlite:///{sqlite_db}")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    assert cursor.fetchone()[0] == 3
    conn.close()


def test_connect_unknown_scheme_raises():
    reg = DriverRegistry()
    with pytest.raises(DriverNotFoundError):
        reg.connect("nosql://localhost/db")


def test_driver_not_found_error_has_install_hint():
    reg = DriverRegistry()
    driver = reg.resolve("postgresql")
    assert driver.install_hint == "pip install psycopg2-binary"


def test_parse_dsn_kwargs():
    from a2db.drivers import _parse_dsn_kwargs

    kwargs = _parse_dsn_kwargs("mysql://admin:secret@db.example.com:3306/mydb")
    assert kwargs["host"] == "db.example.com"
    assert kwargs["port"] == 3306
    assert kwargs["user"] == "admin"
    assert kwargs["password"] == "secret"
    assert kwargs["database"] == "mydb"


def test_parse_dsn_kwargs_minimal():
    from a2db.drivers import _parse_dsn_kwargs

    kwargs = _parse_dsn_kwargs("mysql://localhost/mydb")
    assert kwargs["host"] == "localhost"
    assert kwargs["database"] == "mydb"
    assert "port" not in kwargs
    assert "user" not in kwargs


def test_all_schemes_have_install_hints():
    reg = DriverRegistry()
    for scheme in ["postgresql", "mysql", "mariadb", "sqlite", "oracle", "mssql"]:
        driver = reg.resolve(scheme)
        assert driver.install_hint, f"Missing install hint for {scheme}"
