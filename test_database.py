
import sqlite3

import database


def setup_test_database(monkeypatch, tmp_path):
    test_db = tmp_path / "test_property_monitor.db"

    monkeypatch.setattr(
        database,
        "DATABASE_NAME",
        str(test_db)
    )

    database.create_tables()


def test_create_tables(monkeypatch, tmp_path):
    setup_test_database(monkeypatch, tmp_path)

    connection = database.get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    )
    tables = [row[0] for row in cursor.fetchall()]

    connection.close()

    assert "listings" in tables
    assert "events" in tables


def test_save_and_retrieve_listing(monkeypatch, tmp_path):
    setup_test_database(monkeypatch, tmp_path)

    listing = {
        "id": "TEST123",
        "title": "Vente Villa Mostaganem",
        "created_at": "2026-10-24",
        "price": 25000000,
        "slug": "vente-villa-mostaganem",
        "city": "Mostaganem",
        "transaction_type": "sale",
        "last_seen": "2026-10-24 13:00:00"
    }

    database.save_listing(listing)

    result = database.get_listing_by_id("TEST123")

    assert result is not None
    assert result["id"] == "TEST123"
    assert result["title"] == "Vente Villa Mostaganem"
    assert result["price"] == 25000000
    assert result["city"] == "Mostaganem"


def test_get_missing_listing_returns_none(monkeypatch, tmp_path):
    setup_test_database(monkeypatch, tmp_path)

    result = database.get_listing_by_id("DOES_NOT_EXIST")

    assert result is None


def test_save_and_retrieve_event(monkeypatch, tmp_path):
    setup_test_database(monkeypatch, tmp_path)

    database.save_event(
        "NEW",
        "TEST123",
        "Vente Villa Mostaganem",
        None,
        25000000,
        "Mostaganem",
        "2026-10-24 13:00:00"
    )

    events = database.get_events()

    assert len(events) == 1
    assert events[0]["event_type"] == "NEW"
    assert events[0]["listing_id"] == "TEST123"
    assert events[0]["new_price"] == 25000000
    assert events[0]["old_price"] is None
