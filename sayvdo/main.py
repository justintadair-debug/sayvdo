"""FastAPI web app for Say vs. Do."""

import json
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os

from sayvdo.core import scorer, history
from sayvdo.worklog import log_scan

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app = FastAPI(title="Say vs. Do", version="1.0.0")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    tickers = history.get_all_tickers()
    recent = []
    for t in tickers[:12]:
        row = history.get_latest(t)
        if row:
            recent.append(row)
    recent.sort(key=lambda r: r.get("composite_score", 0), reverse=True)
    return templates.TemplateResponse("index.html", {"request": request, "recent": recent})


@app.get("/score/{ticker}", response_class=HTMLResponse)
async def score_page(request: Request, ticker: str):
    ticker = ticker.upper()
    # Check for cached result
    latest = history.get_latest(ticker)
    hist = history.get_history(ticker)
    if latest:
        result = json.loads(latest["scores_json"])
    else:
        result = None
    return templates.TemplateResponse("report.html", {
        "request": request,
        "ticker": ticker,
        "result": result,
        "history": hist,
    })


@app.post("/score/{ticker}")
async def run_score(ticker: str):
    ticker = ticker.upper()
    result = scorer.run(ticker)
    history.save_score(result)
    log_scan(ticker, result["composite_score"], result["quarter"])
    return JSONResponse(result)


@app.get("/api/score/{ticker}")
async def api_score(ticker: str, fresh: bool = False):
    ticker = ticker.upper()
    if not fresh:
        latest = history.get_latest(ticker)
        if latest:
            return JSONResponse(json.loads(latest["scores_json"]))
    result = scorer.run(ticker)
    history.save_score(result)
    log_scan(ticker, result["composite_score"], result["quarter"])
    return JSONResponse(result)


@app.get("/api/history/{ticker}")
async def api_history(ticker: str):
    return JSONResponse(history.get_history(ticker.upper()))


@app.get("/health")
async def health():
    return {"status": "ok", "service": "sayvdo"}
