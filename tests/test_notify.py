from __future__ import annotations

import pytest
import requests

from pcv.notify import SlackNotifier
from tests.conftest import make_listing


class RecordingSession:
    """Stands in for requests.Session, capturing the posted payload."""

    def __init__(self, status_code: int = 200):
        self.posts: list[dict] = []
        self._status_code = status_code

    def post(self, url, json, timeout):
        self.posts.append({"url": url, "json": json, "timeout": timeout})
        response = requests.Response()
        response.status_code = self._status_code
        return response


@pytest.fixture
def session() -> RecordingSession:
    return RecordingSession()


@pytest.fixture
def notifier(session) -> SlackNotifier:
    return SlackNotifier("https://hooks.slack.test/webhook", session=session)


def test_listings_alert_payload(notifier, session):
    notifier.send_listings_alert(
        [make_listing("a", 6500)], url="https://stuytown.test/search", threshold=7000
    )

    payload = session.posts[0]["json"]
    # `text` is what shows on a phone's lock screen, so the price must be in it.
    assert "under $7,000" in payload["text"]
    assert "1 PCV apartment " in payload["text"]

    body = payload["blocks"][1]["text"]["text"]
    assert "$6,500/mo" in body
    assert "370 First Avenue" in body
    assert "Apt 08-G" in body

    button = payload["blocks"][2]["elements"][0]
    assert button["url"] == "https://stuytown.test/search"


def test_alert_pluralises(notifier, session):
    notifier.send_listings_alert(
        [make_listing("a", 6500), make_listing("b", 6600, "09-C")],
        url="https://stuytown.test/search",
        threshold=7000,
    )

    assert "2 PCV apartments " in session.posts[0]["json"]["text"]


def test_heartbeat_payload(notifier, session):
    notifier.send_heartbeat(2, 6500)

    text = session.posts[0]["json"]["text"]
    assert "tracking 2" in text
    assert "$6,500" in text


def test_heartbeat_with_no_listings(notifier, session):
    notifier.send_heartbeat(0, None)

    assert "cheapest is n/a" in session.posts[0]["json"]["text"]


def test_failure_payload_includes_detail(notifier, session):
    notifier.send_failure(3, "ApiShapeError: no 'unitModels' key")

    text = session.posts[0]["json"]["text"]
    assert "failed 3 times in a row" in text
    assert "no 'unitModels' key" in text


def test_posts_to_the_configured_webhook(notifier, session):
    notifier.send("hello")

    assert session.posts[0]["url"] == "https://hooks.slack.test/webhook"


def test_http_error_propagates():
    """Runner relies on a failed post raising, so it can retry the alert later."""
    notifier = SlackNotifier("https://hooks.slack.test/webhook", session=RecordingSession(500))

    with pytest.raises(requests.HTTPError):
        notifier.send("hello")
