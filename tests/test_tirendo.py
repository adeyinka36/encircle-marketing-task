from pathlib import Path

from tirendo import listing_url, parse_listing

FIXTURE = Path(__file__).parent / "fixtures" / "tirendo_card.html"


def test_listing_url_includes_size_and_page():
    first_page = listing_url("205/55R16", 1)
    second_page = listing_url("205/55R16", 2)
    assert "width=205" in first_page
    assert "profile=55" in first_page
    assert "size=16" in first_page
    assert "pageNoFull=2" in second_page


def test_parse_listing_reads_product_card():
    tyres = parse_listing(FIXTURE.read_text())
    assert len(tyres) == 1
    tyre = tyres[0]
    assert tyre.brand == "TBB Tires"
    assert tyre.pattern == "Fortezza"
    assert tyre.width == 205
    assert tyre.aspect_ratio == 55
    assert tyre.rim_size == 16
    assert tyre.load_index == "91"
    assert tyre.speed_rating == "V"
    assert tyre.price == 40.55
    assert tyre.currency == "EUR"
    assert tyre.season == "summer"
    assert tyre.in_stock is True
    assert tyre.eu_label == "C/B/70"
    assert tyre.source == "tirendo"
    assert str(tyre.url).endswith("/tbb-tires-fortezza-205-55-r16-91v-d-138292.html")
