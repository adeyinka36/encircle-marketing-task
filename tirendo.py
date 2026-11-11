import re
import time
from urllib.parse import urlencode, urljoin

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright
from pydantic import ValidationError

from models import Tyre
from store import TIRENDO_CSV_PATH, save_tyres, write_csv
from utils import format_eu_label, normalise_season, parse_cards, parse_price, parse_tyre_size

BASE_URL = "https://www.tirendo.fr"
TARGET_SIZE = "205/55R16"
REQUEST_DELAY_SECONDS = 1.5

SPEC_PATTERN = re.compile(
    r"(?P<width>\d{3})/(?P<aspect>\d{2})\s*R(?P<rim>\d{2})"
    r"(?:\s+(?P<load>\d{2,3})(?P<speed>[A-Z]))?",
    re.I,
)


def listing_url(tyre_size: str, page: int) -> str:
    size = parse_tyre_size(tyre_size)
    params: dict[str, str | int] = {
        "width": size.width,
        "profile": size.aspect_ratio,
        "size": size.rim_size,
        "vehicleTypes": "PKW",
        "itemsPerPage": 28,
    }
    if page > 1:
        params["pageNoFull"] = page
    return f"{BASE_URL}/search?{urlencode(params)}"


def tyre_from_card(card) -> Tyre | None:
    title = card.select_one(".product-list-title")
    spec = card.select_one(".result-list-prod-size")
    price = card.select_one("[itemprop=price]")
    if title is None or spec is None:
        return None

    brand_el = title.select_one("div span")
    pattern_el = title.select_one("a span")
    link = title.select_one("a")
    if brand_el is None or pattern_el is None or link is None or not link.get("href"):
        return None

    match = SPEC_PATTERN.search(spec.get_text(" ", strip=True))
    if match is None:
        return None

    fuel = card.select_one(".result-list-prod-rating-eff span")
    wet = card.select_one(".result-list-prod-rating-adh span")
    noise = card.select_one(".result-list-prod-rating-noise span")
    availability = card.select_one("[itemprop=availability]")
    in_stock = None
    if availability is not None:
        in_stock = "OutOfStock" not in (availability.get("content") or "")
    elif card.select_one(".limited-stock"):
        in_stock = True

    try:
        return Tyre(
            url=urljoin(BASE_URL, link["href"]),
            brand=brand_el.get_text(strip=True),
            pattern=pattern_el.get_text(strip=True),
            width=int(match["width"]),
            aspect_ratio=int(match["aspect"]),
            rim_size=int(match["rim"]),
            load_index=match["load"],
            speed_rating=match["speed"].upper() if match["speed"] else None,
            price=parse_price(price.get("content") if price else None),
            currency="EUR",
            season=normalise_season(card.get_text(" ", strip=True)),
            in_stock=in_stock,
            eu_label=format_eu_label(
                fuel.get_text(strip=True) if fuel else None,
                wet.get_text(strip=True) if wet else None,
                noise.get_text(strip=True) if noise else None,
            ),
            source="tirendo",
        )
    except (TypeError, ValueError, ValidationError):
        return None


def parse_listing(html: str) -> list[Tyre]:
    return parse_cards(html, ".product-item", tyre_from_card)


def _accept_cookies(page) -> None:
    try:
        page.get_by_role("button", name="Accept all").click(timeout=3000)
    except PlaywrightTimeout:
        pass


def scrape_tirendo(tyre_size: str = TARGET_SIZE) -> list[Tyre]:
    parse_tyre_size(tyre_size)
    found: dict[str, Tyre] = {}
    page_number = 1

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            while True:
                if page_number > 1:
                    time.sleep(REQUEST_DELAY_SECONDS)
                page.goto(
                    listing_url(tyre_size, page_number),
                    wait_until="domcontentloaded",
                )
                _accept_cookies(page)
                try:
                    page.wait_for_selector(".product-item", timeout=15000)
                except PlaywrightTimeout:
                    break
                new_on_page = 0
                for tyre in parse_listing(page.content()):
                    url = str(tyre.url)
                    if url not in found:
                        found[url] = tyre
                        new_on_page += 1
                if new_on_page == 0:
                    break
                page_number += 1
        finally:
            browser.close()

    return list(found.values())


def main() -> None:
    tyres = scrape_tirendo()
    save_tyres(tyres)
    write_csv(tyres, TIRENDO_CSV_PATH)
    print(f"Saved {len(tyres)} tyres from tirendo.fr")


if __name__ == "__main__":
    main()
