from __future__ import annotations

import json
from pathlib import Path

import pytest

from pcv.client import Listing
from pcv.config import Config

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Fail loudly if a test reaches the real network.

    Without this, a test that forgets to stub a fetch silently queries the live
    StuyTown API and passes or fails based on the actual rental market.
    """

    def blocked(*args, **kwargs):
        raise AssertionError("test attempted a real network request")

    monkeypatch.setattr("requests.adapters.HTTPAdapter.send", blocked)


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


@pytest.fixture
def units_response() -> dict:
    """A real captured response with two available 2BR/2BA units."""
    return load_fixture("units_response.json")


@pytest.fixture
def units_empty() -> dict:
    return load_fixture("units_empty.json")


@pytest.fixture
def config(tmp_path) -> Config:
    return Config(
        slack_webhook_url="https://hooks.slack.test/webhook",
        slack_ops_webhook_url="https://hooks.slack.test/ops-webhook",
        rent_threshold=7000,
        bedrooms=2,
        bathrooms=2,
        property_name="Peter Cooper Village",
        timezone="America/New_York",
        scrape_hours="3-7",
        scrape_minutes="0,15,30,45",
        heartbeat_cron_day="mon",
        heartbeat_cron_hour=9,
        state_path=str(tmp_path / "state.json"),
        failure_alert_after=3,
    )


def make_listing(unit_spk: str, rent: int, unit_number: str = "08-G") -> Listing:
    return Listing(
        unit_spk=unit_spk,
        building="370 First Avenue",
        unit_number=unit_number,
        rent=rent,
        sqft=1211,
        available_date="now",
    )


class FakeNotifier:
    """Records what would have been sent to Slack."""

    def __init__(self) -> None:
        self.alerts: list[list[Listing]] = []
        self.heartbeats: list[tuple[int, int | None]] = []
        self.failures: list[tuple[int, str]] = []
        self.recoveries = 0

    def send_listings_alert(self, listings, url, threshold) -> None:
        self.alerts.append(list(listings))

    def send_heartbeat(self, listing_count, cheapest) -> None:
        self.heartbeats.append((listing_count, cheapest))

    def send_failure(self, consecutive_failures, detail) -> None:
        self.failures.append((consecutive_failures, detail))

    def send_recovery(self) -> None:
        self.recoveries += 1


@pytest.fixture
def notifier() -> FakeNotifier:
    """Stands in for the shared apartment-alerts channel."""
    return FakeNotifier()


@pytest.fixture
def ops_notifier() -> FakeNotifier:
    """Stands in for the private ops channel that only Jake can see."""
    return FakeNotifier()
