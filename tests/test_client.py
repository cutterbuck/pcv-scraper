from __future__ import annotations

import pytest

from pcv.client import ApiShapeError, listings_url, parse_units


def test_parses_real_response(units_response):
    listings = parse_units(units_response)

    assert len(listings) == 2
    first = listings[0]
    assert first.unit_spk == "P~NYPC21~B~370~U~08-G"
    assert first.rent == 8477
    assert first.unit_number == "08-G"
    assert first.floor == "08"
    assert first.unit == "G"
    assert first.building == "370 First Avenue"  # API returns "370 FIRST AVENUE"
    assert first.sqft == 1211


def test_empty_result_is_not_an_error(units_empty):
    """No availability is a normal outcome, distinct from a broken scrape.

    The previous implementation conflated the two: it looked for the site's
    "we don't have anything" copy, which Next.js ships in a <script> tag on every
    page load, so every scrape reported zero listings and no alert ever fired.
    """
    assert parse_units(units_empty) == []


def test_available_date_in_the_past_reads_as_now(units_response):
    # Fixture's first unit became available 2026-08-26.
    assert parse_units(units_response)[0].available_date == "now"


def test_future_available_date_is_formatted(units_response):
    units_response["unitModels"][0]["availableDate"] = "2099-09-11T00:00:00Z"
    assert parse_units(units_response)[0].available_date == "Sep 11, 2099"


def test_missing_available_date_is_tolerated(units_response):
    units_response["unitModels"][0].pop("availableDate")
    assert parse_units(units_response)[0].available_date == "unknown"


@pytest.mark.parametrize(
    "payload, expected",
    [
        ([], "expected a JSON object"),
        ({"count": 0}, "no 'unitModels' key"),
        ({"unitModels": "nope"}, "expected a list"),
        ({"unitModels": ["nope"]}, "expected an object"),
    ],
)
def test_unrecognised_shapes_raise(payload, expected):
    """A changed API must fail loudly rather than look like an empty market."""
    with pytest.raises(ApiShapeError, match=expected):
        parse_units(payload)


@pytest.mark.parametrize("field", ["price", "unitSpk", "unitNumber"])
def test_missing_required_field_raises(units_response, field):
    units_response["unitModels"][0].pop(field)
    with pytest.raises(ApiShapeError, match="missing expected field"):
        parse_units(units_response)


def test_missing_building_raises(units_response):
    units_response["unitModels"][0]["building"] = None
    with pytest.raises(ApiShapeError, match="missing expected field"):
        parse_units(units_response)


def test_non_numeric_price_raises(units_response):
    units_response["unitModels"][0]["price"] = "call for pricing"
    with pytest.raises(ApiShapeError, match="non-numeric price"):
        parse_units(units_response)


def test_describe_is_human_readable(units_response):
    assert parse_units(units_response)[0].describe() == (
        "$8,477/mo — 370 First Avenue, Apt 08-G, 1211 sqft — available now"
    )


def test_listings_url_encodes_property_name():
    url = listings_url(2, 2, "Peter Cooper Village")
    assert "PropertyName=Peter+Cooper+Village" in url
    assert "Bedrooms=2" in url and "Bathrooms=2" in url
