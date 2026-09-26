# Notes: getting the 3AM push notification to work

A record of what was actually wrong and what we changed, September 2026. Kept because
these settings live on a phone rather than in this repo — if the phone is replaced, or
notifications stop, this is the list to walk back through.

For instructions to hand to a new channel member, see
[slack-setup.md](slack-setup.md). This file is the diagnostic history.

---

## The symptom

Alerts posted to `#pcv-alerts` correctly and were visible in Slack. No push notification
ever arrived at 3AM. Nothing in the logs indicated a problem — the app reported
`Sent Slack message` every time.

The misleading part: **a Slack webhook returning HTTP 200 only means Slack accepted the
message.** It says nothing about whether any human was told. Every failure below is
invisible from the sending side.

## What isolated it

Three observations narrowed it to a time-of-day gate:

| Event | Time | Notified? |
| --- | --- | --- |
| Manual test run | 8:30 PM | ✅ yes |
| Weekly heartbeat in `#pcv-ops` | 9:00 AM Mondays | ✅ yes |
| Scheduled alert in `#pcv-alerts` | 3:00 AM | ❌ no |

Same phone, same workspace, delivery confirmed in all three cases. That ruled out
permissions, workspace scope, channel settings, and the app itself — notifications worked
at 9AM and 8:30PM but not 3AM, so something was gating on the hour.

## Root cause

**An iOS Do Not Disturb schedule running 23:00–07:00, with Slack not in its allow-list.**

Slack had been added to **Sleep** Focus's allowed apps. But Sleep was not the Focus that
activated overnight — Do Not Disturb was, on its own schedule. Only one Focus runs at a
time and each keeps a separate allow-list, so allowing Slack in the wrong one accomplished
nothing.

This is the trap: the fix looks done and isn't. There's no indication which Focus will win,
and no feedback when one silences something.

## What we changed

### iOS

1. **Deleted the Do Not Disturb schedule** (was every day, 23:00–07:00).
2. **Added that same 23:00–07:00 schedule to Sleep Focus instead**, which already had Slack
   in its allowed apps.
3. Confirmed Sleep's list is set to **Allow Notifications From**, not *Silence Notifications
   From* — that toggle inverts the list's meaning, so Slack being present would block it.
4. **Settings → Notifications → Slack**: Lock Screen enabled, Banner Style **Persistent**,
   **Show Previews → Always**, Sounds on.
5. **Settings → Notifications → Scheduled Summary**: confirmed Slack's toggle is **off**.
   Slack appears in that list regardless; being switched on would batch alerts for later
   delivery.

### Slack (PCV workspace, per-workspace settings)

6. **Notify me about → All new messages.** The default is "Direct messages, mentions &
   keywords," and a webhook post mentions nobody — so the default may notify about nothing.
7. **Notification schedule → Every day, 12:00 AM – 11:30 PM.** It had been 3AM–9PM, which
   put the 3:00:00 AM alert on the opening boundary. Slack won't accept a true 24-hour
   window since the end must follow the start, so 11:30 PM is the practical maximum. The
   paused half hour before midnight costs nothing — alerts only fire 3–8AM.
8. **Notify Me on Mobile → As soon as they're sent.** By default Slack withholds mobile
   push while you're active on a computer, waiting until you've been idle. That would send a
   4AM alert to a desktop and leave the phone silent.

### This repo

9. Alert headline now names the cheapest unit, because Slack only previews the `text` field
   on a lock screen. It previously said how many apartments qualified but not whether any was
   worth getting up for.

## Verifying after any change

```bash
rm /tmp/pcv-state.json
python -m pcv --once
```

Lock the phone first. Confirm three things: it appears on the **lock screen**, it makes a
**sound**, and the text is **readable** rather than "1 new message." A notification that
arrives silently is a practical failure even though it looks like success.

`python -m pcv --heartbeat` does the same for `#pcv-ops`.

## If it breaks again

Check in this order — cheapest and most likely first:

1. **Any Focus mode with an overnight schedule** that lacks Slack in its allow-list. This was
   the actual cause and would be again after an iOS update or a new phone.
2. **Slack's notification schedule**, especially whether an alert time sits on its boundary.
3. **Notify Me on Mobile**, if it works on a laptop but not the phone.
4. **The app itself** — last, not first. Check
   `doctl apps logs 45963431-2932-4210-a5bf-b9d97246a1a9 scraper --context personal`.
   Two weeks of logs showed zero errors while all of the above was broken.
