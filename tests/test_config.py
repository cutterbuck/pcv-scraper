from __future__ import annotations

import pytest

from pcv.config import Config, ConfigError


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for key in (
        "SLACK_WEBHOOK_URL",
        "SLACK_OPS_WEBHOOK_URL",
        "RENT_THRESHOLD",
        "BEDROOMS",
    ):
        monkeypatch.delenv(key, raising=False)


def test_missing_webhook_is_a_config_error():
    with pytest.raises(ConfigError, match="SLACK_WEBHOOK_URL is required"):
        Config.from_env()


def test_ops_webhook_falls_back_to_the_main_webhook(monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.test/main")

    config = Config.from_env()

    assert config.slack_ops_webhook_url == "https://hooks.slack.test/main"


def test_ops_webhook_is_used_when_set(monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.test/main")
    monkeypatch.setenv("SLACK_OPS_WEBHOOK_URL", "https://hooks.slack.test/ops")

    config = Config.from_env()

    assert config.slack_webhook_url == "https://hooks.slack.test/main"
    assert config.slack_ops_webhook_url == "https://hooks.slack.test/ops"


def test_empty_ops_webhook_falls_back(monkeypatch):
    """An env var present but blank is a common App Platform mistake."""
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.test/main")
    monkeypatch.setenv("SLACK_OPS_WEBHOOK_URL", "")

    assert Config.from_env().slack_ops_webhook_url == "https://hooks.slack.test/main"


def test_threshold_defaults_to_9000(monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.test/main")

    assert Config.from_env().rent_threshold == 9000


def test_threshold_is_read_from_env(monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.test/main")
    monkeypatch.setenv("RENT_THRESHOLD", "7000")

    assert Config.from_env().rent_threshold == 7000


def test_non_numeric_threshold_is_a_config_error(monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.test/main")
    monkeypatch.setenv("RENT_THRESHOLD", "seven thousand")

    with pytest.raises(ConfigError, match="RENT_THRESHOLD must be an integer"):
        Config.from_env()
