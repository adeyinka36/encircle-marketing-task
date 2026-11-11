from analyse import brand_gaps, cheapest_listings, compare_prices, product_key
from tests.helpers import make_tyre


def test_same_product_is_cheaper_on_gumi():
    gumi = make_tyre(price=20000.0, source="gumi")
    tirendo = make_tyre(
        url="https://www.tirendo.fr/pneus/michelin-primacy-4",
        source="tirendo",
        currency="EUR",
        price=80.0,
    )
    rows = compare_prices([gumi], [tirendo], eur_to_huf=390)
    assert len(rows) == 1
    assert rows[0]["cheaper_shop"] == "gumi"
    assert rows[0]["tirendo_price_huf"] == 31200.0


def test_product_key_includes_season():
    assert product_key(make_tyre(season="summer")) != product_key(
        make_tyre(season="winter")
    )


def test_cheapest_listings_are_sorted():
    dear = make_tyre(price=30000.0)
    cheap = make_tyre(
        url="https://gumi.hu/tyres/budget",
        brand="Sunny",
        pattern="NP226",
        price=12000.0,
    )
    assert cheapest_listings([dear, cheap], limit=1) == [cheap]


def test_brand_gaps_lists_shop_only_brands():
    gumi = make_tyre(brand="Barum")
    tirendo = make_tyre(
        url="https://www.tirendo.fr/pneus/michelin-primacy-4",
        brand="Michelin",
        source="tirendo",
        currency="EUR",
        price=89.99,
    )
    gaps = brand_gaps([gumi], [tirendo])
    assert {"brand": "Barum", "on_gumi": "yes", "on_tirendo": "no"} in gaps
    assert {"brand": "Michelin", "on_gumi": "no", "on_tirendo": "yes"} in gaps
