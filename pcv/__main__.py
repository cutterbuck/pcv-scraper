"""Entrypoint: schedule the scrape and block forever.

Run with `python -m pcv`. `python -m pcv --once` performs a single scrape and exits,
which is handy for verifying configuration after a deploy.
"""

from __future__ import annotations

import argparse
import logging
import sys
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from pcv.config import Config, ConfigError
from pcv.notify import SlackNotifier
from pcv.runner import Runner
from pcv.state import AlertState


def build_runner(config: Config) -> Runner:
    return Runner(
        config=config,
        notifier=SlackNotifier(config.slack_webhook_url),
        ops_notifier=SlackNotifier(config.slack_ops_webhook_url),
        state=AlertState(config.state_path),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pcv", description="StuyTown availability alerter")
    parser.add_argument(
        "--once", action="store_true", help="run a single scrape and exit"
    )
    parser.add_argument(
        "--no-alert",
        action="store_true",
        help="with --once, scrape and log results without notifying Slack",
    )
    parser.add_argument(
        "--heartbeat",
        action="store_true",
        help="send a single heartbeat and exit, to verify the ops webhook",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        stream=sys.stdout,
    )

    # Load .env for local runs. In production the platform supplies the environment,
    # so python-dotenv is a dev-only dependency and its absence is not an error.
    try:
        from dotenv import load_dotenv
    except ImportError:
        pass
    else:
        load_dotenv()

    try:
        config = Config.from_env()
    except ConfigError as exc:
        logging.error("%s", exc)
        return 1

    runner = build_runner(config)

    if args.heartbeat:
        runner.send_heartbeat()
        return 0

    if args.once:
        runner.run_once(alert=not args.no_alert)
        return 0

    tz = ZoneInfo(config.timezone)
    scheduler = BlockingScheduler(timezone=tz)
    scheduler.add_job(
        runner.run_once,
        CronTrigger(
            hour=config.scrape_hours, minute=config.scrape_minutes, timezone=tz
        ),
        name="scrape",
    )
    scheduler.add_job(
        runner.send_heartbeat,
        CronTrigger(
            day_of_week=config.heartbeat_cron_day,
            hour=config.heartbeat_cron_hour,
            minute=0,
            timezone=tz,
        ),
        name="heartbeat",
    )

    logging.info(
        "Scheduler starting: scraping at %s:%s %s, watching for %d BR / %d BA at %s under $%s",
        config.scrape_hours,
        config.scrape_minutes,
        config.timezone,
        config.bedrooms,
        config.bathrooms,
        config.property_name,
        f"{config.rent_threshold:,}",
    )
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Shutting down")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
