# Say vs. Do — Corporate Truthfulness Engine

> **We score how honest public companies are between what they say and what they actually do.**

Public companies make promises in earnings calls, annual reports, and proxy statements. Then they do (or don't do) those things. We track the gap.

---

## What It Does

Say vs. Do analyzes SEC filings and scores companies across **5 dimensions of corporate honesty**:

| Dimension | What We Measure |
|---|---|
| **AI Disclosure** | Are AI claims specific, measurable, and verifiable — or just buzzwords? |
| **Guidance Accuracy** | How close were their forward-looking statements to actual results? |
| **Risk Language Drift** | Are risk disclosures getting vaguer over time (a red flag)? |
| **Capital Honesty** | Do capital allocation decisions match stated priorities? |
| **ESG Substance** | Is ESG reporting backed by real commitments or just PR? |

---

## Sample Scores

| Company | AI Disclosure | Overall |
|---|---|---|
| NVDA | 94 / 100 | 🟢 Genuine |
| GOOG | 84 / 100 | 🟢 Genuine |
| MSFT | 82 / 100 | 🟢 Genuine |

---

## How It Works

1. **Data Ingestion** — Pulls 10-K, 8-K, and DEF14A filings from EDGAR (SEC's public database)
2. **AI Analysis** — Claude reads and scores each filing across the 5 dimensions
3. **Tracking** — Scores are stored over time so you can see a company's honesty trend
4. **API** — Results served via FastAPI on port 8095

```
GET /score/{ticker}         → Latest truthfulness scores
GET /history/{ticker}       → Historical score trend
GET /leaderboard            → Top and bottom companies by dimension
```

---

## Tech Stack

- **Python** — Core analysis pipeline
- **FastAPI** — REST API (port 8095)
- **SQLite** — Score storage and historical tracking
- **EDGAR API** — SEC filing retrieval (no API key required)
- **Claude AI** — Multi-dimensional filing analysis

---

## Status

🟢 **Live** — Actively scoring S&P 500 companies

---

*Built by Justin Adair | Part of the Neo AI portfolio*
