"""AI Narrative Score — ported from sec-scanner.

Source: 10-K filing
Measures: Does AI disclosure match public AI claims?
"""

import json
import subprocess


PROMPT = """You are analyzing a 10-K SEC filing to score a company's AI narrative integrity.

Score the filing on a 0-100 scale across these factors:
- Specificity: Are AI claims tied to specific products, systems, or metrics? (vague buzzwords = low)
- Financial Impact: Is AI investment quantified ($ spent, headcount, capex)?
- Integration Depth: Is AI described as core infrastructure or just a feature/pilot?
- Competitive Moat: Does AI create defensible advantage or is it commodity tooling?
- Execution Evidence: Are there concrete AI outcomes (speed, cost, revenue) cited?

Return JSON only (no markdown):
{
  "dimension": "ai_narrative",
  "score": <0-100 integer>,
  "evidence": ["<direct quote from filing>", ...],
  "flags": ["<concern or gap>", ...],
  "summary": "<1-2 sentence summary>"
}

Filing text (truncated):
"""


def score(ticker: str, filing_data: dict) -> dict:
    """Score AI narrative from 10-K text."""
    ten_k = filing_data.get("10k")
    if not ten_k or not ten_k.get("text"):
        return {
            "dimension": "ai_narrative",
            "score": 0,
            "evidence": [],
            "flags": ["No 10-K filing available"],
            "summary": "Could not fetch 10-K filing.",
        }

    text = ten_k["text"][:60000]
    prompt = PROMPT + text

    try:
        result = subprocess.run(
            ["/Users/justinadair/bin/claude-wrapper", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=120,
        )
        raw = result.stdout.strip()
        # Extract JSON from output
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            parsed = json.loads(raw[start:end])
            if "dimension" in parsed and "score" in parsed:
                return parsed
    except Exception as e:
        pass

    return {
        "dimension": "ai_narrative",
        "score": 50,
        "evidence": [],
        "flags": [f"Claude analysis failed — defaulting to 50"],
        "summary": "AI narrative analysis unavailable.",
    }
