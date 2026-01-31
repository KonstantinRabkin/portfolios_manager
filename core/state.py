from typing import Dict, Optional
from backup_utils import PORTFOLIOS, PORTFOLIO_HISTORY, DEFAULT_PORTFOLIO

FINNHUB_API_KEY = ""

TAGS: Dict[str, Dict[str, int]] = {}


def resolve_portfolio(q: Optional[str]) -> str:
    """
    - If ?portfolio=<name> and <name> exists in PORTFOLIOS, use it.
    - Otherwise fall back to DEFAULT_PORTFOLIO (if exists) or first portfolio,
      or create a new 'Default' if nothing exists.
    """
    global DEFAULT_PORTFOLIO

    if q:
        name = q.strip()
        if name in PORTFOLIOS:
            return name

    if DEFAULT_PORTFOLIO in PORTFOLIOS:
        return DEFAULT_PORTFOLIO

    if PORTFOLIOS:
        return next(iter(PORTFOLIOS.keys()))

    DEFAULT_PORTFOLIO = "Default"
    PORTFOLIOS[DEFAULT_PORTFOLIO] = {
        "tickers": [],
        "positions": {},
        "transactions": [],
    }
    return DEFAULT_PORTFOLIO

