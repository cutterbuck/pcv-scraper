"""Configuration, read once from the environment at startup."""

from __future__ import annotations

import os
from dataclasses import dataclass


class ConfigError(Exception):
    """Raised when required configuration is missing or malformed."""


def _int_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        raise ConfigError(f"{name} must be an integer, got {raw!r}") from None


@dataclass(frozen=True)
class Config:
    slack_webhook_url: str
    slack_ops_webhook_url: str
    rent_threshold: int
    bedrooms: int
    bathrooms: int
    property_name: str
    timezone: str
    scrape_hours: str
    scrape_minutes: str
    heartbeat_cron_day: str
    heartbeat_cron_hour: int
    state_path: str
    failure_alert_after: int

    @classmethod
    def from_env(cls) -> "Config":
        webhook = os.environ.get("SLACK_WEBHOOK_URL", "")
        if not webhook:
            raise ConfigError(
                "SLACK_WEBHOOK_URL is required. Create an Incoming Webhook at "
                "https://api.slack.com/messaging/webhooks and set it in the environment."
            )
        return cls(
            slack_webhook_url=webhook,
            # Heartbeat, failure and recovery notices go here. Point it at a separate,
            # muted channel so operational chatter cannot desensitise you to the alert
            # that matters. Falls back to the main channel when unset.
            slack_ops_webhook_url=os.environ.get("SLACK_OPS_WEBHOOK_URL") or webhook,
            rent_threshold=_int_env("RENT_THRESHOLD", 7000),
            bedrooms=_int_env("BEDROOMS", 2),
            bathrooms=_int_env("BATHROOMS", 2),
            property_name=os.environ.get("PROPERTY_NAME", "Peter Cooper Village"),
            timezone=os.environ.get("TIMEZONE", "America/New_York"),
            # StuyTown posts new availability between roughly 4 and 6AM ET.
            scrape_hours=os.environ.get("SCRAPE_HOURS", "3-7"),
            scrape_minutes=os.environ.get("SCRAPE_MINUTES", "0,15,30,45"),
            heartbeat_cron_day=os.environ.get("HEARTBEAT_DAY", "mon"),
            heartbeat_cron_hour=_int_env("HEARTBEAT_HOUR", 9),
            state_path=os.environ.get("STATE_PATH", "/tmp/pcv-state.json"),
            failure_alert_after=_int_env("FAILURE_ALERT_AFTER", 3),
        )
