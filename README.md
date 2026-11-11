# Encircle Marketing tyre scrape

Scrapes 205/55R16 tyres from gumi.hu and tirendo.fr, saves them to CSV (and SQLite), and can compare prices.

gumi.py uses requests and Beautiful Soup. tirendo.py uses Playwright then Beautiful Soup because that site builds the listing in the browser. Playwright was easier to set up than Selenium (one install for Chromium, and it can wait for the products to show up).

Shared bits:
- models.py is the Tyre object
- utils.py has size/price/season helpers
- store.py writes CSV and SQLite
- analyse.py is extra. It matches the same product on both shops and compares prices in HUF.

Run gumi.py then tirendo.py. You get data/gumi.csv, data/tirendo.csv and data/tyres.sqlite.

analyse.py needs both shops in the sqlite file. It writes data/price_comparison.csv (same tyre, who is cheaper), data/cheapest.csv (lowest prices on each shop) and data/brand_gaps.csv (brands only on one shop).

The brief asked for url, brand, pattern, width, aspect ratio, rim size, load index, speed rating and price.

I also kept currency (HUF vs EUR), source (which shop), season, whether it is in stock, and the EU label (fuel/wet/noise, like C/B/71). Season is used when matching products so a summer and winter tyre of the same size are not treated as the same thing.

Setup (Python 3.14+):

```
uv sync --dev
uv run playwright install chromium
cp .env.example .env
```

.env is optional. EUR_TO_HUF is only for analyse.py (default 390).

```
uv run python gumi.py
uv run python tirendo.py
uv run python analyse.py
uv run pytest -v
```
