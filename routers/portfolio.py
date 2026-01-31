from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse
from backup_utils import PORTFOLIOS, PORTFOLIO_HISTORY, DEFAULT_PORTFOLIO
from core.state import TAGS

router = APIRouter()

@router.post("/portfolio/add")
async def portfolio_add(name: str = Form(...)):
    new_name = name.strip()
    if new_name and new_name not in PORTFOLIOS:
        PORTFOLIOS[new_name] = {"tickers": [], "positions": {}, "transactions": []}
    return RedirectResponse(url=f"/?portfolio={new_name}", status_code=303)


@router.post("/portfolio/rename")
async def portfolio_rename(old_name: str = Form(...), new_name: str = Form(...)):
    global DEFAULT_PORTFOLIO
    old = old_name.strip()
    new = new_name.strip()
    if old in PORTFOLIOS and new and new not in PORTFOLIOS:
        PORTFOLIOS[new] = PORTFOLIOS.pop(old)
        if old == DEFAULT_PORTFOLIO:
            DEFAULT_PORTFOLIO = new
        if old in PORTFOLIO_HISTORY:
            PORTFOLIO_HISTORY[new] = PORTFOLIO_HISTORY.pop(old)
        if old in TAGS:
            TAGS[new] = TAGS.pop(old)
    return RedirectResponse(url=f"/?portfolio={new}", status_code=303)


@router.post("/portfolio/remove")
async def portfolio_remove(name: str = Form(...)):
    global DEFAULT_PORTFOLIO
    p_name = name.strip()
    if p_name in PORTFOLIOS and len(PORTFOLIOS) > 1:
        PORTFOLIOS.pop(p_name)
        PORTFOLIO_HISTORY.pop(p_name, None)
        TAGS.pop(p_name, None)
        if p_name == DEFAULT_PORTFOLIO:
            new_default = next(iter(PORTFOLIOS.keys()))
            DEFAULT_PORTFOLIO = new_default
            return RedirectResponse(url=f"/?portfolio={new_default}", status_code=303)
    return RedirectResponse(url="/", status_code=303)


@router.post("/summary/tag")
async def set_summary_tag(
    portfolio: str = Form(...),
    symbol: str = Form(...),
    tag: str = Form(""),
):
    p_name = portfolio.strip() or DEFAULT_PORTFOLIO
    sym = symbol.strip().upper()
    if p_name not in TAGS:
        TAGS[p_name] = {}
    if tag == "":
        TAGS[p_name].pop(sym, None)
    else:
        try:
            val = int(tag)
            if 0 <= val <= 9:
                TAGS[p_name][sym] = val
        except ValueError:
            pass
    return RedirectResponse(url=f"/?portfolio={p_name}", status_code=303)

