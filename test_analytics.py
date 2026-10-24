from analytics import (
    calculate_price_change,
    calculate_market_analytics,
)



def test_price_decrease():
    result = calculate_price_change(20_000_000, 18_000_000)

    assert result["difference"] == -2_000_000
    assert result["percentage_change"] == -10
    assert result["direction"] == "decrease"


def test_price_increase():
    result = calculate_price_change(10_000_000, 12_000_000)

    assert result["difference"] == 2_000_000
    assert result["percentage_change"] == 20
    assert result["direction"] == "increase"


def test_unchanged_price():
    result = calculate_price_change(5_000_000, 5_000_000)

    assert result["difference"] == 0
    assert result["percentage_change"] == 0
    assert result["direction"] == "unchanged"


def test_missing_price():
    assert calculate_price_change(None, 10_000_000) is None
    assert calculate_price_change(10_000_000, None) is None


def test_zero_old_price():
    result = calculate_price_change(0, 100)

    assert result["difference"] == 100
    assert result["percentage_change"] is None
    assert result["direction"] == "increase"


def test_invalid_or_negative_prices():
    assert calculate_price_change("unknown", 100) is None
    assert calculate_price_change(-100, 200) is None

def test_market_analytics_groups_listings_by_city():
    listings = [
        {
            "city": "Oran",
            "transaction_type": "sale",
            "price": 10_000_000,
        },
        {
            "city": "Oran",
            "transaction_type": "sale",
            "price": 20_000_000,
        },
        {
            "city": "Mostaganem",
            "transaction_type": "rent",
            "price": 30_000,
        },
    ]

    result = calculate_market_analytics(listings)

    assert result["total_listings"] == 3
    assert result["priced_listings"] == 3

    oran = next(
        item for item in result["by_city"]
        if item["city"] == "Oran"
    )

    assert oran["listing_count"] == 2
    assert oran["average_price"] == 15_000_000
    assert oran["median_price"] == 15_000_000


def test_market_analytics_groups_by_transaction_type():
    listings = [
        {
            "city": "Oran",
            "transaction_type": "sale",
            "price": 10_000_000,
        },
        {
            "city": "Oran",
            "transaction_type": "sale",
            "price": 20_000_000,
        },
        {
            "city": "Oran",
            "transaction_type": "rent",
            "price": 30_000,
        },
    ]

    result = calculate_market_analytics(listings)

    sale = next(
        item for item in result["by_transaction_type"]
        if item["transaction_type"] == "sale"
    )

    rent = next(
        item for item in result["by_transaction_type"]
        if item["transaction_type"] == "rent"
    )

    assert sale["listing_count"] == 2
    assert sale["average_price"] == 15_000_000

    assert rent["listing_count"] == 1
    assert rent["average_price"] == 30_000


def test_market_analytics_excludes_invalid_prices():
    listings = [
        {"city": "Oran", "transaction_type": "sale", "price": 100},
        {"city": "Oran", "transaction_type": "sale", "price": None},
        {"city": "Oran", "transaction_type": "sale", "price": "unknown"},
        {"city": "Oran", "transaction_type": "sale", "price": -50},
        {"city": "Oran", "transaction_type": "sale", "price": 0},
    ]

    result = calculate_market_analytics(listings)

    assert result["total_listings"] == 5
    assert result["priced_listings"] == 1
    assert result["average_price"] == 100


def test_market_analytics_handles_empty_listings():
    result = calculate_market_analytics([])

    assert result["total_listings"] == 0
    assert result["priced_listings"] == 0
    assert result["average_price"] is None
    assert result["median_price"] is None
    assert result["by_city"] == []
    assert result["by_transaction_type"] == []


def test_market_analytics_counts_listings_without_prices():
    listings = [
        {
            "city": "Oran",
            "transaction_type": "sale",
            "price": None,
        },
        {
            "city": "Oran",
            "transaction_type": "sale",
            "price": 200,
        },
    ]

    result = calculate_market_analytics(listings)

    oran = result["by_city"][0]

    assert oran["listing_count"] == 2
    assert oran["priced_listing_count"] == 1
    assert oran["average_price"] == 200
