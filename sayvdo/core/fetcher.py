"""EDGAR fetcher for Say vs. Do — extends sec-scanner pattern.

Fetches: 10-K, 8-K (earnings releases), DEF 14A (proxy statements).
"""

import os
import re
import time
import hashlib
import warnings

import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

HEADERS = {
    "User-Agent": "SayVsDo/1.0 (research@example.com)",
    "Accept-Encoding": "gzip, deflate",
}

CACHE_DIR = os.path.expanduser("~/.sayvdo_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

_last_request_time = 0.0


def _throttle():
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < 0.15:
        time.sleep(0.15 - elapsed)
    _last_request_time = time.time()


def _cache_key(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def _cache_get(url: str) -> str | None:
    path = os.path.join(CACHE_DIR, _cache_key(url) + ".txt")
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return None


def _cache_set(url: str, text: str):
    path = os.path.join(CACHE_DIR, _cache_key(url) + ".txt")
    with open(path, "w") as f:
        f.write(text)


def get_cik(ticker: str) -> str | None:
    """Look up CIK number for a ticker symbol."""
    _throttle()
    url = "https://www.sec.gov/files/company_tickers.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    for entry in resp.json().values():
        if entry.get("ticker", "").upper() == ticker.upper():
            return str(entry["cik_str"])
    return None


def get_company_name(ticker: str) -> str:
    _throttle()
    url = "https://www.sec.gov/files/company_tickers.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    for entry in resp.json().values():
        if entry.get("ticker", "").upper() == ticker.upper():
            return entry.get("title", ticker)
    return ticker


def _get_submissions(cik: str) -> dict:
    _throttle()
    padded = cik.zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{padded}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def download_and_clean(url: str, max_chars: int = 80000) -> str:
    """Download an EDGAR filing and return clean text."""
    cached = _cache_get(url)
    if cached:
        return cached

    _throttle()
    resp = requests.get(url, headers=HEADERS, timeout=60)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup.find_all(["script", "style", "ix:nonfraction", "ix:nonnumeric",
                               "ix:header", "ix:hidden", "ix:references"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    text = "\n".join(lines)
    text = re.sub(r"[_=\-]{10,}", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    if len(text) > max_chars:
        text = text[:max_chars]

    _cache_set(url, text)
    return text


def fetch_10k(ticker: str) -> dict | None:
    """Fetch latest 10-K for ticker. Returns dict or None."""
    print(f"  [{ticker}] Fetching 10-K...")
    cik = get_cik(ticker)
    if not cik:
        print(f"  [{ticker}] ERROR: CIK not found")
        return None

    company = get_company_name(ticker)
    data = _get_submissions(cik)
    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accessions = recent.get("accessionNumber", [])
    dates = recent.get("filingDate", [])
    primary_docs = recent.get("primaryDocument", [])

    for i, form in enumerate(forms):
        if form in ("10-K", "10-K/A"):
            accession = accessions[i].replace("-", "")
            doc = primary_docs[i]
            date = dates[i]
            url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{doc}"
            print(f"  [{ticker}] Downloading 10-K from {date}...")
            text = download_and_clean(url)
            print(f"  [{ticker}] 10-K: {len(text):,} chars")
            return {"ticker": ticker.upper(), "company": company, "date": date, "text": text, "url": url, "form": "10-K"}

    print(f"  [{ticker}] ERROR: No 10-K found")
    return None


def fetch_8k_list(ticker: str, max_count: int = 8) -> list[dict]:
    """Fetch last N 8-K filings for ticker. Returns list of dicts."""
    print(f"  [{ticker}] Fetching 8-Ks...")
    cik = get_cik(ticker)
    if not cik:
        return []

    company = get_company_name(ticker)
    data = _get_submissions(cik)
    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accessions = recent.get("accessionNumber", [])
    dates = recent.get("filingDate", [])
    primary_docs = recent.get("primaryDocument", [])

    results = []
    for i, form in enumerate(forms):
        if form == "8-K" and len(results) < max_count:
            accession = accessions[i].replace("-", "")
            doc = primary_docs[i]
            date = dates[i]
            url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{doc}"
            print(f"  [{ticker}] Downloading 8-K from {date}...")
            text = download_and_clean(url, max_chars=40000)
            results.append({
                "ticker": ticker.upper(),
                "company": company,
                "date": date,
                "text": text,
                "url": url,
                "form": "8-K",
            })

    print(f"  [{ticker}] Got {len(results)} 8-Ks")
    return results


def fetch_def14a(ticker: str) -> dict | None:
    """Fetch latest DEF 14A (proxy statement) for ticker."""
    print(f"  [{ticker}] Fetching DEF 14A (proxy)...")
    cik = get_cik(ticker)
    if not cik:
        return None

    company = get_company_name(ticker)
    data = _get_submissions(cik)
    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accessions = recent.get("accessionNumber", [])
    dates = recent.get("filingDate", [])
    primary_docs = recent.get("primaryDocument", [])

    for i, form in enumerate(forms):
        if form == "DEF 14A":
            accession = accessions[i].replace("-", "")
            doc = primary_docs[i]
            date = dates[i]
            url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{doc}"
            print(f"  [{ticker}] Downloading DEF 14A from {date}...")
            text = download_and_clean(url, max_chars=60000)
            print(f"  [{ticker}] DEF 14A: {len(text):,} chars")
            return {"ticker": ticker.upper(), "company": company, "date": date, "text": text, "url": url, "form": "DEF 14A"}

    print(f"  [{ticker}] No DEF 14A found")
    return None


def fetch_all_filings(ticker: str) -> dict:
    """Fetch all filing types needed for full scoring."""
    return {
        "ticker": ticker.upper(),
        "10k": fetch_10k(ticker),
        "8ks": fetch_8k_list(ticker),
        "def14a": fetch_def14a(ticker),
    }
