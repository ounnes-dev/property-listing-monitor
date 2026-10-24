
import csv
import time

import requests


API_URL = "https://api.ouedkniss.com/graphql"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
}

PAGE_SIZE = 10
REQUEST_TIMEOUT = 20

QUERY = """
query SearchAnnouncementsQuery($filter: SearchAnnouncementsFilterInput, $page: Int, $limit: Int) {
    search: searchAnnouncements(filter: $filter, page: $page, limit: $limit) {
        announcements {
            data {
                id
                title
                price
                createdAt
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
    """Guess whether a property listing is for sale or rent."""
    title = (title or "").lower()

    rental_keywords = (
        "location",
        "loue",
        "louer",
        "à louer",
        "a louer",
        "للإيجار",
        "للكراء",
    )

    sale_keywords = (
        "vente",
        "vendre",
        "à vendre",
        "a vendre",
        "للبيع",
    )

    if any(keyword in title for keyword in rental_keywords):
        return "rent"

    if any(keyword in title for keyword in sale_keywords):
        return "sale"

    return "unknown"


def _extract_search_result(response_json):
    """Validate and extract the search result from the API response."""
    if not isinstance(response_json, dict):
        raise RuntimeError("The API returned an invalid response.")

    if response_json.get("errors"):
        raise RuntimeError(
            f"GraphQL error: {response_json['errors']}"
        )

    data = response_json.get("data") or {}
    search = data.get("search") or {}
    announcements = search.get("announcements") or {}

    if not isinstance(announcements, dict):
        raise RuntimeError("Unexpected announcements response format.")

    listings = announcements.get("data")
    pagination = announcements.get("paginatorInfo")

    if not isinstance(listings, list):
        raise RuntimeError("The API response did not contain a listings list.")

    if not isinstance(pagination, dict):
        raise RuntimeError("The API response did not contain pagination information.")

    return listings, pagination


def _request_page(page):
    """Request one page and fail explicitly if the request is unsuccessful."""
    variables = {
        "filter": {
            "categorySlug": "immobilier",
            "query": "mostaganem",
        },
        "page": page,
        "limit": PAGE_SIZE,
    }

    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={
                "operationName": "SearchAnnouncementsQuery",
                "query": QUERY,
                "variables": variables,
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        response_json = response.json()

    except (requests.RequestException, ValueError) as error:
        raise RuntimeError(
            f"Failed to collect page {page}: {error}"
        ) from error

    try:
        return _extract_search_result(response_json)
    except (KeyError, TypeError, RuntimeError) as error:
        raise RuntimeError(
            f"Failed to process page {page}: {error}"
        ) from error


def _normalise_listing(listing):
    """Convert an API listing into the format used by the project."""
    if not isinstance(listing, dict) or listing.get("id") is None:
        return None

    cities = listing.get("cities") or []
    city = ""

    if cities and isinstance(cities[0], dict):
        city = cities[0].get("name", "")

    price = listing.get("price")

    if price in ("", None):
        price = None

    return {
        "id": str(listing["id"]),
        "title": listing.get("title") or "",
        "createdAt": listing.get("createdAt") or "",
        "price": price,
        "slug": listing.get("slug") or "",
        "cities": [{"name": city}] if city else [],
        "city": city,
        "transaction_type": get_transaction_type(
            listing.get("title", "")
        ),
    }


def collect_listings(max_pages=None, delay_seconds=0.5):
    """
    Collect property listings from Ouedkniss.

    max_pages=None collects all pages reported by the API.
    Set max_pages to a positive integer for a limited test run.

    If any page fails, raise RuntimeError instead of returning
    an incomplete result that could be mistaken for a full collection.
    """
    if max_pages is not None and (
        not isinstance(max_pages, int)
        or isinstance(max_pages, bool)
        or max_pages < 1
    ):
        raise ValueError("max_pages must be a positive integer or None.")

    if delay_seconds < 0:
        raise ValueError("delay_seconds cannot be negative.")

    # Initial request obtains pagination information.
    _, pagination = _request_page(1)

    try:
        last_page = int(pagination.get("lastPage", 1))
    except (TypeError, ValueError) as error:
        raise RuntimeError("The API returned an invalid lastPage value.") from error

    if last_page < 1:
        raise RuntimeError("The API returned an invalid page count.")

    pages_to_collect = (
        min(last_page, max_pages)
        if max_pages is not None
        else last_page
    )

    listings_by_id = {}

    for page in range(1, pages_to_collect + 1):
        if page > 1:
            time.sleep(delay_seconds)

        page_listings, _ = _request_page(page)

        for raw_listing in page_listings:
            listing = _normalise_listing(raw_listing)

            if listing is not None:
                listings_by_id[listing["id"]] = listing

        print(
            f"Collected page: {page} | "
            f"Listings returned: {len(page_listings)} | "
            f"Unique listings so far: {len(listings_by_id)}"
        )

    listings = list(listings_by_id.values())

    # Save only after every requested page has been collected successfully.
    with open("listings.csv", "w", newline="", encoding="utf-8") as file:
        fieldnames = [
            "id",
            "title",
            "createdAt",
            "price",
            "slug",
            "city",
            "transaction_type",
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for listing in listings:
            writer.writerow({
                "id": listing["id"],
                "title": listing["title"],
                "createdAt": listing["createdAt"],
                "price": listing["price"],
                "slug": listing["slug"],
                "city": listing["city"],
                "transaction_type": listing["transaction_type"],
            })

    print(f"Collection complete. Unique listings: {len(listings)}")

    return listings


if __name__ == "__main__":
    collect_listings(max_pages=3)
