from analytics import calculate_price_change


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