from collector import get_transaction_type
from monitor import (
    detect_new_listings,
    detect_removed_listings,
    detect_price_changes,
)


def test_sale_listing():
    assert get_transaction_type("Vente Villa Mostaganem") == "sale"


def test_rent_listing():
    assert get_transaction_type("Location Appartement F3 Mostaganem") == "rent"


def test_unknown_listing():
    assert get_transaction_type("Appartement Mostaganem") == "unknown"


def test_detect_new_listings():

    current = {
        "1": {"id": "1", "title": "Villa"},
        "2": {"id": "2", "title": "Appartement"},
    }

    previous = {
        "1": {"id": "1", "title": "Villa"},
    }

    new_listings = detect_new_listings(current, previous)

    assert len(new_listings) == 1
    assert new_listings[0]["id"] == "2"


def test_detect_removed_listings():

    current = {
        "1": {"id": "1", "title": "Villa"},
    }

    previous = {
        "1": {"id": "1", "title": "Villa"},
        "2": {"id": "2", "title": "Appartement"},
    }

    removed_listings = detect_removed_listings(current, previous)

    assert len(removed_listings) == 1
    assert removed_listings[0]["id"] == "2"


def test_detect_no_new_listings():

    current = {
        "1": {"id": "1", "title": "Villa"},
    }

    previous = {
        "1": {"id": "1", "title": "Villa"},
    }

    new_listings = detect_new_listings(current, previous)

    assert new_listings == []


def test_detect_no_removed_listings():

    current = {
        "1": {"id": "1", "title": "Villa"},
    }

    previous = {
        "1": {"id": "1", "title": "Villa"},
    }

    removed_listings = detect_removed_listings(current, previous)

    assert removed_listings == []


def test_detect_price_change():

    current = {
        "1": {
            "id": "1",
            "title": "Villa",
            "price": 4500000,
        }
    }

    previous = {
        "1": {
            "id": "1",
            "title": "Villa",
            "price": 5000000,
        }
    }

    price_changes = detect_price_changes(current, previous)

    assert len(price_changes) == 1
    assert price_changes[0]["old_price"] == 5000000
    assert price_changes[0]["new_price"] == 4500000


def test_detect_no_price_change():

    current = {
        "1": {
            "id": "1",
            "title": "Villa",
            "price": 5000000,
        }
    }

    previous = {
        "1": {
            "id": "1",
            "title": "Villa",
            "price": 5000000,
        }
    }

    price_changes = detect_price_changes(current, previous)

    assert price_changes == []


def test_detect_missing_price_change():

    current = {
        "1": {
            "id": "1",
            "title": "Villa",
            "price": None,
        }
    }

    previous = {
        "1": {
            "id": "1",
            "title": "Villa",
            "price": 5000000,
        }
    }

    price_changes = detect_price_changes(current, previous)

    assert len(price_changes) == 1
    assert price_changes[0]["old_price"] == 5000000
    assert price_changes[0]["new_price"] is None


def test_detect_missing_price_event():
    current = {
        "1": {
            "id": "1",
            "title": "Villa",
            "price": None,
        }
    }

    previous = {
        "1": {
            "id": "1",
            "title": "Villa",
            "price": 5_000_000,
        }
    }

    events = detect_price_changes(current, previous)

    assert len(events) == 1
    assert events[0]["event_type"] == "PRICE_MISSING"
    assert events[0]["old_price"] == 5_000_000
    assert events[0]["new_price"] is None


def test_detect_price_added_event():
    current = {
        "1": {
            "id": "1",
            "title": "Villa",
            "price": 5_000_000,
        }
    }

    previous = {
        "1": {
            "id": "1",
            "title": "Villa",
            "price": None,
        }
    }

    events = detect_price_changes(current, previous)

    assert len(events) == 1
    assert events[0]["event_type"] == "PRICE_ADDED"
    assert events[0]["old_price"] is None
    assert events[0]["new_price"] == 5_000_000


def test_detect_new_listings_does_not_repeat_existing_listing():
    listing = {
        "id": "123",
        "title": "Villa in Mostaganem",
        "price": 5_000_000,
    }

    current_listings = {"123": listing}
    previous_listings = {"123": listing.copy()}

    result = detect_new_listings(
        current_listings,
        previous_listings,
    )

    assert result == []

