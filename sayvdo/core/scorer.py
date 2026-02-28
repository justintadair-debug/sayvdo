"""Composite scorer — runs all 5 dimensions and returns weighted score."""

import datetime
from sayvdo.core import fetcher
from sayvdo.core.dimensions import (
    ai_narrative,
    guidance_accuracy,
    risk_drift,
    capital_honesty,
    esg_substance,
)

WEIGHTS = {
    "ai_narrative": 0.25,
    "guidance_accuracy": 0.25,
    "risk_drift": 0.20,
    "capital_honesty": 0.15,
    "esg_substance": 0.15,
}

SCORERS = [
    ai_narrative,
    guidance_accuracy,
    risk_drift,
    capital_honesty,
    esg_substance,
]


def _current_quarter() -> str:
    now = datetime.datetime.now()
    q = (now.month - 1) // 3 + 1
    return f"Q{q}-{now.year}"


def run(ticker: str, quarter: str | None = None) -> dict:
    """Run all 5 dimension scorers and return composite result."""
    ticker = ticker.upper()
    quarter = quarter or _current_quarter()

    print(f"\n[SayVsDo] Scoring {ticker} for {quarter}")
    print("=" * 50)

    # Fetch all filings
    filing_data = fetcher.fetch_all_filings(ticker)
    company = (
        (filing_data.get("10k") or {}).get("company")
        or (filing_data.get("def14a") or {}).get("company")
        or ticker
    )

    # Run each dimension
    dimension_results = {}
    for scorer_module in SCORERS:
        dim_name = scorer_module.__name__.split(".")[-1]
        print(f"\n[{ticker}] Scoring: {dim_name}...")
        result = scorer_module.score(ticker, filing_data)
        dimension_results[result["dimension"]] = result
        print(f"  → Score: {result['score']}")

    # Composite weighted score
    composite = 0.0
    for dim_key, weight in WEIGHTS.items():
        dim_score = dimension_results.get(dim_key, {}).get("score", 50)
        composite += dim_score * weight

    composite = round(composite)

    # Verdict
    if composite >= 80:
        verdict = "High Narrative Integrity"
    elif composite >= 60:
        verdict = "Moderate — Monitor"
    elif composite >= 40:
        verdict = "Significant Narrative Gap"
    else:
        verdict = "High Divergence — Red Flags"

    result = {
        "ticker": ticker,
        "company": company,
        "quarter": quarter,
        "composite_score": composite,
        "verdict": verdict,
        "dimensions": dimension_results,
        "scanned_at": datetime.datetime.now().isoformat(),
    }

    return result
