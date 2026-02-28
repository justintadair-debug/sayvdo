"""Guidance Accuracy Score.

Source: 8-K earnings releases (quarterly)
Measures: Compare EPS/revenue/margin guidance to actual results.
"""

import json
import subprocess


PROMPT = """You are analyzing a series of 8-K earnings release filings to score a company's guidance accuracy.

Analyze the filings for:
- Forward guidance language: Is guidance specific (ranges, numbers) or aspirational ("we expect strong growth")?
- Guidance vs actuals: Where earlier filings made specific predictions, did later filings confirm or miss them?
- Margin vs revenue patterns: Do they beat revenue but miss margins? (signals bonus structure gaming)
- Language patterns: "Aspirational guidance" — always raises, never gives a range

Score 0-100 where:
- 90-100: Consistent specific guidance, hits targets
- 70-89: Mostly accurate, minor misses
- 50-69: Mixed — some specific guidance, some misses
- 30-49: Frequent misses or consistently vague guidance
- 0-29: Aspirational only, major misses, or misleading guidance

Return JSON only (no markdown):
{
  "dimension": "guidance_accuracy",
  "score": <0-100 integer>,
  "evidence": ["<direct quote from filing>", ...],
  "flags": ["<concern or pattern>", ...],
  "summary": "<1-2 sentence summary>"
}

8-K filings (most recent first):
"""


def score(ticker: str, filing_data: dict) -> dict:
    """Score guidance accuracy from 8-K filings."""
    eight_ks = filing_data.get("8ks", [])
    if not eight_ks:
        return {
            "dimension": "guidance_accuracy",
            "score": 50,
            "evidence": [],
            "flags": ["No 8-K filings available"],
            "summary": "Could not fetch 8-K earnings releases.",
        }

    # Combine up to 4 most recent 8-Ks
    combined_text = ""
    for i, filing in enumerate(eight_ks[:4]):
        combined_text += f"\n\n--- 8-K #{i+1} ({filing['date']}) ---\n"
        combined_text += filing["text"][:10000]

    prompt = PROMPT + combined_text[:50000]

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
        "dimension": "guidance_accuracy",
        "score": 50,
        "evidence": [],
        "flags": ["Claude analysis failed — defaulting to 50"],
        "summary": "Guidance accuracy analysis unavailable.",
    }
