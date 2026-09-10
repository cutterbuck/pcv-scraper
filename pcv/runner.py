"""One scrape cycle: fetch, diff against what we have already reported, alert."""

from __future__ import annotations

import logging

import requests

from pcv.client import ApiShapeError, Listing, fetch_listings, listings_url
from pcv.config import Config
from pcv.notify import SlackNotifier
from pcv.state import AlertState

log = logging.getLogger(__name__)


class Runner:
    def __init__(
        self,
        config: Config,
        notifier: SlackNotifier,
        state: AlertState,
        ops_notifier: SlackNotifier | None = None,
    ):
        self._config = config
        self._notifier = notifier
        # Operational noise (heartbeat, failures) is routed separately from apartment
        # alerts so the two can have different Slack notification settings.
        self._ops_notifier = ops_notifier or notifier
        self._state = state
        self._session = requests.Session()

    def _fetch(self) -> list[Listing]:
        return fetch_listings(
            bedrooms=self._config.bedrooms,
            bathrooms=self._config.bathrooms,
            property_name=self._config.property_name,
            session=self._session,
        )

    def _record_failure(self, detail: str) -> None:
        self._state.consecutive_failures += 1
        log.error("Scrape failed (%d in a row): %s", self._state.consecutive_failures, detail)
        should_alert = (
            self._state.consecutive_failures >= self._config.failure_alert_after
            and not self._state.failure_alert_sent
        )
        if should_alert:
            try:
                self._ops_notifier.send_failure(self._state.consecutive_failures, detail)
                self._state.failure_alert_sent = True
            except requests.RequestException as exc:
                log.error("Could not send failure alert to Slack: %s", exc)
        self._state.save()

    def _record_success(self) -> None:
        if self._state.failure_alert_sent:
            try:
                self._ops_notifier.send_recovery()
            except requests.RequestException as exc:
                log.error("Could not send recovery notice to Slack: %s", exc)
        self._state.consecutive_failures = 0
        self._state.failure_alert_sent = False

    def run_once(self, alert: bool = True) -> list[Listing]:
        """Run a single scrape. Returns the listings found (empty on failure)."""
        try:
            listings = self._fetch()
        except (requests.RequestException, ApiShapeError) as exc:
            self._record_failure(f"{type(exc).__name__}: {exc}")
            return []

        self._record_success()
        log.info(
            "Found %d listing(s): %s",
            len(listings),
            ", ".join(f"{l.unit_number} ${l.rent:,}" for l in listings) or "none",
        )

        self._state.forget_units_absent_from({listing.unit_spk for listing in listings})

        cheap = [l for l in listings if l.rent < self._config.rent_threshold]
        new_cheap = [l for l in cheap if l.unit_spk not in self._state.alerted_units]

        if new_cheap and alert:
            try:
                self._notifier.send_listings_alert(
                    new_cheap,
                    url=listings_url(
                        self._config.bedrooms,
                        self._config.bathrooms,
                        self._config.property_name,
                    ),
                    threshold=self._config.rent_threshold,
                )
                self._state.alerted_units.update(l.unit_spk for l in new_cheap)
            except requests.RequestException as exc:
                # Leave these units unrecorded so the next cycle retries the alert.
                log.error("Could not send listings alert to Slack: %s", exc)
        elif new_cheap:
            log.info("Found %d new cheap listing(s), alerts disabled", len(new_cheap))

        self._state.save()
        return listings

    def send_heartbeat(self) -> None:
        """Weekly proof-of-life, so a silent scraper is distinguishable from a quiet market."""
        try:
            listings = self._fetch()
        except (requests.RequestException, ApiShapeError) as exc:
            self._record_failure(f"{type(exc).__name__}: {exc}")
            return
        cheapest = min((l.rent for l in listings), default=None)
        try:
            self._ops_notifier.send_heartbeat(len(listings), cheapest)
        except requests.RequestException as exc:
            log.error("Could not send heartbeat to Slack: %s", exc)
