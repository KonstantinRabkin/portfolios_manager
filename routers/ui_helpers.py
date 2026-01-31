# routers/ui_helpers.py

from typing import Dict, List, Any, Tuple

from backup_utils import PORTFOLIOS  # data store [file:525]
from core.state import TAGS  # per-symbol tags [file:525]
from routers.ui_constants import TAG_LABELS  # semantic labels [file:525]


def build_positions_rows(
    pname: str,
    tickers: List[str],
    positions: Dict[str, Dict[str, float]],
    transactions: List[Dict[str, Any]],
    prices: Dict[str, float],
    sort_by: str,
    sort_dir: str,
) -> Tuple[str, float]:
    last_note_for_symbol: Dict[str, str] = {}
    for tx in transactions:
        sym = tx.get("symbol")
        note_tx = tx.get("note")
        if sym and note_tx:
            last_note_for_symbol[sym] = note_tx

    rows_data: List[Dict[str, Any]] = []
    total_pl = 0.0

    for symbol in tickers:
        price = prices.get(symbol)
        pos = positions.get(symbol, {})
        qty = pos.get("qty")
        buy = pos.get("buy")

        current_value = None
        cost_basis = None
        pl = None
        pl_pct = None

        if price is not None and qty is not None and buy is not None:
            current_value = price * qty
            cost_basis = buy * qty
            pl = current_value - cost_basis
            pl_pct = (pl / cost_basis * 100.0) if cost_basis != 0 else 0.0
            total_pl += pl or 0.0

        note_str = last_note_for_symbol.get(symbol, "")

        rows_data.append(
            {
                "symbol": symbol,
                "price": price,
                "qty": qty,
                "buy": buy,
                "cost_basis": cost_basis,
                "pl": pl,
                "pl_pct": pl_pct,
                "note": note_str,
            }
        )

    valid_sort_by = ["symbol", "price", "qty", "buy", "cost", "pl", "pl_pct"]
    if sort_by not in valid_sort_by:
        sort_by = "symbol"
    if sort_dir not in ["asc", "desc"]:
        sort_dir = "asc"

    def sort_key(row: Dict[str, Any]):
        if sort_by == "symbol":
            return row["symbol"] or ""
        if sort_by == "price":
            return row["price"] if row["price"] is not None else float("-inf")
        if sort_by == "qty":
            return row["qty"] if row["qty"] is not None else float("-inf")
        if sort_by == "buy":
            return row["buy"] if row["buy"] is not None else float("-inf")
        if sort_by == "cost":
            return row["cost_basis"] if row["cost_basis"] is not None else float("-inf")
        if sort_by == "pl":
            return row["pl"] if row["pl"] is not None else float("-inf")
        if sort_by == "pl_pct":
            return row["pl_pct"] if row["pl_pct"] is not None else float("-inf")
        return row["symbol"] or ""

    rows_data.sort(key=sort_key, reverse=(sort_dir == "desc"))

    rows_html = ""
    for row in rows_data:
        symbol = row["symbol"]
        price = row["price"]
        qty = row["qty"]
        buy = row["buy"]
        cost_basis = row["cost_basis"]
        pl = row["pl"]
        pl_pct = row["pl_pct"]
        note_str = row["note"]

        if price is not None and qty is not None and buy is not None:
            price_str = f"{price:.2f}"
            qty_str = f"{qty:g}"
            buy_str = f"{buy:.2f}"
            total_cost_str = f"{cost_basis:.2f}"
            pl_str = f"{pl:.2f}"
            pl_pct_str = f"{pl_pct:.2f}"
        else:
            price_str = f"{price:.2f}" if price is not None else "NA"
            qty_str = "-" if qty is None else f"{qty:g}"
            buy_str = "-" if buy is None else f"{buy:.2f}"
            total_cost_str = "-"
            pl_str = "-"
            pl_pct_str = "-"

        rows_html += f"""
        <tr class="ticker-row" data-symbol="{symbol}">
            <td><a href="https://ca.finance.yahoo.com/quote/{symbol}" target="_blank">{symbol}</a></td>
            <td>{price_str}</td>
            <td>{qty_str}</td>
            <td>{buy_str}</td>
            <td>{total_cost_str}</td>
            <td>{pl_str}</td>
            <td>{pl_pct_str}</td>
            <td>{note_str}</td>
            <td class="trade-cell">
                <form method="post" class="trade-form">
                    <input type="hidden" name="portfolio" value="{pname}">
                    <input type="hidden" name="symbol" value="{symbol}">
                    <input type="number" step="0.0001" name="qty" placeholder="Qty" class="trade-input qty">
                    <input type="number" step="0.01" name="price" placeholder="Price" class="trade-input price">
                    <input type="text" name="note" placeholder="Note" class="trade-input note">
                    <button type="submit" formaction="/buy">Buy</button>
                    <button type="submit" formaction="/sell">Sell</button>
                </form>
            </td>
        </tr>
        """

    return rows_html, total_pl


