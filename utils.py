import re
from collections.abc import Callable
from typing import NamedTuple

from bs4 import BeautifulSoup

from models import Tyre


class TyreSize(NamedTuple):
    width: int
    aspect_ratio: int
    rim_size: int


TYRE_SIZE_PATTERN = re.compile(
    r"^(?P<width>\d{3})\s*/\s*(?P<aspect>\d{2})\s*[ZzRr]*\s*(?P<rim>\d{2})$"
)


def parse_tyre_size(value: str) -> TyreSize:
    match = TYRE_SIZE_PATTERN.match(value.strip())
    if match is None:
        raise ValueError(f"Could not parse tyre size: {value!r}")
    return TyreSize(
        width=int(match["width"]),
        aspect_ratio=int(match["aspect"]),
        rim_size=int(match["rim"]),
    )


def parse_price(value: str | int | float | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalise_season(value: str | None) -> str | None:
    if not value or value == "undefined":
        return None
    text = value.strip().lower()
    if any(
        token in text
        for token in (
            "all season",
            "all_season",
            "toutes saisons",
            "négyévszakos",
            "negyevszakos",
        )
    ):
        return "all_season"
    if any(token in text for token in ("winter", "hiver", "téli", "teli")):
        return "winter"
    if any(token in text for token in ("summer", "été", "nyári", "nyari")):
        return "summer"
    return None


def format_eu_label(fuel, wet, noise) -> str | None:
    parts = [
        str(part).strip()
        for part in (fuel, wet, noise)
        if part not in (None, "", "undefined")
    ]
    return "/".join(parts) if parts else None


def parse_cards(
    html: str,
    selector: str,
    from_card: Callable[..., Tyre | None],
) -> list[Tyre]:
    soup = BeautifulSoup(html, "html.parser")
    return [
        tyre
        for tyre in (from_card(card) for card in soup.select(selector))
        if tyre is not None
    ]
