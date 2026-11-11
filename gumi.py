import json
import time
from urllib.parse import urlencode, urljoin

import requests
from pydantic import ValidationError

from models import Tyre
from store import GUMI_CSV_PATH, save_tyres, write_csv
from utils import format_eu_label, normalise_season, parse_cards, parse_price, parse_tyre_size

BASE_URL = "https://gumi.hu"
TARGET_SIZE = "205/55R16"
REQUEST_DELAY_SECONDS = 1.5
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def listing_url(tyre_size: str, page: int) -> str:
    params: dict[str, str | int] = {"query": tyre_size}
    if page > 1:
        params["page"] = page
    return f"{BASE_URL}/products/search/keyword?{urlencode(params)}"


def _season(card, data) -> str | None:
    season = normalise_season(str(data.get("category") or ""))
    if season:
        return season
    if card.select_one(".season-NEGY"):
        return "all_season"
    if card.select_one(".season-T"):
        return "winter"
    if card.select_one(".season-N"):
        return "summer"
    return None


def tyre_from_card(card) -> Tyre | None:
    payload = card.get("data-json")
    link = card.select_one("a.product-link")
    if not payload or link is None or not link.get("href"):
        return None

    try:
        data = json.loads(payload)
        brand = str(data.get("brand") or "").strip()
        name = str(data.get("name") or "").strip()
        if not brand or not name:
            return None

        pattern = (
            name[len(brand) :].strip()
            if name.lower().startswith(brand.lower())
            else name
        )
        load_index = data.get("load_index")
        speed_index = data.get("speed_index")
        stock = data.get("stock")
        in_stock = None
        if stock not in (None, "", "undefined"):
            in_stock = int(stock) > 0
        return Tyre(
            url=urljoin(BASE_URL, link["href"]),
            brand=brand,
            pattern=pattern,
            width=int(data["width"]),
            aspect_ratio=int(data["sidewall"]),
            rim_size=int(data["diameter"]),
            load_index=str(load_index) if load_index else None,
            speed_rating=str(speed_index) if speed_index else None,
            price=parse_price(data.get("price")),
            currency="HUF",
            season=_season(card, data),
            in_stock=in_stock,
            eu_label=format_eu_label(
                data.get("fuel_efficiency"),
                data.get("wet_breaking"),
                data.get("noise"),
            ),
            source="gumi",
        )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError, ValidationError):
        return None


def parse_listing(html: str) -> list[Tyre]:
    return parse_cards(html, ".product-card", tyre_from_card)


def scrape_gumi(tyre_size: str = TARGET_SIZE) -> list[Tyre]:
    parse_tyre_size(tyre_size)
    session = requests.Session()
    session.headers.update(HEADERS)
    found: dict[str, Tyre] = {}
    page = 1

    while True:
        if page > 1:
            time.sleep(REQUEST_DELAY_SECONDS)
        response = session.get(listing_url(tyre_size, page), timeout=30)
        response.raise_for_status()
        new_on_page = 0
        for tyre in parse_listing(response.text):
            url = str(tyre.url)
            if url not in found:
                found[url] = tyre
                new_on_page += 1
        if new_on_page == 0:
            break
        page += 1

    return list(found.values())


def main() -> None:
    tyres = scrape_gumi()
    save_tyres(tyres)
    write_csv(tyres, GUMI_CSV_PATH)
    print(f"Saved {len(tyres)} tyres from gumi.hu")


if __name__ == "__main__":
    main()
