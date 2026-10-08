import csv
from datetime import datetime
from search_test import collect_listings, get_transaction_type


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


# collect current listings
listings = collect_listings()

listings_by_id = {}

for listing in listings:
    listing_id = listing["id"]
    listings_by_id[listing_id] = listing



# load previous listings
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


# detect new listings
for listing_id in listings_by_id:

    if listing_id not in previous_by_id:

        listing = listings_by_id[listing_id]

        print()
        print("NEW LISTING")
        print("ID:", listing["id"])
        print("Title:", listing["title"])
        print("Price:", listing["price"])
        print("City:", listing["cities"][0]["name"])
        print("Transaction type:", get_transaction_type(listing["title"]))

        log_event(
            "NEW",
            listing["id"],
            listing["title"],
            "",
            listing["price"],
            listing["cities"][0]["name"]
        )


# detect removed listings
for listing_id in previous_by_id:

    if listing_id not in listings_by_id:

        listing = previous_by_id[listing_id]

        print()
        print("REMOVED LISTING")
        print("ID:", listing["id"])
        print("Title:", listing["title"])
        print("Last known price:", listing["price"])
        print("City:", listing["city"])
        print("Transaction type:", listing.get("transaction_type", "unknown"))

        log_event(
            "REMOVED",
            listing["id"],
            listing["title"],
            listing["price"],
            "",
            listing["city"]
        )


# detect price changes
for listing_id in listings_by_id:

    if listing_id in previous_by_id:

        current_price = listings_by_id[listing_id]["price"]
        previous_price = previous_by_id[listing_id]["price"]

        if current_price in ("", None):
            current_price = None
        else:
            current_price = float(current_price)

        if previous_price in ("", None):
            previous_price = None
        else:
            previous_price = float(previous_price)

        if current_price != previous_price:

            listing = listings_by_id[listing_id]

            print()
            print("PRICE CHANGED")
            print("ID:", listing["id"])
            print("Title:", listing["title"])
            print("Old price:", previous_price)
            print("New price:", current_price)
            print("City:", listing["cities"][0]["name"])

            log_event(
                "PRICE_CHANGED",
                listing["id"],
                listing["title"],
                previous_price,
                current_price,
                listing["cities"][0]["name"]
            )


# save current listings as the new previous snapshot
with open("previous_listings.csv", "w", newline="", encoding="utf-8") as file:

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
            "transaction_type": get_transaction_type(listing["title"])
        })


print("Previous snapshot updated.")

