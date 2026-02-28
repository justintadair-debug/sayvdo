# Say vs. Do — Project Context

## What It Is
Say vs. Do is a multi-dimensional corporate truthfulness engine. It scores public companies on the gap between what they claim publicly and what their SEC filings actually disclose. Think Bloomberg Terminal meets fact-checker.

Every major corporate fraud (Enron, Theranos, FTX) showed the same pattern: the public narrative diverged from verifiable signals before the collapse. The signals were always public. Nobody was reading them systematically. LLMs make this automatable at scale.

## The 5 Dimensions

### 1. AI Narrative Score (weight: 25%)
- **Source:** 10-K annual filing
- **Measures:** Does the AI disclosure in the 10-K match the company's public AI claims?
- **Signal:** Companies that claim AI transformation but show zero AI-specific capex or headcount in 10-K disclosures are AI-washing.

### 2. Guidance Accuracy Score (weight: 25%)
- **Source:** 8-K earnings releases (quarterly)
- **Measures:** Compare EPS/revenue/margin guidance to actual results 1-2 quarters later
- **Signal:** Companies that consistently miss margin but beat revenue are revealing something about their bonus structure incentives.
- **Flag:** "Aspirational guidance" language — always raises, never a specific range.

### 3. Risk Language Drift Score (weight: 20%)
- **Source:** 10-K Risk Factors section, year-over-year comparison
- **Measures:** What risks quietly appeared or disappeared between annual filings?
- **Signal:** Adding "dependency on third-party AI providers" risk = real business concern worth investigating.
- **Flag:** Removing previously specific risk language can mean either it was resolved OR it was buried.

### 4. Capital Allocation Honesty Score (weight: 15%)
- **Source:** 10-K + proxy statement (DEF 14A)
- **Measures:** Does actual R&D/capex spend match stated strategic priorities?
- **Signal:** Company says "innovation is our top priority" but R&D spend declined year-over-year.
- **Flag:** Compensation structure misaligned with stated priorities (bonus on revenue, not innovation).

### 5. ESG Substance Score (weight: 15%)
- **Source:** Proxy statement (DEF 14A)
- **Measures:** Are ESG claims quantified or aspirational?
- **Signal:** "We're committed to diversity" vs. "Board is 40% women, up from 30% in 2023"
- **Flag:** ESG language with zero metrics — all commitment, no accountability.

## Scoring Philosophy
**Score the filing language, not the company's reputation.**

We are not making moral judgments about companies. We are measuring the gap between narrative and disclosure. A company with a sterling public reputation can score low if their filings lack specificity. A company with a mixed press record can score high if they disclose precisely and follow through.

## Key Calibration
**Conservative filers (AAPL, AMZN) will score lower on disclosure — that's correct.**

Apple and Amazon are famously tight-lipped. Their filings tend to be less disclosive than peers. This is a real signal, not a flaw in the scoring. The tool measures disclosure quality, not corporate virtue.

## Evidence-First Principle
**Every score requires specific quotes from filings.**

No score is valid without:
- The exact language from the filing that supports it
- The source document and section
- What changed (for drift scores) or what's missing (for substance scores)

Vague assessments like "the company seems cautious" are not evidence. A direct quote from the Risk Factors section is.

## Composite Score
Weighted average across all 5 dimensions. Range: 0–100. Called the "Narrative vs. Reality" score.

| Score | Interpretation |
|-------|----------------|
| 80–100 | High narrative integrity — disclosures match public claims |
| 60–79 | Moderate — some gaps, worth monitoring |
| 40–59 | Significant narrative gap — scrutinize further |
| 0–39 | High divergence — red flags present |

## Watchlist
Default companies: NVDA, MSFT, AAPL, AMZN, GOOG, META, TSLA, CRM, IBM, ORCL, NFLX, JPM
