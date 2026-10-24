import math
from statistics import median


def calculate_price_change(old_price, new_price):
    """
    Calculate the absolute and percentage change between two prices.

    Returns None when either price is missing or invalid.
    Percentage change is undefined when the old price is zero.
    """

    if old_price in ("", None) or new_price in ("", None):
        return None

    try:
        old_price = float(old_price)
        new_price = float(new_price)
    except (TypeError, ValueError):
        return None

    if (
        not math.isfinite(old_price)
        or not math.isfinite(new_price)
        or old_price < 0
        or new_price < 0
    ):
        return None

    difference = new_price - old_price

    if difference > 0:
        direction = "increase"
    elif difference < 0:
        direction = "decrease"
    else:
        direction = "unchanged"

    if old_price == 0:
        percentage_change = None
    else:
        percentage_change = (difference / old_price) * 100

    return {
        "old_price": old_price,
        "new_price": new_price,
        "difference": difference,
        "percentage_change": percentage_change,
        "direction": direction,
    }


def _valid_market_price(value):
    """Return a positive finite price as a float, or None."""

    if value in ("", None):
        return None

    try:
        price = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(price) or price <= 0:
        return None

    return price


def _summarize_group(group_listings):
    """Calculate listing and price statistics for one group."""

    prices = [
        price
        for listing in group_listings
        if (price := _valid_market_price(listing.get("price"))) is not None
    ]

    average_price = (
        sum(prices) / len(prices)
        if prices
        else None
    )

    median_price = median(prices) if prices else None

    return {
        "listing_count": len(group_listings),
        "priced_listing_count": len(prices),
        "average_price": average_price,
        "median_price": median_price,
    }


def calculate_market_analytics(listings):
    """
    Summarize advertised listing prices by city and transaction type.

    Only positive, finite prices are included in price statistics.
    Listings with missing or invalid prices still count as listings.
    """

    listings = list(listings)

    by_city = {}
    by_transaction_type = {}

    for listing in listings:
        city = str(listing.get("city") or "Unknown").strip() or "Unknown"

        transaction_type = (
            str(listing.get("transaction_type") or "unknown")
            .strip()
            .lower()
        )

        by_city.setdefault(city, []).append(listing)
        by_transaction_type.setdefault(
            transaction_type, []
        ).append(listing)

    city_results = [
        {
            "city": city,
            **_summarize_group(city_listings),
        }
        for city, city_listings in by_city.items()
    ]

    transaction_results = [
        {
            "transaction_type": transaction_type,
            **_summarize_group(group_listings),
        }
        for transaction_type, group_listings
        in by_transaction_type.items()
    ]

    # Put groups with the most listings first.
    city_results.sort(
        key=lambda item: item["listing_count"],
        reverse=True,
    )

    transaction_results.sort(
        key=lambda item: item["listing_count"],
        reverse=True,
    )

    overall = _summarize_group(listings)

    return {
        "total_listings": overall["listing_count"],
        "priced_listings": overall["priced_listing_count"],
        "average_price": overall["average_price"],
        "median_price": overall["median_price"],
        "by_city": city_results,
        "by_transaction_type": transaction_results,
    }
