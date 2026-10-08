import csv
from search_test import collect_listings


# collect current listings
listings = collect_listings()

listings_by_id = {}

for listing in listings:
    listing_id = listing["id"]
    listings_by_id[listing_id] = listing


# load previous listings
with open("previous_listings.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    previous_listings = list(reader)

previous_by_id = {}

for listing in previous_listings:
    listing_id = listing["id"]
    previous_by_id[listing_id] = listing


print("Current listings:", len(listings_by_id))
print("Previous listings:", len(previous_by_id))


# detect new listings
for listing_id in listings_by_id:

    if listing_id not in previous_by_id:
        print("NEW LISTING:", listing_id)


# detect removed listings
for listing_id in previous_by_id:

    if listing_id not in listings_by_id:
        print("REMOVED LISTING:", listing_id)


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
            print(
                "PRICE CHANGED:",
                listing_id,
                "|",
                previous_price,
                "->",
                current_price
            )


# save current listings as the new previous snapshot
with open("previous_listings.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["id", "title", "createdAt", "price", "slug", "city"]
    )

    writer.writeheader()

    for listing in listings:
        writer.writerow({
            "id": listing["id"],
            "title": listing["title"],
            "createdAt": listing["createdAt"],
            "price": listing["price"],
            "slug": listing["slug"],
            "city": listing["cities"][0]["name"]
        })

print("Previous snapshot updated.")