from models import Tyre


def make_tyre(**overrides) -> Tyre:
    values = {
        "url": "https://gumi.hu/tyres/michelin-primacy-4",
        "brand": "Michelin",
        "pattern": "Primacy 4",
        "width": 205,
        "aspect_ratio": 55,
        "rim_size": 16,
        "load_index": "91",
        "speed_rating": "V",
        "price": 24990.0,
        "currency": "HUF",
        "source": "gumi",
    }
    values.update(overrides)
    return Tyre(**values)
