"""SQLite history — time series of scores per company per quarter."""

import json
import os
import sqlite3

DB_PATH = os.path.expanduser("~/projects/sayvdo/sayvdo.db")


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if not exists."""
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                company TEXT,
                quarter TEXT,
                composite_score INTEGER,
                ai_score INTEGER,
                guidance_score INTEGER,
                risk_drift_score INTEGER,
                capital_score INTEGER,
                esg_score INTEGER,
                scanned_at TEXT DEFAULT (datetime('now')),
                scores_json TEXT,
                UNIQUE(ticker, quarter)
            )
        """)


def save_score(result: dict):
    """Persist a scorer result to SQLite."""
    init_db()
    dims = result.get("dimensions", {})

    with _conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO scores
                (ticker, company, quarter, composite_score,
                 ai_score, guidance_score, risk_drift_score, capital_score, esg_score,
                 scanned_at, scores_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result["ticker"],
            result.get("company"),
            result.get("quarter"),
            result.get("composite_score"),
            dims.get("ai_narrative", {}).get("score"),
            dims.get("guidance_accuracy", {}).get("score"),
            dims.get("risk_drift", {}).get("score"),
            dims.get("capital_honesty", {}).get("score"),
            dims.get("esg_substance", {}).get("score"),
            result.get("scanned_at"),
            json.dumps(result),
        ))


def get_history(ticker: str, limit: int = 8) -> list[dict]:
    """Get score history for a ticker."""
    init_db()
    with _conn() as conn:
        rows = conn.execute("""
            SELECT * FROM scores
            WHERE ticker = ?
            ORDER BY scanned_at DESC
            LIMIT ?
        """, (ticker.upper(), limit)).fetchall()
    return [dict(r) for r in rows]


def get_latest(ticker: str) -> dict | None:
    """Get the most recent score for a ticker."""
    rows = get_history(ticker, limit=1)
    return rows[0] if rows else None


def get_all_tickers() -> list[str]:
    """Get all tickers in the database."""
    init_db()
    with _conn() as conn:
        rows = conn.execute("SELECT DISTINCT ticker FROM scores ORDER BY ticker").fetchall()
    return [r["ticker"] for r in rows]
