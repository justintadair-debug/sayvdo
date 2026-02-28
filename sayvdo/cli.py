"""CLI entry point for Say vs. Do."""

import argparse
import json
import sys

from sayvdo.core import scorer, history
from sayvdo.worklog import log_scan

WATCHLIST = ["NVDA", "MSFT", "AAPL", "AMZN", "GOOG", "META", "TSLA", "CRM", "IBM", "ORCL", "NFLX", "JPM"]

BAR_CHARS = "█"


def _bar(score: int, width: int = 20) -> str:
    filled = round(score / 100 * width)
    return BAR_CHARS * filled + "░" * (width - filled)


def _color(score: int) -> str:
    if score >= 80:
        return "\033[92m"  # green
    elif score >= 60:
        return "\033[93m"  # yellow
    elif score >= 40:
        return "\033[33m"  # orange
    else:
        return "\033[91m"  # red


RESET = "\033[0m"


def print_scorecard(result: dict):
    ticker = result["ticker"]
    company = result.get("company", ticker)
    quarter = result.get("quarter", "")
    composite = result["composite_score"]
    verdict = result.get("verdict", "")
    dims = result.get("dimensions", {})

    c = _color(composite)
    print(f"\n{'='*60}")
    print(f"  SAY VS. DO — {company} ({ticker})")
    print(f"  {quarter}")
    print(f"{'='*60}")
    print(f"\n  COMPOSITE SCORE: {c}{composite}/100{RESET}")
    print(f"  Verdict: {c}{verdict}{RESET}")
    print(f"\n  {_bar(composite)}\n")

    dim_labels = {
        "ai_narrative": "AI Narrative     (25%)",
        "guidance_accuracy": "Guidance Accuracy (25%)",
        "risk_drift": "Risk Drift        (20%)",
        "capital_honesty": "Capital Honesty   (15%)",
        "esg_substance": "ESG Substance     (15%)",
    }

    for key, label in dim_labels.items():
        dim = dims.get(key, {})
        s = dim.get("score", "N/A")
        if isinstance(s, int):
            c2 = _color(s)
            print(f"  {label}: {c2}{s:>3}{RESET}  {_bar(s, 15)}")
        else:
            print(f"  {label}: {s}")

    print()
    # Print evidence + flags for each dimension
    for key in dim_labels:
        dim = dims.get(key, {})
        if not dim:
            continue
        summary = dim.get("summary", "")
        flags = dim.get("flags", [])
        evidence = dim.get("evidence", [])
        print(f"  ── {dim_labels[key].split('(')[0].strip()} ──")
        if summary:
            print(f"     {summary}")
        for flag in flags[:2]:
            print(f"     ⚠️  {flag}")
        for ev in evidence[:1]:
            print(f"     📎 \"{ev[:120]}\"")
        print()

    print(f"{'='*60}\n")


def cmd_score(args):
    ticker = args.ticker.upper()
    quarter = getattr(args, "quarter", None)
    result = scorer.run(ticker, quarter=quarter)
    history.save_score(result)
    log_scan(ticker, result["composite_score"], result["quarter"])
    print_scorecard(result)

    if getattr(args, "json", False):
        print(json.dumps(result, indent=2))


def cmd_watchlist(args):
    print(f"Running watchlist ({len(WATCHLIST)} companies)...")
    for ticker in WATCHLIST:
        try:
            result = scorer.run(ticker)
            history.save_score(result)
            log_scan(ticker, result["composite_score"], result["quarter"])
            print(f"  {ticker:6s} → {result['composite_score']:>3}/100  {result['verdict']}")
        except Exception as e:
            print(f"  {ticker:6s} → ERROR: {e}")


def cmd_history(args):
    ticker = args.ticker.upper()
    rows = history.get_history(ticker)
    if not rows:
        print(f"No history found for {ticker}")
        return

    print(f"\n  Score History: {ticker}")
    print(f"  {'Quarter':<12} {'Composite':>9} {'AI':>5} {'Guidance':>9} {'Risk':>6} {'Capital':>8} {'ESG':>5}")
    print(f"  {'-'*60}")
    for row in rows:
        print(f"  {row['quarter']:<12} {row['composite_score']:>9} "
              f"{row['ai_score'] or '?':>5} {row['guidance_score'] or '?':>9} "
              f"{row['risk_drift_score'] or '?':>6} {row['capital_score'] or '?':>8} "
              f"{row['esg_score'] or '?':>5}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="sayvdo",
        description="Say vs. Do — Corporate Truthfulness Engine",
    )
    subparsers = parser.add_subparsers(dest="command")

    # score
    p_score = subparsers.add_parser("score", help="Score a company")
    p_score.add_argument("ticker", help="Ticker symbol (e.g. MSFT)")
    p_score.add_argument("--quarter", help="Quarter (e.g. Q4-2025)", default=None)
    p_score.add_argument("--json", action="store_true", help="Output raw JSON")

    # watchlist
    subparsers.add_parser("watchlist", help="Score all watchlist companies")

    # history
    p_history = subparsers.add_parser("history", help="Show score history for a ticker")
    p_history.add_argument("ticker", help="Ticker symbol")

    args = parser.parse_args()

    if args.command == "score":
        cmd_score(args)
    elif args.command == "watchlist":
        cmd_watchlist(args)
    elif args.command == "history":
        cmd_history(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