def build_history_rows(
    transactions: List[Dict[str, Any]],
    sort_by: str,
    sort_dir: str,
    row_class: str,
) -> str:
    valid_sort = ["time", "portfolio", "symbol", "action", "qty", "price"]
    if sort_by not in valid_sort:
        sort_by = "time"
    if sort_dir not in ["asc", "desc"]:
        sort_dir = "desc"

    def key_fn(tx: Dict[str, Any]):
        if sort_by == "time":
            return tx["time"]
        if sort_by == "portfolio":
            return tx["portfolio"]
        if sort_by == "symbol":
            return tx["symbol"]
        if sort_by == "action":
            return tx["action"]
        if sort_by == "qty":
            return tx["qty"]
        if sort_by == "price":
            return tx["price"]
        return tx["time"]

    sorted_txs = sorted(transactions, key=key_fn, reverse=(sort_dir == "desc"))
    rows = ""
    for tx in sorted_txs:
        rows += f"""
        <tr class="{row_class}">
            <td>{tx["time"]}</td>
            <td>{tx["portfolio"]}</td>
            <td>{tx["symbol"]}</td>
            <td>{tx["action"]}</td>
            <td>{tx["qty"]:g}</td>
            <td>{tx["price"]:.2f}</td>
            <td>{tx.get("note") or ""}</td>
        </tr>
        """
    if not rows:
        rows = """
        <tr>
            <td colspan="7" style="text-align:center;color:#666;">No transactions yet</td>
        </tr>
        """
    return rows


def build_summary(
    active_portfolio: str,
    portfolio_names: List[str],
    prices_by_pf: Dict[str, Dict[str, float]],
    summary_sort_by: str,
    summary_sort_dir: str,
) -> Dict[str, str]:
    all_symbols = set()
    for pf in PORTFOLIOS.values():
        all_symbols.update(pf["tickers"])
    all_symbols = sorted(all_symbols)

    summary_data: List[Dict[str, Any]] = []
    for sym in all_symbols:
        row = {"symbol": sym, "cells": {}}
        for pfname in portfolio_names:
            pf = PORTFOLIOS[pfname]
            pos = pf["positions"].get(sym)
            cell = {
                "has_pos": False,
                "qty": None,
                "buy": None,
                "cost": None,
                "pl_price": None,
                "pl_pct": None,
                "tag": None,
            }
            if pos and pos.get("qty") is not None and pos.get("buy") is not None:
                qty = pos["qty"]
                buy = pos["buy"]
                cost_basis = qty * buy
                cell["has_pos"] = True
                cell["qty"] = qty
                cell["buy"] = buy
                cell["cost"] = cost_basis
                price_map = prices_by_pf.get(pfname, {})
                price = price_map.get(sym)
                if price is not None:
                    current_value = price * qty
                    pl_val = current_value - cost_basis
                    pl_pct = pl_val / cost_basis * 100.0 if cost_basis != 0 else 0.0
                    cell["pl_price"] = pl_val
                    cell["pl_pct"] = pl_pct
                tag_val = TAGS.get(pfname, {}).get(sym)
                cell["tag"] = tag_val
            row["cells"][pfname] = cell
        summary_data.append(row)

    valid_summary_sort = ["symbol", "qty", "cost", "pl", "pl_pct"]
    if summary_sort_by not in valid_summary_sort:
        summary_sort_by = "symbol"
    if summary_sort_dir not in ["asc", "desc"]:
        summary_sort_dir = "asc"

    def summary_key(row: Dict[str, Any]):
        sym = row["symbol"]
        cell = row["cells"].get(active_portfolio, {})
        if summary_sort_by == "symbol":
            return sym
        if summary_sort_by == "qty":
            return cell.get("qty") if cell.get("qty") is not None else float("-inf")
        if summary_sort_by == "cost":
            return cell.get("cost") if cell.get("cost") is not None else float("-inf")
        if summary_sort_by == "pl":
            return cell.get("pl_price") if cell.get("pl_price") is not None else float("-inf")
        if summary_sort_by == "pl_pct":
            return cell.get("pl_pct") if cell.get("pl_pct") is not None else float("-inf")
        return sym

    summary_data.sort(key=summary_key, reverse=(summary_sort_dir == "desc"))

    summary_rows = ""
    for row in summary_data:
        sym = row["symbol"]
        row_html = f'<tr class="summary-row" data-symbol="{sym}"><td class="summary-symbol">{sym}</td>'
        for pfname in portfolio_names:
            cell = row["cells"].get(pfname, {})
            tag_val = cell.get("tag")
            if cell.get("has_pos"):
                qty = cell["qty"]
                buy = cell["buy"]
                cost_basis = cell["cost"]
                pl_price = cell["pl_price"]
                pl_pct = cell["pl_pct"]

                qty_str = f"{qty:g}"
                avg_str = f"{buy:.2f}"
                cost_str = f"{cost_basis:.2f}"
                if pl_price is not None and pl_pct is not None:
                    pl_price_str = f"{pl_price:.2f}"
                    pl_pct_str = f"{pl_pct:.2f}"
                    pl_cell_str = f"{pl_price_str} ({pl_pct_str}%)"
                else:
                    pl_cell_str = "-"

                if tag_val is None or not (0 <= tag_val < len(TAG_LABELS)):
                    tag_display = ""
                else:
                    tag_display = TAG_LABELS[tag_val]

                options_html = ""
                for idx, label in enumerate(TAG_LABELS):
                    selected_attr = "selected" if tag_display == label else ""
                    options_html += f'<option value="{idx}" {selected_attr}>{label}</option>'

                tag_select = f"""
                <form method="post" action="/summary/tag" class="summary-tag-form">
                    <input type="hidden" name="portfolio" value="{pfname}">
                    <input type="hidden" name="symbol" value="{sym}">
                    <select name="tag" class="summary-tag-select" onchange="this.form.submit()">
                        <option value="" {'selected' if not tag_display else ''}></option>
                        {options_html}
                    </select>
                </form>
                """

                cell_html = f"""
                <span class="cell-part">Qty: {qty_str}</span>
                <span class="cell-part">Avg: {avg_str}</span>
                <span class="cell-part">Cost: {cost_str}</span>
                <span class="cell-part">PL: {pl_cell_str}</span>
                <span class="cell-part">Tag: {tag_select}</span>
                """
            else:
                cell_html = '<span class="cell-empty"></span>'

            cell_tag_attr = ""
            if tag_val is not None and 0 <= tag_val < len(TAG_LABELS):
                cell_tag_attr = TAG_LABELS[tag_val]

            row_html += (
                f'<td class="summary-cell" data-pfname="{pfname}" '
                f'data-tag="{cell_tag_attr}">{cell_html}</td>'
            )

        row_html += "</tr>"
        summary_rows += row_html

    if not summary_rows:
        cols = len(portfolio_names) + 1
        summary_rows = f"""
        <tr>
            <td colspan="{cols}" style="text-align:center;color:#666;">No positions in any portfolio</td>
        </tr>
        """

    portfolio_header_cells = "".join(
        f'<th class="summary-header summary-header-col" data-pfname="{name}">{name}</th>'
        for name in portfolio_names
    )
    tag_filter_cells = "".join(
        '<td><input type="text" class="summary-tag-filter" '
        'placeholder="Tag labels, e.g. Buy, Sell" style="width:90px;"></td>'
        for _ in portfolio_names
    )

    return {
        "rows": summary_rows,
        "header_cells": portfolio_header_cells,
        "tag_filter_cells": tag_filter_cells,
    }


