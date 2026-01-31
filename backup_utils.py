import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Shared in-memory state
PORTFOLIOS: Dict[str, Dict[str, Any]] = {}
PORTFOLIO_HISTORY: Dict[str, List[Dict[str, Any]]] = {}
DEFAULT_PORTFOLIO: str = "Default"

# Backups directory inside container (bind-mounted on host)
BACKUP_DIR = Path("/app/backups")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


# ---------- Price fetching ----------

async def fetch_prices(tickers, api_key: str) -> Dict[str, float]:
    import httpx

    if not tickers:
        return {}

    prices: Dict[str, float] = {}
    async with httpx.AsyncClient(timeout=10) as client:
        for symbol in tickers:
            try:
                r = await client.get(
                    "https://finnhub.io/api/v1/quote",
                    params={"symbol": symbol, "token": api_key},
                )
                r.raise_for_status()
                data = r.json()
                price = data.get("c")
                if isinstance(price, (int, float)):
                    prices[symbol] = float(price)
            except Exception:
                continue
    return prices


# ---------- History helpers ----------

def update_portfolio_history_point(
    portfolio_name: str,
    tickers,
    positions,
    prices: Dict[str, float],
) -> None:
    total_value = 0.0
    for sym in tickers:
        pos = positions.get(sym)
        if not pos:
            continue
        qty = pos.get("qty")
        buy = pos.get("buy")
        if qty is None or buy is None:
            continue
        price = prices.get(sym, buy)
        total_value += (price or 0.0) * qty

    hist = PORTFOLIO_HISTORY.setdefault(portfolio_name, [])
    hist.append(
        {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "value": total_value,
        }
    )


def rebuild_portfolio_history_from_transactions(portfolio_name: str) -> None:
    pf = PORTFOLIOS.get(portfolio_name)
    if not pf:
        PORTFOLIO_HISTORY[portfolio_name] = []
        return

    hist: List[Dict[str, Any]] = []
    running_cost = 0.0

    for tx in sorted(pf["transactions"], key=lambda t: t["time"]):
        qty = tx.get("qty", 0.0) or 0.0
        price = tx.get("price", 0.0) or 0.0
        if tx.get("action") == "BUY":
            running_cost += qty * price
        elif tx.get("action") == "SELL":
            running_cost -= qty * price

        hist.append(
            {
                "time": tx["time"],
                "value": running_cost,
            }
        )

    PORTFOLIO_HISTORY[portfolio_name] = hist


# ---------- Backup / restore ----------

def _state_to_dict() -> Dict[str, Any]:
    return {
        "PORTFOLIOS": PORTFOLIOS,
        "PORTFOLIO_HISTORY": PORTFOLIO_HISTORY,
        "DEFAULT_PORTFOLIO": DEFAULT_PORTFOLIO,
    }


def _state_from_dict(data: Dict[str, Any]) -> None:
    global PORTFOLIOS, PORTFOLIO_HISTORY, DEFAULT_PORTFOLIO
    PORTFOLIOS.clear()
    PORTFOLIO_HISTORY.clear()
    PORTFOLIOS.update(data.get("PORTFOLIOS", {}))
    PORTFOLIO_HISTORY.update(data.get("PORTFOLIO_HISTORY", {}))
    DEFAULT_PORTFOLIO = data.get("DEFAULT_PORTFOLIO", "Default")


def create_backup_file() -> Path:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = BACKUP_DIR / f"backup-{ts}.json"
    path.write_text(json.dumps(_state_to_dict(), indent=2, sort_keys=True))
    return path


def list_backups() -> List[Path]:
    return sorted(BACKUP_DIR.glob("backup-*.json"))


def get_latest_backup_path() -> Optional[Path]:
    files = list_backups()
    return files[-1] if files else None


def restore_from_bytes(content: bytes) -> None:
    data = json.loads(content.decode("utf-8"))
    _state_from_dict(data)


def load_latest_backup_on_startup() -> None:
    path = get_latest_backup_path()
    if not path:
        return
    try:
        data = json.loads(path.read_text())
        _state_from_dict(data)
    except Exception:
        pass

