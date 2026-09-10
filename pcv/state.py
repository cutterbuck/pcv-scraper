"""Best-effort persistence of which units we have already alerted on.

App Platform containers have an ephemeral filesystem, so this survives a process
restart but not a redeploy. That is an acceptable trade: the worst case is one
duplicate alert about an apartment you would want to hear about anyway.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)


class AlertState:
    def __init__(self, path: str):
        self._path = Path(path)
        self.alerted_units: set[str] = set()
        self.consecutive_failures: int = 0
        self.failure_alert_sent: bool = False
        self._load()

    def _load(self) -> None:
        try:
            raw = json.loads(self._path.read_text())
        except FileNotFoundError:
            return
        except (OSError, ValueError) as exc:
            log.warning("Could not read state from %s (%s); starting fresh", self._path, exc)
            return
        self.alerted_units = set(raw.get("alerted_units", []))
        self.consecutive_failures = raw.get("consecutive_failures", 0)
        self.failure_alert_sent = raw.get("failure_alert_sent", False)
        log.info("Loaded state: %d previously alerted unit(s)", len(self.alerted_units))

    def save(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(
                json.dumps(
                    {
                        "alerted_units": sorted(self.alerted_units),
                        "consecutive_failures": self.consecutive_failures,
                        "failure_alert_sent": self.failure_alert_sent,
                    }
                )
            )
        except OSError as exc:
            # Losing state costs us a duplicate alert, never a missed one.
            log.warning("Could not persist state to %s: %s", self._path, exc)

    def forget_units_absent_from(self, current_unit_spks: set[str]) -> None:
        """Drop units that are no longer listed.

        If a unit is taken off the market and later relisted, that is genuinely new
        availability and should alert again.
        """
        self.alerted_units &= current_unit_spks
