import pytest

from utils import TyreSize, format_eu_label, normalise_season, parse_price, parse_tyre_size


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("205/55R16", TyreSize(205, 55, 16)),
        ("205/55r16", TyreSize(205, 55, 16)),
        ("205/55 R16", TyreSize(205, 55, 16)),
        ("205/55ZR16", TyreSize(205, 55, 16)),
    ],
)
def test_parse_tyre_size(raw: str, expected: TyreSize):
    assert parse_tyre_size(raw) == expected


def test_parse_tyre_size_rejects_invalid_values():
    with pytest.raises(ValueError):
        parse_tyre_size("not-a-size")


def test_parse_price():
    assert parse_price(29990) == 29990.0
    assert parse_price("29990") == 29990.0
    assert parse_price(None) is None
    assert parse_price("") is None


def test_normalise_season():
    assert normalise_season("All season") == "all_season"
    assert normalise_season("Pneus été") == "summer"
    assert normalise_season("Pneus hiver") == "winter"
    assert normalise_season(None) is None


def test_format_eu_label():
    assert format_eu_label("C", "B", 71) == "C/B/71"
    assert format_eu_label(None, None, None) is None
