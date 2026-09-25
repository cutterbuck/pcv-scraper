# Getting PCV alerts on your phone

When a below-market Peter Cooper Village apartment is listed, a bot posts it to
**#pcv-alerts**. These go fast and get posted between roughly 4 and 6AM, so the alert is only
useful if it wakes you.

Slack won't do that out of the box: it suppresses notifications overnight by default, and a
bot message doesn't mention you by name. Takes about five minutes to fix.

Do all of these — each one on its own is enough to block the alert.

---

## Part 1 — Slack settings

Same on iPhone and Android.

Make sure you're in the **PCV workspace** first — swipe right from the Home tab to switch.
These settings are per-workspace, so setting them in another Slack won't carry over.

Tap your **profile picture** (top-right, or the **You** tab at the bottom) → **Notifications**.

### Notify me about → **All new messages**

Some versions call this *"Let you know about"* → **Everything**. The default is "Direct
messages, mentions & keywords" — the bot doesn't mention you by name, so on the default you
may get nothing.

### Notification schedule → **Every day, 12:00 AM to 11:30 PM**

**This is the one that catches everyone.** Slack sets a schedule by default, often business
hours on weekdays, and silently drops everything outside it. Alerts arrive around 4AM, right
in the blocked window.

Tap **Allow notifications**, choose **Every day**, then set **Start** to **12:00 AM** and
**End** to the latest option available — **11:30 PM**. Slack requires the end to be after the
start, so it won't accept a true 24-hour window; 12:00 AM–11:30 PM is as close as it gets.

The half hour before midnight stays paused, which costs nothing: alerts only ever fire between
3 and 8AM.

Don't narrow this to just cover 3–7AM. An alert arriving in the same minute the schedule opens
may be dropped, and that failure is deeply confusing — notifications work all day and vanish
at precisely the hour you care about. Starting at midnight puts hours of margin before the
first alert.

Nothing else gets posted to this workspace, so there's no reason to limit the hours further.

### Notify Me on Mobile → **As soon as they're sent**

By default Slack won't push to your phone while you're active on a computer — it waits until
you've been idle. If you're up with a laptop open when an apartment posts, the alert goes to
your desktop and your phone stays silent.

---

## Part 2 — Phone settings

### iPhone

**Settings → Notifications → Slack**

| Setting | Set to | Why |
| --- | --- | --- |
| Allow Notifications | **On** | |
| Lock Screen | **Checked** | Otherwise it never reaches the lock screen |
| Banner Style | **Persistent** | Stays until dismissed instead of vanishing |
| Show Previews | **Always** | Otherwise you get "1 new message" with no details |
| Sounds | **On** | A silent notification won't wake you |
| Time Sensitive Notifications | **On** (if shown) | Breaks through Focus modes |

**Settings → Notifications → Scheduled Summary** — make sure **Slack's toggle is off**.
Summary batches notifications for later delivery, so a 4AM alert would reach you hours late.
Slack appearing in the list is normal; just confirm it isn't switched on.

**Settings → Focus** — this one is worth doing carefully, because it's where people get caught.

Only one Focus runs at a time, and each has its own separate allow-list. Allowing Slack in
**Sleep** does nothing if the Focus actually running at 4AM is **Do Not Disturb**.

1. Tap each Focus mode in turn — Do Not Disturb, Sleep, Personal, Work
2. Check each for a **Schedule** that covers overnight hours (a DND schedule like 23:00–07:00
   is common, and it silences the alert completely)
3. In each one: **Allow Notifications → Apps → add Slack**
4. Confirm the list says **Allow Notifications From**, not **Silence Notifications From** — that
   toggle inverts the meaning, so Slack being listed would *block* it

Adding Slack to every Focus mode takes a couple of minutes and means you don't have to work out
which one wins at 4AM.

To see which Focus is currently active: its name appears at the top of the lock screen, or
swipe down from the top-right and long-press the **Focus** button.

### Android

Part 1 is identical. For system settings:

**Settings → Apps → Slack → Notifications** — allow notifications, show on lock screen with
sound, importance **Urgent**.

**Settings → Notifications → Do Not Disturb** — add Slack as an allowed exception.

Exact wording varies by manufacturer.

---

## Confirm it works

Ask Jake to send a test alert. **Lock your phone first**, then check you get a notification on
the lock screen showing the apartment details.

Don't skip this. Every failure below looks fine from the sending side — the message posts to
the channel normally either way. Watching one arrive is the only way to know.

---

## Troubleshooting

| What you see | Almost certainly |
| --- | --- |
| Message is in the channel, no notification | Notification schedule |
| Works during the day, never overnight | A Focus mode you didn't check — often Do Not Disturb on an overnight schedule — or the Slack notification schedule |
| Works at every hour except the one the schedule starts | Schedule boundary — set it to all hours |
| Works on laptop, never on phone | Notify Me on Mobile |
| Notification arrives but hides the text | Show Previews not set to Always |
| Notification arrives hours late | Scheduled Summary has Slack switched on |
| Nothing at all, ever | Notify me about, or the channel is muted |

To check the channel isn't muted: open **#pcv-alerts** → tap the channel name → **Settings &
Details** → **Notifications**. It should say *Everything* or *Use workspace default*.
