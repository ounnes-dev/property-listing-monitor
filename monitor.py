from datetime import datetime

from collector import collect_listings, get_transaction_type
from database import (
    create_tables,
    get_all_listings,
    save_listing,
    save_event
)


def normalize_price(price):

    if price in ("", None):
        return None

    return float(price)


def detect_new_listings(current_listings, previous_listings):

    new_listings = []

    for listing_id in current_listings:

        if listing_id not in previous_listings:
            new_listings.append(current_listings[listing_id])

    return new_listings


def detect_removed_listings(current_listings, previous_listings):

    removed_listings = []

    for listing_id in previous_listings:

        if listing_id not in current_listings:
            removed_listings.append(previous_listings[listing_id])

    return removed_listings


def detect_price_changes(current_listings, previous_listings):

    price_changes = []

    for listing_id in current_listings:

        if listing_id not in previous_listings:
            continue

        current_price = normalize_price(
            current_listings[listing_id]["price"]
        )

        previous_price = normalize_price(
            previous_listings[listing_id]["price"]
        )

        if current_price != previous_price:

            price_changes.append({
                "listing": current_listings[listing_id],
                "old_price": previous_price,
                "new_price": current_price
            })

    return price_changes


create_tables()

listings = collect_listings()

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

current_by_id = {}

for listing in listings:

    listing_id = listing["id"]

    current_by_id[listing_id] = {
        "id": listing["id"],
        "title": listing["title"],
        "created_at": listing["createdAt"],
        "price": normalize_price(listing["price"]),
        "slug": listing["slug"],
        "city": listing["cities"][0]["name"],
        "transaction_type": get_transaction_type(
            listing["title"]
        ),
        "last_seen": current_time
    }


previous_listings = get_all_listings()

previous_by_id = {}

for listing in previous_listings:

    listing_id = listing["id"]

    previous_by_id[listing_id] = listing


print("Current listings:", len(current_by_id))
print("Previous listings:", len(previous_by_id))


new_listings = detect_new_listings(
    current_by_id,
    previous_by_id
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
        current_time
    )


removed_listings = detect_removed_listings(
    current_by_id,
    previous_by_id
)

for listing in removed_listings:

    print()
    print("REMOVED LISTING")
    print("ID:", listing["id"])
    print("Title:", listing["title"])
    print("Last known price:", listing["price"])
    print("City:", listing["city"])
    print("Transaction type:", listing["transaction_type"])

    save_event(
        "REMOVED",
        listing["id"],
        listing["title"],
        listing["price"],
        None,
        listing["city"],
        current_time
    )


price_changes = detect_price_changes(
    current_by_id,
    previous_by_id
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
        current_time
    )


for listing in current_by_id.values():

    save_listing(listing)


print()
print("Database updated.")