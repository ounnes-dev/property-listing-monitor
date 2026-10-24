import os
from datetime import datetime

from collector import collect_listings, get_transaction_type
from database import (
    create_tables,
    get_all_listings,
    save_listing,
    save_event,
)


def current_timestamp():
    """Return the current local timestamp in the database format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def prepare_listing(listing):
    """Normalize a collected listing for database storage."""
    cities = listing.get("cities") or []
    city = listing.get("city") or ""

    if not city and cities and isinstance(cities[0], dict):
        city = cities[0].get("name", "") or ""

    title = listing.get("title") or ""
    timestamp = current_timestamp()

    return {
        "id": str(listing["id"]),
        "title": title,
        "created_at": (
            listing.get("created_at")
            or listing.get("createdAt")
            or ""
        ),
        "last_seen": listing.get("last_seen") or timestamp,
        "price": listing.get("price"),
        "slug": listing.get("slug") or "",
        "city": city,
        "transaction_type": (
            listing.get("transaction_type")
            or get_transaction_type(title)
        ),
    }

def normalize_price(price):
    """Convert a price to float, preserving missing prices as None."""
    if price in ("", None):
        return None

    try:
        return float(price)
    except (TypeError, ValueError):
        return None


def detect_new_listings(current_listings, previous_listings):
    """Return listings whose IDs were not in the previous snapshot."""
    return [
        current_listings[listing_id]
        for listing_id in current_listings
        if listing_id not in previous_listings
    ]


def detect_price_changes(current_listings, previous_listings):
    """
    Detect price changes for listings present in both snapshots.

    Event types:
    - PRICE_MISSING: a previously available price is now missing.
    - PRICE_ADDED: a previously missing price is now available.
    - PRICE_CHANGED: both prices exist and differ.
    """
    events = []

    for listing_id, current in current_listings.items():
        if listing_id not in previous_listings:
            continue

        previous = previous_listings[listing_id]

        old_price = normalize_price(previous.get("price"))
        new_price = normalize_price(current.get("price"))

        if old_price == new_price:
            continue

        if old_price is not None and new_price is None:
            event_type = "PRICE_MISSING"
        elif old_price is None and new_price is not None:
            event_type = "PRICE_ADDED"
        else:
            event_type = "PRICE_CHANGED"

        events.append({
            "event_type": event_type,
            "listing_id": listing_id,
            "title": current.get("title", ""),
            "old_price": old_price,
            "new_price": new_price,
            "city": current.get("city", ""),
        })

    return events


def detect_removed_listings(current_listings, previous_listings):
    """
    Identify previously active listings absent from current results.

    Absence from a limited collection does not prove removal from
    Ouedkniss. Use this comparison only for a complete, equivalent
    search scope.
    """
    return [
        previous_listings[listing_id]
        for listing_id in previous_listings
        if listing_id not in current_listings
    ]


def main():
    """Collect listings, detect changes, and update the database."""
    create_tables()

    max_pages = int(
        os.getenv("PROPERTY_MONITOR_MAX_PAGES", "3")
    )

    if max_pages < 1:
        raise ValueError(
            "PROPERTY_MONITOR_MAX_PAGES must be at least 1."
        )

    try:
        listings = collect_listings(max_pages=max_pages)
    except (RuntimeError, ValueError) as error:
        print(f"ERROR: Collection failed: {error}")
        return

    if not listings:
        raise RuntimeError(
            "No listings were collected. Database was not updated."
        )

    # Normalize and deduplicate the current results.
    current_by_id = {}

    for raw_listing in listings:
        if not isinstance(raw_listing, dict):
            continue

        if raw_listing.get("id") is None:
            continue

        listing = prepare_listing(raw_listing)
        current_by_id[listing["id"]] = listing

    if not current_by_id:
        raise RuntimeError(
            "No valid listings were collected. Database was not updated."
        )

    # Load the existing database snapshot.
    previous_list = get_all_listings()
    previous_by_id = {
        str(listing["id"]): listing
        for listing in previous_list
        if listing.get("id") is not None
    }

    print("Current listings:", len(current_by_id))
    print("Previous listings:", len(previous_by_id))

    # Detect new listings.
    new_listings = detect_new_listings(
        current_by_id,
        previous_by_id,
    )

    for listing in new_listings:
        print()
        print("NEW LISTING")
        print("ID:", listing["id"])
        print("Title:", listing["title"])
        print("Price:", listing["price"])
        print("City:", listing["city"])
        print("Transaction type:", listing["transaction_type"])

        save_event(
            "NEW",
            listing["id"],
            listing["title"],
            None,
            normalize_price(listing["price"]),
            listing["city"],
            current_timestamp(),
        )

    # Detect price changes.
    price_events = detect_price_changes(
        current_by_id,
        previous_by_id,
    )

    for event in price_events:
        print()
        print(event["event_type"])
        print("ID:", event["listing_id"])
        print("Title:", event["title"])
        print("Old price:", event["old_price"])
        print("New price:", event["new_price"])
        print("City:", event["city"])

        save_event(
            event["event_type"],
            event["listing_id"],
            event["title"],
            event["old_price"],
            event["new_price"],
            event["city"],
            current_timestamp(),
        )

    # Do not mark absent listings as removed: collection is limited
    # to a few pages and cannot establish removal from the whole site.

    # Save normalized current listings.
    for listing in current_by_id.values():
        save_listing(listing)

    print()
    print("Monitoring run complete.")
    print("New listings detected:", len(new_listings))
    print("Price events detected:", len(price_events))
    print("Listings saved:", len(current_by_id))
    print("Removed listings: not checked (limited collection).")


if __name__ == "__main__":
    main()
