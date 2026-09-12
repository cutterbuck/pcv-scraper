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

### Notification schedule → **allow all hours**, every day

**This is the one that catches everyone.** Slack sets a schedule by default, often business
hours on weekdays, and silently drops everything outside it. Alerts arrive around 4AM, right
in the blocked window.

Nothing else gets posted to this workspace, so there's no reason to limit the hours.

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

**Settings → Focus → Sleep → Allowed Apps** — **add Slack**. Without this, Sleep Focus
silences the alert during exactly the hours that matter. Add it to any other overnight Focus
modes too.

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
| Works during the day, never overnight | Notification schedule, or Sleep Focus missing Slack |
| Works on laptop, never on phone | Notify Me on Mobile |
| Notification arrives but hides the text | Show Previews not set to Always |
| Notification arrives hours late | Scheduled Summary has Slack switched on |
| Nothing at all, ever | Notify me about, or the channel is muted |

To check the channel isn't muted: open **#pcv-alerts** → tap the channel name → **Settings &
Details** → **Notifications**. It should say *Everything* or *Use workspace default*.
