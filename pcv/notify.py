"""Slack delivery via an Incoming Webhook."""

from __future__ import annotations

import logging

import requests

from pcv.client import Listing

log = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10


class SlackNotifier:
    def __init__(self, webhook_url: str, session: requests.Session | None = None):
        self._webhook_url = webhook_url
        self._session = session or requests.Session()

    def _post(self, payload: dict) -> None:
        response = self._session.post(
            self._webhook_url, json=payload, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()

    def send(self, text: str, blocks: list[dict] | None = None) -> None:
        """Post a message. `text` doubles as the mobile notification preview."""
        payload: dict = {"text": text}
        if blocks:
            payload["blocks"] = blocks
        self._post(payload)
        log.info("Sent Slack message: %s", text)

    def send_listings_alert(self, listings: list[Listing], url: str, threshold: int) -> None:
        count = len(listings)
        # Slack only previews `text` on a lock screen, so name the cheapest unit there.
        # Otherwise the push says how many apartments there are but not whether any is
        # worth getting out of bed for.
        cheapest = min(listings, key=lambda listing: listing.rent)
        headline = (
            f":rotating_light: {count} PCV apartment{'s' if count != 1 else ''} "
            f"under ${threshold:,} — cheapest ${cheapest.rent:,}, "
            f"{cheapest.building} {cheapest.unit_number}"
        )
        lines = "\n".join(f"• {listing.describe()}" for listing in listings)
        self.send(
            text=headline,
            blocks=[
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*{headline}*"},
                },
                {"type": "section", "text": {"type": "mrkdwn", "text": lines}},
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Apply on StuyTown"},
                            "url": url,
                            "style": "primary",
                        }
                    ],
                },
            ],
        )

    def send_heartbeat(self, listing_count: int, cheapest: int | None) -> None:
        cheapest_text = f"${cheapest:,}" if cheapest is not None else "n/a"
        self.send(
            f":heartbeat: PCV scraper alive. Currently tracking {listing_count} "
            f"2BR/2BA listing(s); cheapest is {cheapest_text}."
        )

    def send_failure(self, consecutive_failures: int, detail: str) -> None:
        self.send(
            f":warning: PCV scraper has failed {consecutive_failures} times in a row. "
            f"The StuyTown API may have changed.\n```{detail}```"
        )

    def send_recovery(self) -> None:
        self.send(":white_check_mark: PCV scraper is working again.")
