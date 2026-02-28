# Say vs. Do — Build Spec

## What This Is
A multi-dimensional corporate truthfulness engine. Scores public companies on the gap between what they claim publicly and what their SEC filings actually disclose. Think Bloomberg Terminal meets fact-checker.

## The Core Insight
Every major corporate fraud (Enron, Theranos, FTX) showed the same pattern: the public narrative diverged from verifiable signals before the collapse. The signals were always public. Nobody was reading them systematically. LLMs make this automatable at scale.

## The 5 Dimensions

### 1. AI Narrative Score (already built — port from SEC scanner)
- Source: 10-K filing
- What: Does AI disclosure match public AI claims?
- Existing: sec-scanner produces this score

### 2. Guidance Accuracy Score
- Source: 8-K earnings releases (quarterly)
- What: Compare EPS/revenue/margin guidance to actual results 1-2 quarters later
- Signal: Companies that consistently miss margin but beat revenue are telling you something about bonus structures
- Flag: "Aspirational guidance" language (always raises, never specific range)

### 3. Risk Language Drift Score
- Source: 10-K Risk Factors section, YoY comparison
- What: What risks quietly appeared or disappeared between filings?
- Signal: Adding "dependency on third-party AI providers" risk = real concern
- Flag: Removing previously specific risk language = either resolved or buried

### 4. Capital Allocation Honesty Score
- Source: 10-K + proxy statement
- What: Does actual R&D/capex spend match stated strategic priorities?
- Signal: Company says "innovation is our top priority" but R&D spend declined YoY
- Flag: Compensation structure misaligned with stated priorities (bonus on revenue, not innovation)

### 5. ESG Substance Score
- Source: Proxy statement (DEF 14A)
- What: Are ESG claims quantified or aspirational?
- Signal: "We're committed to diversity" vs. "Board is 40% women, up from 30% in 2023"
- Flag: ESG language with zero metrics

## Composite Score
Weighted average: AI 25%, Guidance 25%, Risk Drift 20%, Capital 15%, ESG 15%
Range: 0-100. "Narrative vs. Reality" score.

## Stack
- FastAPI backend (Python)
- SQLite — time series of scores per company per quarter
- Static frontend — company scorecard
- Claude subprocess for all analysis
- Port: 8094
- Path: ~/projects/sayvdo/

## Architecture
```
sayvdo/
├── main.py              # FastAPI web app
├── core/
│   ├── fetcher.py       # Extend sec-scanner fetcher — add 8-K, DEF 14A
│   ├── dimensions/
│   │   ├── ai_narrative.py       # Port from sec-scanner
│   │   ├── guidance_accuracy.py  # 8-K promises vs outcomes
│   │   ├── risk_drift.py         # YoY risk factor language shift
│   │   ├── capital_honesty.py    # Spend vs stated priorities
│   │   └── esg_substance.py      # Proxy ESG claims vs metrics
│   ├── scorer.py        # Runs all 5, returns composite
│   └── history.py       # SQLite time series
├── templates/
│   └── report.html      # Company scorecard
└── sayvdo.db
```

## Dimension Interface (all scorers must follow this)
```python
def score(ticker: str, filing_data: dict) -> dict:
    return {
        "dimension": "guidance_accuracy",
        "score": 72,           # 0-100
        "evidence": ["..."],   # specific quotes from filings
        "flags": ["..."],      # concerns
        "summary": "..."       # 1-2 sentence summary
    }
```

## Filing Types Needed
- 10-K: annual report (already fetching via sec-scanner)
- 8-K: earnings releases — filed ~4x/year, contains guidance and results
- DEF 14A: proxy statement — contains ESG, compensation, board composition

## EDGAR Fetching for New Filing Types
Extend sec_scanner/fetcher.py pattern:
- 8-K: type="8-K", filter for earnings releases (look for "Results of Operations" in filename)
- DEF 14A: type="DEF 14A"
- Need last 4 quarters of 8-Ks for guidance_accuracy scorer

## Database Schema
```sql
CREATE TABLE scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    company TEXT,
    quarter TEXT,            -- e.g. "Q4 2025"
    composite_score INTEGER,
    ai_score INTEGER,
    guidance_score INTEGER,
    risk_drift_score INTEGER,
    capital_score INTEGER,
    esg_score INTEGER,
    scanned_at TEXT DEFAULT (datetime('now')),
    scores_json TEXT,        -- full dimension details as JSON
    UNIQUE(ticker, quarter)
);
```

## Web Frontend
- Input: ticker symbol
- Output: scorecard showing all 5 dimensions + composite
- Trend chart: composite score over last 4 quarters
- Peer comparison: show same-sector companies
- "What changed" section: biggest movers between quarters

## CLI
```bash
sayvdo score MSFT          # score one company
sayvdo score MSFT --quarter Q4-2025  # specific quarter
sayvdo watchlist           # run full watchlist
sayvdo history MSFT        # show score history
```

## Watchlist (start with these)
NVDA, MSFT, AAPL, AMZN, GOOG, META, TSLA, CRM, IBM, ORCL, NFLX, JPM

## WorkLog Integration
Log every scan to http://localhost:8092/api/log
Header: X-WL-Key: wl-justin-2026

## Build Order
1. Fetcher extensions (8-K + DEF 14A)
2. guidance_accuracy scorer (highest value)
3. risk_drift scorer
4. Port ai_narrative from sec-scanner
5. capital_honesty and esg_substance scorers
6. Composite scorer + SQLite history
7. CLI
8. FastAPI web frontend

## NOT in Phase 1
- Patent velocity (Phase 2 — USPTO API)
- Talent/culture signals (Phase 2 — LinkedIn/Glassdoor)
- Email alerts
- Payment/subscription

## When to Build
After the multi-agent system is proven with real workloads. This project runs THROUGH the agent system — Researcher fetches filings, Analyst runs dimension scorers, Builder handles any code generation. It's the first real test of the full pipeline at scale.

## On Completion
When completely finished and tested, run:
openclaw system event --text "Done: Say vs. Do Phase 1 built — 5 dimensions, web frontend, CLI, watchlist" --mode now
