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

    if old_price < 0 or new_price < 0:
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