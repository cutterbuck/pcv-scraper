# Getting PCV alerts on your phone

When a below-market Peter Cooper Village apartment is listed, a bot posts it to
**#pcv-alerts**. These apartments go fast and get posted between roughly 4 and 6AM, so the
alert is only useful if it wakes you up.

Slack will **not** do that out of the box. By default it suppresses notifications overnight,
and a bot message doesn't mention you by name so it may not notify you at all. The settings
below fix both.

Takes about five minutes. Do all of them — each one independently blocks the alert.

---

## Part 1 — Slack settings

Same on iPhone and Android.

First, **make sure you're in the right workspace.** Swipe right from the Home tab to see your
workspace list and select the PCV one. These settings are per-workspace, so doing this in your
work Slack won't help and won't hurt.

Then tap your **profile picture** (top-right corner, or the **You** tab at the bottom) →
**Notifications**.

### 1a. Notify me about → **All new messages**

Some versions call this *"Let you know about"* → **Everything**.

The default is "Direct messages, mentions & keywords." The bot doesn't mention you by name,
so on the default setting you may get nothing at all.

### 1b. Notification schedule → **allow all hours**

**This is the one that catches everyone.** Slack sets a schedule by default, often something
like 8AM–5PM on weekdays, and silently suppresses notifications outside it. Alerts arrive at
4AM — squarely inside the blocked window.

Set it to allow notifications at **all hours**, every day.

There's nothing noisy in this workspace — just rare apartment alerts — so there's no reason
to limit the hours, and a schedule can only ever cause you to miss one.

### 1c. Notify Me on Mobile → **As soon as they're sent**

By default Slack won't push to your phone while you're active on a computer. It waits until
you've been idle — one minute after locking your screen, or ten minutes without cursor
activity.

If you're up with your laptop open when an apartment posts, the default sends the alert to
your desktop and leaves your phone silent. "As soon as they're sent" removes that dependency.

### 1d. Check #pcv-alerts isn't muted

Open **#pcv-alerts** → tap the channel name → **Settings & Details** → **Notifications**.

It should say *Everything* or *Use workspace default* — not *Nothing* or *Muted*. A muted
channel stays silent even with everything above set correctly.

---

## Part 2 — Phone settings

Slack can only deliver what your phone allows through.

### iPhone

**Settings → Notifications → Slack**

| Setting | Set to | Why |
| --- | --- | --- |
| Allow Notifications | **On** | |
| Lock Screen | **Checked** | Otherwise it never reaches the lock screen |
| Banner Style | **Persistent** | Stays until dismissed instead of vanishing in seconds |
| Show Previews | **Always** | Otherwise you see "1 new message" with no apartment details |
| Sounds | **On** | A silent notification won't wake you |
| Time Sensitive Notifications | **On** (if shown) | Lets it break through Focus modes |

**Settings → Notifications → Scheduled Summary**

Make sure **Slack is not switched on** in this list. Summary batches notifications for
scheduled delivery, so a 4AM alert would reach you hours late. Slack appearing in the list is
normal — just confirm its toggle is off.

**Settings → Focus → Sleep → Allowed Apps**

**Add Slack.** Without this, Sleep Focus silences the alert during exactly the hours that
matter. If you use other Focus modes overnight, add Slack to those too.

### Android

Slack settings (Part 1) are identical. For system settings:

**Settings → Apps → Slack → Notifications** — make sure notifications are allowed, set the
Slack notification category to show on the lock screen with sound, and set importance to
**Urgent**.

**Settings → Notifications → Do Not Disturb** — add Slack as an allowed exception so overnight
DND doesn't suppress it.

Exact wording varies by manufacturer (Samsung, Pixel, and OnePlus all differ slightly).

---

## Test it

Ask whoever runs the scraper to send a test alert. Lock your phone first, then confirm you
get a notification **on the lock screen** showing the apartment details — not just a silent
entry you find later in the app.

Don't skip this. Every failure mode above looks identical from the sending side: the message
posts to the channel and appears in Slack normally. The only way to know your phone will
actually wake you is to watch one arrive.

---

## Troubleshooting

| What you see | Almost certainly |
| --- | --- |
| Message is in the channel, no notification at all | Notification schedule (1b) — check whether the misses line up with time of day |
| Notifications work in the day, never overnight | Notification schedule (1b), or Sleep Focus missing Slack |
| Works on laptop, never on phone | Notify Me on Mobile (1c) |
| Notification arrives but hides the text | Show Previews not set to Always |
| Notification arrives hours late | Scheduled Summary has Slack switched on |
| Nothing at all, ever | Notify me about (1a), or the channel is muted (1d) |

A message appearing in #pcv-alerts only proves Slack accepted it. It says nothing about
whether your phone was going to tell you.
