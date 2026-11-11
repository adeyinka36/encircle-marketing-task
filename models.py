from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class Tyre(BaseModel):
    url: HttpUrl
    brand: str = Field(min_length=1)
    pattern: str = Field(min_length=1)
    width: int = Field(gt=0)
    aspect_ratio: int = Field(gt=0)
    rim_size: int = Field(gt=0)
    load_index: str | None = None
    speed_rating: str | None = None
    price: float | None = None
    currency: str | None = None
    season: str | None = None
    in_stock: bool | None = None
    eu_label: str | None = None
    source: Literal["gumi", "tirendo"]