def build_sidebar_cards(
    portfolio_names: List[str],
    prices_by_pf: Dict[str, Dict[str, float]],
) -> str:
    sidebar_cards = ""
    for pfname in portfolio_names:
        pf = PORTFOLIOS[pfname]
        tickers = pf["tickers"]
        positions = pf["positions"]
        pf_prices = prices_by_pf.get(pfname, {})
        total_value = 0.0
        total_cost = 0.0
        for sym in tickers:
            pos = positions.get(sym)
            if not pos:
                continue
            qty = pos.get("qty")
            buy = pos.get("buy")
            if qty is None or buy is None:
                continue
            cost_val = qty * buy
            price_val = pf_prices.get(sym)
            value_val = price_val * qty if price_val is not None else cost_val
            total_cost += cost_val
            total_value += value_val
        pl_val = total_value - total_cost
        value_str = f"{total_value:.2f}"
        pl_str = f"{pl_val:.2f}"
        pl_class = "pos" if pl_val >= 0 else "neg"
        sidebar_cards += f"""
        <div class="pf-card">
            <div class="pf-title">{pfname}</div>
            <div class="pf-line">
                <span>Total value</span><span>{value_str}</span>
            </div>
            <div class="pf-line">
                <span>Total PL</span><span class="{pl_class}">{pl_str}</span>
            </div>
        </div>
        """
    return sidebar_cards


def build_charts_html(portfolio_names: List[str]) -> str:
    charts_html = ""
    for pfname in portfolio_names:
        charts_html += f"""
        <div class="chart-placeholder">
            <div class="chart-title">{pfname} growth</div>
            <div class="chart-box">
                <img src="/chart/{pfname}" alt="{pfname} chart" style="max-width:100%;max-height:100%;">
            </div>
        </div>
        """
    return charts_html


def toggle_col(current_by: str, current_dir: str, col: str) -> str:
    if current_by == col and current_dir == "asc":
        return "desc"
    return "asc"

