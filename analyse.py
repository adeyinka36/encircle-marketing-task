import os
from pathlib import Path

from models import Tyre
from store import DB_PATH, load_tyres, write_rows

EUR_TO_HUF = float(os.getenv("EUR_TO_HUF", "390"))
CHEAPEST_COUNT = 10

# When there are same tyre on both shops, prices in HUF so you can see who is cheaper
COMPARISON_CSV = Path("data/price_comparison.csv")
# Lowest-priced listings from each shop
CHEAPEST_CSV = Path("data/cheapest.csv")
# Brands that only appear on one shop
BRAND_GAPS_CSV = Path("data/brand_gaps.csv")

COMPARISON_FIELDS = [
    "brand",
    "pattern",
    "size",
    "load_index",
    "speed_rating",
    "gumi_price_huf",
    "tirendo_price_eur",
    "tirendo_price_huf",
    "cheaper_shop",
    "gumi_url",
    "tirendo_url",
    "eur_to_huf",
]


def product_key(tyre: Tyre) -> tuple:
    return (
        tyre.brand.strip().lower(),
        tyre.pattern.strip().lower(),
        tyre.width,
        tyre.aspect_ratio,
        tyre.rim_size,
        (tyre.season or "").strip().lower(),
        (tyre.load_index or "").strip(),
        (tyre.speed_rating or "").strip().upper(),
    )


def cheapest_by_product(tyres: list[Tyre]) -> dict[tuple, Tyre]:
    best: dict[tuple, Tyre] = {}
    for tyre in tyres:
        if tyre.price is None:
            continue
        key = product_key(tyre)
        current = best.get(key)
        if current is None or tyre.price < current.price:
            best[key] = tyre
    return best


def compare_prices(
    gumi_tyres: list[Tyre],
    tirendo_tyres: list[Tyre],
    eur_to_huf: float = EUR_TO_HUF,
) -> list[dict]:
    gumi_best = cheapest_by_product(gumi_tyres)
    tirendo_best = cheapest_by_product(tirendo_tyres)
    rows = []
    for key in sorted(set(gumi_best) & set(tirendo_best)):
        gumi = gumi_best[key]
        tirendo = tirendo_best[key]
        gumi_huf = gumi.price
        tirendo_huf = tirendo.price * eur_to_huf
        if gumi_huf < tirendo_huf:
            cheaper = "gumi"
        elif tirendo_huf < gumi_huf:
            cheaper = "tirendo"
        else:
            cheaper = "same"
        rows.append(
            {
                "brand": gumi.brand,
                "pattern": gumi.pattern,
                "size": f"{gumi.width}/{gumi.aspect_ratio}R{gumi.rim_size}",
                "load_index": gumi.load_index or "",
                "speed_rating": gumi.speed_rating or "",
                "gumi_price_huf": gumi_huf,
                "tirendo_price_eur": tirendo.price,
                "tirendo_price_huf": round(tirendo_huf, 2),
                "cheaper_shop": cheaper,
                "gumi_url": str(gumi.url),
                "tirendo_url": str(tirendo.url),
                "eur_to_huf": eur_to_huf,
            }
        )
    return rows


def cheapest_listings(tyres: list[Tyre], limit: int = CHEAPEST_COUNT) -> list[Tyre]:
    priced = [tyre for tyre in tyres if tyre.price is not None]
    priced.sort(key=lambda tyre: tyre.price)
    return priced[:limit]


def brand_gaps(gumi_tyres: list[Tyre], tirendo_tyres: list[Tyre]) -> list[dict]:
    gumi_brands = {tyre.brand.strip() for tyre in gumi_tyres}
    tirendo_brands = {tyre.brand.strip() for tyre in tirendo_tyres}
    rows = []
    for brand in sorted(gumi_brands - tirendo_brands):
        rows.append({"brand": brand, "on_gumi": "yes", "on_tirendo": "no"})
    for brand in sorted(tirendo_brands - gumi_brands):
        rows.append({"brand": brand, "on_gumi": "no", "on_tirendo": "yes"})
    return rows


def main() -> None:
    tyres = load_tyres(DB_PATH)
    gumi_tyres = [tyre for tyre in tyres if tyre.source == "gumi"]
    tirendo_tyres = [tyre for tyre in tyres if tyre.source == "tirendo"]

    if not gumi_tyres or not tirendo_tyres:
        print("Need listings from both shops in data/tyres.sqlite.")
        print("Run gumi.py and tirendo.py first.")
        return

    comparison = compare_prices(gumi_tyres, tirendo_tyres)
    cheapest = cheapest_listings(gumi_tyres) + cheapest_listings(tirendo_tyres)
    gaps = brand_gaps(gumi_tyres, tirendo_tyres)

    write_rows(COMPARISON_CSV, comparison, COMPARISON_FIELDS)
    write_rows(
        CHEAPEST_CSV,
        [
            {
                "source": tyre.source,
                "brand": tyre.brand,
                "pattern": tyre.pattern,
                "price": tyre.price,
                "currency": tyre.currency,
                "url": str(tyre.url),
            }
            for tyre in cheapest
        ],
        ["source", "brand", "pattern", "price", "currency", "url"],
    )
    write_rows(BRAND_GAPS_CSV, gaps, ["brand", "on_gumi", "on_tirendo"])

    print(f"Compared {len(comparison)} matching products ({EUR_TO_HUF:g} HUF per EUR).")
    print(f"Wrote {COMPARISON_CSV}")
    print(f"Wrote {CHEAPEST_CSV} (cheapest {CHEAPEST_COUNT} per shop)")
    print(f"Wrote {BRAND_GAPS_CSV} ({len(gaps)} brands on one shop only)")


if __name__ == "__main__":
    main()
