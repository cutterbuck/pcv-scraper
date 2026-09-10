"""Client for the StuyTown units API.

The stuytown.com search page is a Next.js app whose listing grid is populated by a
public JSON endpoint on units.stuytown.com. Reading that endpoint directly is far
more reliable than driving a headless browser over the rendered HTML.

The endpoint is undocumented and can change without notice, so every field we depend
on is validated here. A shape we do not recognise raises ApiShapeError rather than
quietly yielding zero listings -- silence is indistinguishable from "no apartments",
which is exactly how the previous version of this app failed unnoticed for months.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import requests

API_URL = "https://units.stuytown.com/api/units"

#: Human-facing search page, linked in alerts so you can go straight to applying.
LISTINGS_URL = (
    "https://www.stuytown.com/nyc-apartments-for-rent"
    "?Order=low-price&Bedrooms={bedrooms}&PropertyName={property_query}&Bathrooms={bathrooms}"
)

REQUEST_TIMEOUT = 15


class ApiShapeError(Exception):
    """The API responded, but not with the structure we know how to read."""


@dataclass(frozen=True)
class Listing:
    unit_spk: str
    building: str
    unit_number: str
    rent: int
    sqft: int | None
    available_date: str

    @property
    def floor(self) -> str:
        return self.unit_number.split("-")[0]

    @property
    def unit(self) -> str:
        parts = self.unit_number.split("-")
        return parts[1] if len(parts) > 1 else self.unit_number

    def describe(self) -> str:
        sqft = f", {self.sqft} sqft" if self.sqft else ""
        return (
            f"${self.rent:,}/mo — {self.building}, Apt {self.unit_number}"
            f"{sqft} — available {self.available_date}"
        )


def _title_case_address(address: str) -> str:
    """"370 FIRST AVENUE" -> "370 First Avenue"."""
    return " ".join(word.capitalize() for word in address.split())


def _format_available_date(raw: str | None) -> str:
    if not raw:
        return "unknown"
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return raw
    if parsed <= datetime.now(timezone.utc):
        return "now"
    return parsed.strftime("%b %-d, %Y")


def parse_units(payload: Any) -> list[Listing]:
    """Turn a raw API payload into Listings, or raise ApiShapeError trying."""
    if not isinstance(payload, dict):
        raise ApiShapeError(f"expected a JSON object, got {type(payload).__name__}")
    if "unitModels" not in payload:
        raise ApiShapeError(f"no 'unitModels' key; keys were {sorted(payload)}")

    units = payload["unitModels"]
    if not isinstance(units, list):
        raise ApiShapeError(f"'unitModels' was {type(units).__name__}, expected a list")

    listings = []
    for index, unit in enumerate(units):
        if not isinstance(unit, dict):
            raise ApiShapeError(f"unit {index} was {type(unit).__name__}, expected an object")
        try:
            rent = unit["price"]
            unit_spk = unit["unitSpk"]
            unit_number = unit["unitNumber"]
            building = unit["building"]["address"]
        except (KeyError, TypeError) as exc:
            raise ApiShapeError(f"unit {index} is missing expected field: {exc}") from exc

        if not isinstance(rent, (int, float)):
            raise ApiShapeError(f"unit {index} has non-numeric price {rent!r}")

        listings.append(
            Listing(
                unit_spk=str(unit_spk),
                building=_title_case_address(str(building)),
                unit_number=str(unit_number),
                rent=int(rent),
                sqft=unit.get("sqft"),
                available_date=_format_available_date(unit.get("availableDate")),
            )
        )
    return listings


def fetch_listings(
    bedrooms: int,
    bathrooms: int,
    property_name: str,
    session: requests.Session | None = None,
) -> list[Listing]:
    """Fetch currently available units matching the search criteria.

    Raises requests.RequestException on transport failures and ApiShapeError when the
    response cannot be interpreted.
    """
    params = {
        "Bedrooms": bedrooms,
        "Bathrooms": bathrooms,
        "PropertyName": property_name,
        "Order": "low-price",
        "page": 0,
        "itemsOnPage": 100,
    }
    getter = session.get if session else requests.get
    response = getter(
        API_URL,
        params=params,
        timeout=REQUEST_TIMEOUT,
        headers={"Accept": "application/json"},
    )
    response.raise_for_status()
    try:
        payload = response.json()
    except ValueError as exc:
        raise ApiShapeError(f"response was not JSON: {response.text[:200]!r}") from exc
    return parse_units(payload)


def listings_url(bedrooms: int, bathrooms: int, property_name: str) -> str:
    return LISTINGS_URL.format(
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        property_query=property_name.replace(" ", "+"),
    )
