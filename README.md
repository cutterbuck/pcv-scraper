# PCV Apartment Alerter

Watches Peter Cooper Village for below-market 2 bedroom / 2 bathroom availability and
posts to Slack the moment one appears.

StuyTown publishes new availability early in the morning, usually between 4 and 6AM.
Below-market units are rare and get taken quickly, so current and aspiring residents
set alarms to check. This app checks for you every 15 minutes during that window and
only wakes you when there is something worth waking up for.

## How it works

The stuytown.com search page is a Next.js app whose listing grid is populated by a
public JSON endpoint:

```
GET https://units.stuytown.com/api/units?Bedrooms=2&Bathrooms=2&PropertyName=Peter+Cooper+Village
```

The app reads that endpoint directly — no headless browser, no HTML parsing. A scrape
takes about 200ms and the whole service fits in 512 MiB.

Each cycle it fetches current listings, drops any unit it has already reported, and
posts the rest to Slack if the rent is below `RENT_THRESHOLD`. A unit that disappears
and is later relisted counts as new availability and alerts again.

### Failure is loud

The previous version of this app detected "no results" by searching the page for the
site's *"we don't have anything within that search criteria"* copy. Next.js ships that
copy in a `<script>` tag on **every** page load, so every scrape reported zero listings.
The app went silent for four months and looked exactly like a quiet market.

This version treats an unreadable response as an error, not as an empty result:

- An unrecognised API shape raises `ApiShapeError` rather than returning `[]`.
- After `FAILURE_ALERT_AFTER` consecutive failures (default 3) it posts a Slack warning,
  once, and posts again when it recovers.
- A weekly heartbeat reports that it is alive and what it currently sees.

## Setup

Python 3.12, matching the deployed image.

```bash
conda create -n pcv python=3.12 -y
conda activate pcv
pip install -r requirements-dev.txt   # or requirements.txt to skip pytest
cp .env.example .env                  # then fill in the webhook URLs
```

### Two channels

Apartment alerts go to everyone; scraper plumbing goes only to you. A Slack Incoming
Webhook is bound to one channel when you create it, so this needs two webhooks:

| Channel | Webhook | Who's in it | Receives |
| --- | --- | --- | --- |
| `#pcv-alerts` (shared) | `SLACK_WEBHOOK_URL` | you + anyone else hunting | apartment alerts |
| `#pcv-ops` (private) | `SLACK_OPS_WEBHOOK_URL` | just you | heartbeat, failure, recovery |

Create both at <https://api.slack.com/messaging/webhooks> — add an Incoming Webhook to
the same app twice, picking a different channel each time. Make `#pcv-ops` a **private**
channel so the others never see it.

If `SLACK_OPS_WEBHOOK_URL` is unset, everything goes to the single main channel.

Beyond privacy, the split is what lets you set notification rules per channel: leave
`#pcv-alerts` on *All new messages* with mobile push, and mute `#pcv-ops` so a weekly
heartbeat never trains you to swipe these away.

### Make sure the alert actually reaches you

Slack mobile notifications respect Do Not Disturb, and at 4AM your phone is likely in
a Sleep Focus. Two settings are needed or the alert will queue silently until morning:

1. **iOS** → Settings → Focus → Sleep → **Allowed Apps** → add Slack.
2. **Slack mobile** → Notifications → set the notification schedule to allow 3–7AM.

## Running

```bash
python -m pcv                    # start the scheduler and block
python -m pcv --once             # single scrape, alerts if warranted
python -m pcv --once --no-alert  # single scrape, log only — good for a smoke test
```

## Configuration

All configuration is environment variables; see `.env.example` for the full list.

| Variable | Default | Purpose |
| --- | --- | --- |
| `SLACK_WEBHOOK_URL` | *(required)* | Webhook for apartment alerts (shared channel) |
| `SLACK_OPS_WEBHOOK_URL` | main webhook | Webhook for heartbeat/failures (private channel) |
| `RENT_THRESHOLD` | `9000` | Alert when monthly rent is below this |
| `BEDROOMS` / `BATHROOMS` | `2` / `2` | Search criteria |
| `PROPERTY_NAME` | `Peter Cooper Village` | Search criteria |
| `TIMEZONE` | `America/New_York` | Timezone for all schedules |
| `SCRAPE_HOURS` | `3-7` | Cron hours to scrape |
| `SCRAPE_MINUTES` | `0,15,30,45` | Cron minutes to scrape |
| `HEARTBEAT_DAY` / `HEARTBEAT_HOUR` | `mon` / `9` | Weekly proof-of-life |
| `STATE_PATH` | `/tmp/pcv-state.json` | Cache of already-alerted units |
| `FAILURE_ALERT_AFTER` | `3` | Consecutive failures before warning |

## Deploying to DigitalOcean

Deployed as an App Platform **Worker** — a long-running process with no HTTP listener
and no public URL, at $5/month.

```bash
doctl apps create --spec .do/app.yaml
```

Then set `SLACK_WEBHOOK_URL` as a **secret** environment variable in the DO control
panel. `deploy_on_push` is enabled, so pushing to `main` redeploys.

Note that App Platform's filesystem is ephemeral. `STATE_PATH` survives a process
restart but not a redeploy; the worst case is one duplicate alert.

## Tests

```bash
pytest
```

`tests/fixtures/units_response.json` is a real captured API response, so the parser is
tested against the actual shape the service returns. Tests never touch the network — an
autouse fixture fails any test that tries.
