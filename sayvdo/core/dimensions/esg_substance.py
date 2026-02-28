"""ESG Substance Score.

Source: DEF 14A proxy statement
Measures: Are ESG claims quantified or aspirational?
"""

import json
import subprocess


PROMPT = """You are analyzing a DEF 14A proxy statement to score the substantiveness of ESG disclosures.

Score whether ESG claims are backed by real metrics vs aspirational language:

Look for:
- Diversity: "We value diversity" vs "Board is 40% women, up from 30% in 2023"
- Climate: "Committed to sustainability" vs "Reduced Scope 1 emissions by 23% since 2020"
- Pay equity: "We pay fairly" vs "Women earn $0.98 per $1.00 vs men in comparable roles"
- Supply chain: "Responsible sourcing" vs specific audit numbers and remediation counts
- Governance: "Independent board oversight" vs actual independence metrics

Red flags:
- ESG section with zero numerical metrics
- Commitments without timelines ("we plan to...")
- Forward-looking claims dominate backward-looking results
- No third-party verification cited

Score 0-100 where:
- 90-100: Quantified, verified, specific ESG metrics with YoY progress
- 70-89: Mostly quantified with some aspirational gaps
- 50-69: Mix of metrics and aspirational language
- 30-49: Mostly aspirational with sparse metrics
- 0-29: Pure narrative — no substantive metrics, or section missing

Return JSON only (no markdown):
{
  "dimension": "esg_substance",
  "score": <0-100 integer>,
  "evidence": ["<direct quote from proxy>", ...],
  "flags": ["<aspirational claim or missing metric>", ...],
  "summary": "<1-2 sentence summary>"
}

DEF 14A proxy statement:
"""


def score(ticker: str, filing_data: dict) -> dict:
    """Score ESG substance from DEF 14A proxy statement."""
    def14a = filing_data.get("def14a")

    if not def14a or not def14a.get("text"):
        return {
            "dimension": "esg_substance",
            "score": 30,
            "evidence": [],
            "flags": ["No DEF 14A proxy statement available — scoring conservatively"],
            "summary": "No proxy statement found. Cannot assess ESG disclosure quality.",
        }

    prompt = PROMPT + def14a["text"][:60000]

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
        "dimension": "esg_substance",
        "score": 50,
        "evidence": [],
        "flags": ["Claude analysis failed — defaulting to 50"],
        "summary": "ESG substance analysis unavailable.",
    }
