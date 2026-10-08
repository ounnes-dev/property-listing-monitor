import requests
import csv

url = "https://api.ouedkniss.com/graphql"

query = """
query SearchAnnouncementsQuery($q: String, $filter: SearchFilterInput) {
    search(q: $q, filter: $filter) {
        announcements {
            data {
                id
                title
                createdAt
                price
                slug
                cities {
                    id
                    name
                }
            }

            paginatorInfo {
                lastPage
                hasMorePages
            }
        }
    }
}
"""


def get_transaction_type(title):

    title = title.lower()

    if "vente" in title:
        return "sale"

    if "location" in title:
        return "rent"

    return "unknown"


def get_announcements(result):

    if "errors" in result:

        print("API returned an error:")
        print(result["errors"])

        return None

    if "data" not in result:
        print("Unexpected API response.")
        return None

    if result["data"] is None:
        print("API returned no data.")
        return None

    if "search" not in result["data"]:
        print("Search data missing from API response.")
        return None

    if result["data"]["search"] is None:
        print("Search returned no results.")
        return None

    if "announcements" not in result["data"]["search"]:
        print("Announcements data missing from API response.")
        return None

    return result["data"]["search"]["announcements"]



def collect_listings():

    all_listings = []

    max_pages = 5

    # First request: discover how many pages exist
    page = 1

    variables = {
        "filter": {
            "categorySlug": None,
            "origin": None,
            "connected": False,
            "delivery": None,
            "regionIds": [],
            "cityIds": [],
            "page": page
        },
        "q": "mostaganem"
    }

    data = {
        "operationName": "SearchAnnouncementsQuery",
        "variables": variables,
        "query": query
    }

    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()

    except requests.RequestException as error:
        print("Request failed:", error)
        return []


    announcements = get_announcements(result)

    if announcements is None:
        return []

    last_page = announcements["paginatorInfo"]["lastPage"]

    print("Pages available:", last_page)

    pages_to_collect = min(last_page, max_pages)

    print("Pages we will collect:", pages_to_collect)

    # Collect the pages
    for page in range(1, pages_to_collect + 1):

        variables["filter"]["page"] = page

        data["variables"] = variables

        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()

        except requests.RequestException as error:
            print("Request failed on page", page, ":", error)
            continue

        announcements = get_announcements(result)

        if announcements is None:
            print("Skipping Page", page)
            continue

        listings = announcements["data"]

        all_listings.extend(listings)

        print("Collected page:", page, "| Listings:", len(listings))


    # Check which properties have a price vs those who don't
    priced_listings = []

    for listing in all_listings:

        if listing["price"] is not None:
            priced_listings.append(listing["price"])


    print("Listings with a price:", len(priced_listings))
    print("Listings without a price:", len(all_listings) - len(priced_listings))


    if len(priced_listings) > 0:

        average_price = sum(priced_listings) / len(priced_listings)

        print("Average price:", average_price)


    with open("listings.csv", "w", newline="", encoding="utf-8") as file:

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

        for listing in all_listings:

            price = listing["price"]

            if price is not None:
                price = float(price)

            writer.writerow({
                "id": listing["id"],
                "title": listing["title"],
                "createdAt": listing["createdAt"],
                "price": price,
                "slug": listing["slug"],
                "city": listing["cities"][0]["name"],
                "transaction_type": get_transaction_type(listing["title"])
            })


    print("Total listings:", len(all_listings))

    return all_listings

