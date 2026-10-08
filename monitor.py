import csv
from datetime import datetime
from collector import collect_listings, get_transaction_type


def log_event(event_type, listing_id, title, old_price, new_price, city):

    with open("events.csv", "a", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        if file.tell() == 0:
            writer.writerow([
                "timestamp",
                "event_type",
                "id",
                "title",
                "old_price",
                "new_price",
                "city"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            event_type,
            listing_id,
            title,
            old_price,
            new_price,
            city
        ])


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


def normalize_price(price):

    if price in ("", None):
        return None

    return float(price)


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


listings = collect_listings()

listings_by_id = {}

for listing in listings:

    listing_id = listing["id"]
    listings_by_id[listing_id] = listing


try:

    with open("previous_listings.csv", "r", encoding="utf-8") as file:

        reader = csv.DictReader(file)
        previous_listings = list(reader)

except FileNotFoundError:

    print()
    print("No previous snapshot found.")
    print("This is the first monitoring run.")

    previous_listings = []


previous_by_id = {}

for listing in previous_listings:

    listing_id = listing["id"]
    previous_by_id[listing_id] = listing


print("Current listings:", len(listings_by_id))
print("Previous listings:", len(previous_by_id))


new_listings = detect_new_listings(
    listings_by_id,
    previous_by_id
)

for listing in new_listings:

    print()
    print("NEW LISTING")
    print("ID:", listing["id"])
    print("Title:", listing["title"])
    print("Price:", listing["price"])
    print("City:", listing["cities"][0]["name"])
    print(
        "Transaction type:",
        get_transaction_type(listing["title"])
    )

    log_event(
        "NEW",
        listing["id"],
        listing["title"],
        "",
        listing["price"],
        listing["cities"][0]["name"]
    )


removed_listings = detect_removed_listings(
    listings_by_id,
    previous_by_id
)

for listing in removed_listings:

    print()
    print("REMOVED LISTING")
    print("ID:", listing["id"])
    print("Title:", listing["title"])
    print("Last known price:", listing["price"])
    print("City:", listing["city"])
    print(
        "Transaction type:",
        listing.get("transaction_type", "unknown")
    )

    log_event(
        "REMOVED",
        listing["id"],
        listing["title"],
        listing["price"],
        "",
        listing["city"]
    )


price_changes = detect_price_changes(
    listings_by_id,
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
    print("City:", listing["cities"][0]["name"])

    log_event(
        "PRICE_CHANGED",
        listing["id"],
        listing["title"],
        change["old_price"],
        change["new_price"],
        listing["cities"][0]["name"]
    )


with open(
    "previous_listings.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "id",
            "title",
            "createdAt",
            "price",
            "slug",
            "city",
            "transaction_type"
        ]
    )

    writer.writeheader()

    for listing in listings:

        writer.writerow({
            "id": listing["id"],
            "title": listing["title"],
            "createdAt": listing["createdAt"],
            "price": listing["price"],
            "slug": listing["slug"],
            "city": listing["cities"][0]["name"],
            "transaction_type": get_transaction_type(
                listing["title"]
            )
        })


print("Previous snapshot updated.")