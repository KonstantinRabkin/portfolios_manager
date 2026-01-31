import json
from pathlib import Path
from typing import List, Dict

from backup_utils import PORTFOLIOS

# Where to store the order on disk
CONFIG_PATH = Path("/app/config/summary_order.json")


def _load_raw_config() -> Dict:
    if not CONFIG_PATH.exists():
        return {}
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_raw_config(data: Dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def get_portfolio_summary_order() -> List[str]:
    """
    Return the portfolio order for the summary table.
    If config is missing or stale, fall back to current PORTFOLIOS.keys().
    """
    cfg = _load_raw_config()
    cfg_order = cfg.get("summary_order")

    current_names = list(PORTFOLIOS.keys())

    if not current_names:
        return []

    # If no config or config not a list -> default
    if not isinstance(cfg_order, list):
        return current_names

    # Keep only existing portfolios, in configured order
    seen = set()
    ordered = []
    for name in cfg_order:
        if name in PORTFOLIOS and name not in seen:
            ordered.append(name)
            seen.add(name)

    # Append any new portfolios not yet in config
    for name in current_names:
        if name not in seen:
            ordered.append(name)
            seen.add(name)

    return ordered


def set_portfolio_summary_order(order: List[str]) -> None:
    """
    Persist a new summary order.
    `order` should be a list of portfolio names in desired order.
    """
    # Filter against existing portfolios, dedupe
    seen = set()
    cleaned: List[str] = []
    for name in order:
        if name in PORTFOLIOS and name not in seen:
            cleaned.append(name)
            seen.add(name)

    # Add any portfolios that were omitted
    for name in PORTFOLIOS.keys():
        if name not in seen:
            cleaned.append(name)
            seen.add(name)

    data = _load_raw_config()
    data["summary_order"] = cleaned
    _save_raw_config(data)

