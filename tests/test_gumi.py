from pathlib import Path

from gumi import listing_url, parse_listing

FIXTURE = Path(__file__).parent / "fixtures" / "gumi_card.html"


def test_listing_url_includes_size_and_page():
    assert listing_url("205/55R16", 1) == (
        "https://gumi.hu/products/search/keyword?query=205%2F55R16"
    )
    assert listing_url("205/55R16", 5).endswith("page=5")


def test_parse_listing_reads_card_json():
    tyres = parse_listing(FIXTURE.read_text())
    assert len(tyres) == 1
    tyre = tyres[0]
    assert tyre.brand == "Dunlop"
    assert tyre.pattern == "Allseason 2"
    assert tyre.width == 205
    assert tyre.aspect_ratio == 55
    assert tyre.rim_size == 16
    assert tyre.load_index == "91"
    assert tyre.speed_rating == "V"
    assert tyre.price == 29990.0
    assert tyre.currency == "HUF"
    assert tyre.season == "all_season"
    assert tyre.in_stock is True
    assert tyre.eu_label == "C/B/71"
    assert str(tyre.url).endswith("/autogumi/negyevszakos/dunlop/205/55r16/allseason-2")
