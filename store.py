import csv
import sqlite3
from pathlib import Path

from models import Tyre

DB_PATH = Path("data/tyres.sqlite")
GUMI_CSV_PATH = Path("data/gumi.csv")
TIRENDO_CSV_PATH = Path("data/tirendo.csv")

CSV_COLUMNS = [
    "url",
    "brand",
    "pattern",
    "width",
    "aspect_ratio",
    "rim_size",
    "load_index",
    "speed_rating",
    "price",
    "currency",
    "season",
    "in_stock",
    "eu_label",
    "source",
]

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS tyres (
    url TEXT PRIMARY KEY,
    brand TEXT NOT NULL,
    pattern TEXT NOT NULL,
    width INTEGER NOT NULL,
    aspect_ratio INTEGER NOT NULL,
    rim_size INTEGER NOT NULL,
    load_index TEXT,
    speed_rating TEXT,
    price REAL,
    currency TEXT,
    season TEXT,
    in_stock INTEGER,
    eu_label TEXT,
    source TEXT NOT NULL
);
"""

_UPSERT = """
INSERT INTO tyres (
    url, brand, pattern, width, aspect_ratio, rim_size,
    load_index, speed_rating, price, currency, season, in_stock, eu_label, source
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(url) DO UPDATE SET
    brand = excluded.brand,
    pattern = excluded.pattern,
    width = excluded.width,
    aspect_ratio = excluded.aspect_ratio,
    rim_size = excluded.rim_size,
    load_index = excluded.load_index,
    speed_rating = excluded.speed_rating,
    price = excluded.price,
    currency = excluded.currency,
    season = excluded.season,
    in_stock = excluded.in_stock,
    eu_label = excluded.eu_label,
    source = excluded.source;
"""


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path: Path = DB_PATH) -> None:
    with connect(db_path) as connection:
        connection.execute(_CREATE_TABLE)
        connection.commit()


def _row(tyre: Tyre) -> tuple:
    data = tyre.model_dump(mode="json")
    return tuple(data[name] for name in CSV_COLUMNS)


def save_tyres(tyres: list[Tyre], db_path: Path = DB_PATH) -> int:
    init_db(db_path)
    with connect(db_path) as connection:
        connection.executemany(_UPSERT, [_row(tyre) for tyre in tyres])
        connection.commit()
    return len(tyres)


def load_tyres(db_path: Path = DB_PATH) -> list[Tyre]:
    init_db(db_path)
    with connect(db_path) as connection:
        rows = connection.execute("SELECT * FROM tyres").fetchall()
    return [Tyre(**dict(row)) for row in rows]


def write_rows(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_csv(tyres: list[Tyre], path: Path) -> None:
    write_rows(path, [tyre.model_dump(mode="json") for tyre in tyres], CSV_COLUMNS)
