from collector import get_transaction_type


def test_sale_listing():
    assert get_transaction_type("Vente Villa Mostaganem") == "sale"


def test_rent_listing():
    assert get_transaction_type("Location Appartement F3 Mostaganem") == "rent"


def test_unknown_listing():
    assert get_transaction_type("Appartement Mostaganem") == "unknown"