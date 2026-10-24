
from datetime import datetime

from collector import collect_listings, get_transaction_type
from database import (
    create_tables,
    get_all_listings,
    save_listing,
    save_event,
)


def normalize_price(price):
    """Convert a price to a number, or None when it is missing."""
    if price in ("", None):
        return None

    try:
        return float(price)
    except (TypeError, ValueError):
        return None


def detect_new_listings(current_listings, previous_listings):
    return [
        current_listings[listing_id]
        for listing_id in current_listings
        if listing_id not in previous_listings
    ]


def detect_removed_listings(current_listings, previous_listings):
    return [
        previous_listings[listing_id]
        for listing_id in previous_listings
        if listing_id not in current_listings
    ]





def detect_price_changes(current_listings, previous_listings):
    changes = []

    for listing_id, current in current_listings.items():
        if listing_id not in previous_listings:
            continue

        previous = previous_listings[listing_id]

        old_price = normalize_price(previous.get("price"))
        new_price = normalize_price(current.get("price"))

        # Ignore records where both prices are missing.
        if old_price is None and new_price is None:
            continue

        # Report a change if either price is missing or the values differ.
        if old_price != new_price:
            changes.append({
                "listing": current,
                "old_price": old_price,
                "new_price": new_price,
            })

    return changes



def prepare_listing(listing):
    """Prepare a listing for the database."""
    cities = listing.get("cities") or []
    city = listing.get("city") or ""

    if not city and cities and isinstance(cities[0], dict):
        city = cities[0].get("name", "")

    return {
        "id": str(listing["id"]),
        "title": listing.get("title") or "",
        "created_at": listing.get("createdAt")
        or listing.get("created_at")
        or "",
        "price": normalize_price(listing.get("price")),
        "slug": listing.get("slug") or "",
        "city": city,
        "transaction_type": listing.get("transaction_type")
        or get_transaction_type(listing.get("title", "")),
        "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def main():
    create_tables()

    try:
        listings = collect_listings()
    except RuntimeError as error:
        raise SystemExit(f"ERROR: {error}") from error

    # Never treat a failed or empty collection as proof that
    # previously seen listings have disappeared.
    if not listings:
        raise SystemExit(
            "ERROR: No listings were collected. "
            "The database was not updated."
        )

    current_by_id = {}

    for listing in listings:
        if listing.get("id") is None:
            continue

        prepared = prepare_listing(listing)
        current_by_id[prepared["id"]] = prepared

    if not current_by_id:
        raise SystemExit(
            "ERROR: No valid listing IDs were collected. "
            "The database was not updated."
        )

    previous_listings = get_all_listings()
    previous_by_id = {
        str(listing["id"]): listing
        for listing in previous_listings
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
            listing["price"],
            listing["city"],
        )

    # Removal detection is intentionally skipped while the search
    # scope may differ from the historical database contents.
    print()
    print("Removal detection skipped because the search scope changed.")

    # Detect price changes.
    price_changes = detect_price_changes(
        current_by_id,
        previous_by_id,
    )

    for change in price_changes:
        listing = change["listing"]

        print()
        print("PRICE CHANGED")
        print("ID:", listing["id"])
        print("Title:", listing["title"])
        print("Old price:", change["old_price"])
        print("New price:", change["new_price"])
        print("City:", listing["city"])

        save_event(
            "PRICE_CHANGED",
            listing["id"],
            listing["title"],
            change["old_price"],
            change["new_price"],
            listing["city"],
        )

    # Save the current snapshot only after collection and comparison.
    for listing in current_by_id.values():
        save_listing(listing)

    print("Database updated.")


if __name__ == "__main__":
    main()
