import csv
from pathlib import Path

from store import CSV_COLUMNS, connect, init_db, load_tyres, save_tyres, write_csv
from tests.helpers import make_tyre


def test_init_db_creates_tyres_table_with_expected_columns(db_path: Path):
    init_db(db_path)

    with connect(db_path) as connection:
        columns = [
            row["name"]
            for row in connection.execute("PRAGMA table_info(tyres)").fetchall()
        ]

    assert columns == CSV_COLUMNS


def test_save_then_load_returns_the_same_listing(db_path: Path):
    tyre = make_tyre()
    save_tyres([tyre], db_path)
    loaded = load_tyres(db_path)
    assert loaded == [tyre]


def test_saving_the_same_url_updates_the_existing_row(db_path: Path):
    save_tyres([make_tyre(price=24990.0)], db_path)
    save_tyres([make_tyre(price=19990.0)], db_path)
    loaded = load_tyres(db_path)
    assert len(loaded) == 1
    assert loaded[0].price == 19990.0


def test_write_csv_matches_tyre_fields(tmp_path: Path):
    tyre = make_tyre()
    csv_path = tmp_path / "gumi.csv"
    write_csv([tyre], csv_path)

    with csv_path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    assert list(rows[0].keys()) == CSV_COLUMNS
    assert rows[0]["url"] == str(tyre.url)
    assert rows[0]["brand"] == tyre.brand
    assert rows[0]["source"] == "gumi"
    assert rows[0]["price"] == "24990.0"
