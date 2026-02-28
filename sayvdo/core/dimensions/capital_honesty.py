"""Capital Allocation Honesty Score.

Source: 10-K + DEF 14A proxy statement
Measures: Does actual R&D/capex spend match stated strategic priorities?
"""

import json
import subprocess


PROMPT = """You are analyzing SEC filings to score whether a company's capital allocation matches its stated strategic priorities.

Look for mismatches between:
- Company states "AI/innovation is our #1 priority" but R&D spend is flat or declining
- Company says "talent is our greatest asset" but total compensation declined
- Company emphasizes "long-term value creation" but buybacks dwarf R&D investment
- Compensation structure: are executives bonused on revenue/EPS (short-term) or innovation metrics (long-term)?
- Capex allocation: does spending match stated growth areas?

Score 0-100 where:
- 90-100: Strong alignment between stated priorities and spending
- 70-89: Generally aligned with minor gaps
- 50-69: Some mismatches — stated priorities not backed by capital
- 30-49: Clear misalignment — rhetoric doesn't match spend
- 0-29: Significant capital misallocation vs stated strategy

Return JSON only (no markdown):
{
  "dimension": "capital_honesty",
  "score": <0-100 integer>,
  "evidence": ["<direct quote or data point from filing>", ...],
  "flags": ["<mismatch or concern>", ...],
  "summary": "<1-2 sentence summary>"
}

10-K filing excerpt:
"""


def score(ticker: str, filing_data: dict) -> dict:
    """Score capital allocation honesty from 10-K + DEF 14A."""
    ten_k = filing_data.get("10k")
    def14a = filing_data.get("def14a")

    if not ten_k or not ten_k.get("text"):
        return {
            "dimension": "capital_honesty",
            "score": 0,
            "evidence": [],
            "flags": ["No 10-K filing available"],
            "summary": "Could not fetch 10-K filing.",
        }

    # Combine 10-K financial section + proxy compensation data
    combined = ten_k["text"][:40000]
    if def14a and def14a.get("text"):
        combined += "\n\n--- PROXY STATEMENT (DEF 14A) ---\n"
        combined += def14a["text"][:20000]

    prompt = PROMPT + combined[:60000]

    try:
        result = subprocess.run(
            ["/Users/justinadair/bin/claude-wrapper", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=120,
        )
        raw = result.stdout.strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            parsed = json.loads(raw[start:end])
            if "dimension" in parsed and "score" in parsed:
                return parsed
    except Exception as e:
        pass

    return {
        "dimension": "capital_honesty",
        "score": 50,
        "evidence": [],
        "flags": ["Claude analysis failed — defaulting to 50"],
        "summary": "Capital allocation analysis unavailable.",
    }
