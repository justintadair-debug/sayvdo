"""Risk Language Drift Score.

Source: 10-K Risk Factors section, YoY comparison
Measures: What risks quietly appeared or disappeared between filings?
"""

import json
import re
import subprocess


PROMPT = """You are analyzing a 10-K SEC filing's Risk Factors section to score a company's risk disclosure transparency.

Look for:
- New risks that appeared (added language about AI dependency, regulatory risk, concentration risk, etc.)
- Missing risks: based on the company's business, what risks are conspicuously absent?
- Specificity of risk language: vague "macro uncertainty" vs specific "revenue from 3 customers represents 40%"
- Boilerplate vs substance: standard legal CYA language vs genuinely informative risk disclosure
- Hidden or minimized risks: risks mentioned briefly that seem material

Score 0-100 where:
- 90-100: Specific, comprehensive risk disclosure — no obvious gaps
- 70-89: Good disclosure with minor gaps
- 50-69: Mix of specific and boilerplate, some material gaps
- 30-49: Mostly boilerplate, important risks understated
- 0-29: Risk factors appear designed to minimize rather than disclose

Return JSON only (no markdown):
{
  "dimension": "risk_drift",
  "score": <0-100 integer>,
  "evidence": ["<direct quote from filing>", ...],
  "flags": ["<concern or missing risk>", ...],
  "summary": "<1-2 sentence summary>"
}

10-K filing (focus on Risk Factors section):
"""


def _extract_risk_section(text: str) -> str:
    """Try to extract just the Risk Factors section."""
    # Look for common Risk Factors headers
    patterns = [
        r"(?i)ITEM\s+1A[\.\s]+RISK FACTORS(.*?)(?=ITEM\s+1B|ITEM\s+2)",
        r"(?i)Risk Factors(.*?)(?=Item\s+2|PART\s+II)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1)[:30000]
    # Return first 40k chars as fallback
    return text[:40000]


def score(ticker: str, filing_data: dict) -> dict:
    """Score risk language drift from 10-K."""
    ten_k = filing_data.get("10k")
    if not ten_k or not ten_k.get("text"):
        return {
            "dimension": "risk_drift",
            "score": 0,
            "evidence": [],
            "flags": ["No 10-K filing available"],
            "summary": "Could not fetch 10-K filing.",
        }

    risk_text = _extract_risk_section(ten_k["text"])
    prompt = PROMPT + risk_text

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
        "dimension": "risk_drift",
        "score": 50,
        "evidence": [],
        "flags": ["Claude analysis failed — defaulting to 50"],
        "summary": "Risk drift analysis unavailable.",
    }
