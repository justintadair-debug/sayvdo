"""WorkLog integration — log every scan."""

import requests

WORKLOG_URL = "http://localhost:8092/api/log"
WORKLOG_KEY = "wl-justin-2026"


def log_scan(ticker: str, composite_score: int, quarter: str, notes: str = ""):
    """Log a completed scan to WorkLog."""
    try:
        payload = {
            "project": "sayvdo",
            "description": f"Scored {ticker} for {quarter}: composite={composite_score}. {notes}".strip(),
            "task_type": "analysis",
            "actual_hours": 0.05,
            "manual_estimate": 0.5,
        }
        requests.post(
            WORKLOG_URL,
            json=payload,
            headers={"X-WL-Key": WORKLOG_KEY},
            timeout=5,
        )
    except Exception:
        pass  # Never let WorkLog failures break scoring
