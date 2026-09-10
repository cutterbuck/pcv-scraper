from __future__ import annotations

import pytest
import requests

from pcv.client import ApiShapeError
from pcv.runner import Runner
from pcv.state import AlertState
from tests.conftest import make_listing


@pytest.fixture
def build(config, notifier, ops_notifier, monkeypatch):
    """Build a Runner whose fetches are driven by a scripted queue of results."""

    def _build(*results):
        queue = list(results)

        def fake_fetch(**kwargs):
            outcome = queue.pop(0)
            if isinstance(outcome, Exception):
                raise outcome
            return outcome

        monkeypatch.setattr("pcv.runner.fetch_listings", fake_fetch)
        return Runner(
            config, notifier, AlertState(config.state_path), ops_notifier=ops_notifier
        )

    return _build


CHEAP = make_listing("unit-cheap", 6500)
EXPENSIVE = make_listing("unit-pricey", 8477, unit_number="09-C")


def test_alerts_on_listing_below_threshold(build, notifier):
    build([CHEAP]).run_once()

    assert len(notifier.alerts) == 1
    assert notifier.alerts[0] == [CHEAP]


def test_does_not_alert_above_threshold(build, notifier):
    build([EXPENSIVE]).run_once()

    assert notifier.alerts == []


def test_does_not_realert_for_the_same_unit(build, notifier):
    """A lingering cheap unit must not re-page every 15 minutes."""
    runner = build([CHEAP], [CHEAP], [CHEAP])

    runner.run_once()
    runner.run_once()
    runner.run_once()

    assert len(notifier.alerts) == 1


def test_realerts_if_a_unit_is_delisted_then_returns(build, notifier):
    """Coming back on the market is genuinely new availability."""
    runner = build([CHEAP], [], [CHEAP])

    runner.run_once()
    runner.run_once()  # unit disappears
    runner.run_once()  # and comes back

    assert len(notifier.alerts) == 2


def test_alerts_for_a_second_cheap_unit(build, notifier):
    second = make_listing("unit-cheap-2", 6900, unit_number="11-A")
    runner = build([CHEAP], [CHEAP, second])

    runner.run_once()
    runner.run_once()

    assert len(notifier.alerts) == 2
    assert notifier.alerts[1] == [second]


def test_no_alert_flag_suppresses_slack(build, notifier):
    build([CHEAP]).run_once(alert=False)

    assert notifier.alerts == []


def test_empty_market_is_quiet(build, notifier, ops_notifier):
    build([]).run_once()

    assert notifier.alerts == []
    assert ops_notifier.failures == []


def test_failures_alert_once_after_threshold(build, ops_notifier):
    boom = ApiShapeError("no 'unitModels' key")
    runner = build(boom, boom, boom, boom)

    for _ in range(4):
        runner.run_once()

    # failure_alert_after=3, and the alert must not repeat on the 4th failure.
    assert len(ops_notifier.failures) == 1
    assert ops_notifier.failures[0][0] == 3


def test_transient_failure_below_threshold_is_silent(build, notifier, ops_notifier):
    runner = build(requests.ConnectionError("timeout"), [CHEAP])

    runner.run_once()
    runner.run_once()

    assert ops_notifier.failures == []
    assert len(notifier.alerts) == 1


def test_recovery_is_announced(build, ops_notifier):
    boom = ApiShapeError("broken")
    runner = build(boom, boom, boom, [])

    for _ in range(4):
        runner.run_once()

    assert len(ops_notifier.failures) == 1
    assert ops_notifier.recoveries == 1


def test_alert_is_retried_when_slack_is_down(build, notifier):
    """A failed Slack post must not mark the unit as already-alerted."""
    runner = build([CHEAP], [CHEAP])
    working = notifier.send_listings_alert

    def explode(*args, **kwargs):
        raise requests.ConnectionError("slack unreachable")

    notifier.send_listings_alert = explode
    runner.run_once()
    assert notifier.alerts == []

    notifier.send_listings_alert = working
    runner.run_once()

    assert len(notifier.alerts) == 1


def test_state_survives_a_restart(build, notifier, config):
    build([CHEAP]).run_once()
    assert len(notifier.alerts) == 1

    # A new Runner reading the same state file must not re-alert.
    build([CHEAP]).run_once()
    assert len(notifier.alerts) == 1


def test_heartbeat_reports_market_summary(build, ops_notifier):
    build([CHEAP, EXPENSIVE]).send_heartbeat()

    assert ops_notifier.heartbeats == [(2, 6500)]


def test_heartbeat_on_empty_market(build, ops_notifier):
    build([]).send_heartbeat()

    assert ops_notifier.heartbeats == [(0, None)]


# Everyone in the shared channel should see apartment alerts; only the private ops
# channel should see the machinery breaking.


def test_apartment_alerts_never_reach_the_ops_channel(build, notifier, ops_notifier):
    build([CHEAP]).run_once()

    assert len(notifier.alerts) == 1
    assert ops_notifier.alerts == []


def test_failures_never_reach_the_shared_channel(build, notifier, ops_notifier):
    boom = ApiShapeError("no 'unitModels' key")
    runner = build(boom, boom, boom, [])

    for _ in range(4):
        runner.run_once()

    assert len(ops_notifier.failures) == 1
    assert ops_notifier.recoveries == 1
    assert notifier.failures == []
    assert notifier.recoveries == 0


def test_heartbeat_never_reaches_the_shared_channel(build, notifier, ops_notifier):
    build([CHEAP]).send_heartbeat()

    assert len(ops_notifier.heartbeats) == 1
    assert notifier.heartbeats == []


def test_ops_notifier_defaults_to_the_main_channel(config, notifier, monkeypatch):
    """With SLACK_OPS_WEBHOOK_URL unset, everything lands in one channel."""
    monkeypatch.setattr("pcv.runner.fetch_listings", lambda **kw: [CHEAP])
    runner = Runner(config, notifier, AlertState(config.state_path))

    runner.send_heartbeat()

    assert len(notifier.heartbeats) == 1
