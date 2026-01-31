from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse
from datetime import datetime

from backup_utils import PORTFOLIOS, DEFAULT_PORTFOLIO, rebuild_portfolio_history_from_transactions
from core.state import TAGS

router = APIRouter()


@router.post("/add")
async def add_ticker(portfolio: str = Form(...), symbol: str = Form(...)):
    p_name = portfolio.strip() or DEFAULT_PORTFOLIO
    symbol = symbol.strip().upper()
    if p_name not in PORTFOLIOS:
        PORTFOLIOS[p_name] = {"tickers": [], "positions": {}, "transactions": []}
    pf = PORTFOLIOS[p_name]
    if symbol and symbol not in pf["tickers"]:
        pf["tickers"].append(symbol)
        pf["tickers"].sort()
    return RedirectResponse(url=f"/?portfolio={p_name}", status_code=303)


@router.post("/remove")
async def remove_ticker(portfolio: str = Form(...), symbol: str = Form(...)):
    p_name = portfolio.strip() or DEFAULT_PORTFOLIO
    symbol = symbol.strip().upper()
    if p_name in PORTFOLIOS:
        pf = PORTFOLIOS[p_name]
        if symbol in pf["tickers"]:
            pf["tickers"].remove(symbol)
        pf["positions"].pop(symbol, None)
    if p_name in TAGS and symbol in TAGS[p_name]:
        TAGS[p_name].pop(symbol, None)
    return RedirectResponse(url=f"/?portfolio={p_name}", status_code=303)


@router.post("/buy")
async def buy(
    portfolio: str = Form(...),
    symbol: str = Form(...),
    qty: float = Form(...),
    price: float = Form(...),
    note: str = Form(""),
):
    p_name = portfolio.strip() or DEFAULT_PORTFOLIO
    symbol = symbol.strip().upper()
    if p_name not in PORTFOLIOS:
        PORTFOLIOS[p_name] = {"tickers": [], "positions": {}, "transactions": []}
    pf = PORTFOLIOS[p_name]

    if symbol not in pf["tickers"]:
        pf["tickers"].append(symbol)
        pf["tickers"].sort()

    pos = pf["positions"].get(symbol, {"qty": 0.0, "buy": 0.0})
    old_qty = pos["qty"]
    old_buy = pos["buy"]
    new_qty = old_qty + qty
    if new_qty > 0:
        new_buy = (old_buy * old_qty + price * qty) / new_qty if old_qty > 0 else price
    else:
        new_buy = price
    pos["qty"] = new_qty
    pos["buy"] = new_buy
    pf["positions"][symbol] = pos

    pf["transactions"].append(
        {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "portfolio": p_name,
            "symbol": symbol,
            "action": "BUY",
            "qty": qty,
            "price": price,
            "note": note,
        }
    )

    rebuild_portfolio_history_from_transactions(p_name)
    return RedirectResponse(url=f"/?portfolio={p_name}", status_code=303)


@router.post("/sell")
async def sell(
    portfolio: str = Form(...),
    symbol: str = Form(...),
    qty: float = Form(...),
    price: float = Form(...),
    note: str = Form(""),
):
    p_name = portfolio.strip() or DEFAULT_PORTFOLIO
    symbol = symbol.strip().upper()
    if p_name not in PORTFOLIOS:
        PORTFOLIOS[p_name] = {"tickers": [], "positions": {}, "transactions": []}
    pf = PORTFOLIOS[p_name]

    pos = pf["positions"].get(symbol, {"qty": 0.0, "buy": 0.0})
    old_qty = pos["qty"]
    new_qty = max(0.0, old_qty - qty)
    pos["qty"] = new_qty
    pf["positions"][symbol] = pos

    pf["transactions"].append(
        {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "portfolio": p_name,
            "symbol": symbol,
            "action": "SELL",
            "qty": qty,
            "price": price,
            "note": note,
        }
    )

    rebuild_portfolio_history_from_transactions(p_name)
    return RedirectResponse(url=f"/?portfolio={p_name}", status_code=303)

