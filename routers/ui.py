# routers/ui.py

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse, Response
from typing import Optional, Dict, List, Any
import io
import matplotlib.pyplot as plt

from backup_utils import (
    PORTFOLIOS,
    PORTFOLIO_HISTORY,
    fetch_prices,
    update_portfolio_history_point,
)
from core.state import resolve_portfolio, FINNHUB_API_KEY
from config.summary_order import get_portfolio_summary_order

from routers.ui_constants import STYLE_BLOCK
from routers.ui_helpers import (
    build_positions_rows,
    build_history_rows,
    build_summary,
    build_sidebar_cards,
    build_charts_html,
    toggle_col,
)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(
    portfolio: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("symbol"),
    sort_dir: Optional[str] = Query("asc"),
    summary_sort_by: Optional[str] = Query("symbol"),
    summary_sort_dir: Optional[str] = Query("asc"),
    history_sort_by: Optional[str] = Query("time"),
    history_sort_dir: Optional[str] = Query("desc"),
    global_sort_by: Optional[str] = Query("time"),
    global_sort_dir: Optional[str] = Query("desc"),
):
    pname = resolve_portfolio(portfolio)

    if pname not in PORTFOLIOS:
        PORTFOLIOS[pname] = {
            "tickers": ["TECL", "AAPL", "MSFT", "GOOG"],
            "positions": {},
            "transactions": [],
        }

    p = PORTFOLIOS[pname]
    TICKERS = p["tickers"]
    POSITIONS = p["positions"]
    TRANSACTIONS = p["transactions"]

    prices = await fetch_prices(TICKERS, FINNHUB_API_KEY)
    update_portfolio_history_point(pname, TICKERS, POSITIONS, prices)

    rows_html, total_pl = build_positions_rows(
        pname, TICKERS, POSITIONS, TRANSACTIONS, prices, sort_by or "symbol", sort_dir or "asc"
    )
    total_pl_str = f"{total_pl:.2f}"
    current_list = ", ".join(TICKERS) if TICKERS else "none"

    history_rows = build_history_rows(
        TRANSACTIONS, history_sort_by or "time", history_sort_dir or "desc", "history-row"
    )

    all_txs: List[Dict[str, Any]] = []
    for pfname, pf in PORTFOLIOS.items():
        all_txs.extend(pf["transactions"])
    global_history_rows = build_history_rows(
        all_txs, global_sort_by or "time", global_sort_dir or "desc", "global-history-row"
    )

    portfolio_names = get_portfolio_summary_order()

    portfolio_options = ""
    for name in portfolio_names:
        selected = "selected" if name == pname else ""
        portfolio_options += f'<option value="{name}" {selected}>{name}</option>'

    pf_prices_all: Dict[str, Dict[str, float]] = {}
    for pfname, pf in PORTFOLIOS.items():
        tickers = pf["tickers"]
        if pfname == pname:
            pf_prices_all[pfname] = prices
        else:
            pf_prices_all[pfname] = await fetch_prices(tickers, FINNHUB_API_KEY)

    summary_parts = build_summary(
        active_portfolio=pname,
        portfolio_names=portfolio_names,
        prices_by_pf=pf_prices_all,
        summary_sort_by=summary_sort_by or "symbol",
        summary_sort_dir=summary_sort_dir or "asc",
    )

    sidebar_cards = build_sidebar_cards(portfolio_names, pf_prices_all)
    charts_html = build_charts_html(portfolio_names)

    toggle_symbol = toggle_col(sort_by, sort_dir, "symbol")
    toggle_price = toggle_col(sort_by, sort_dir, "price")
    toggle_qty = toggle_col(sort_by, sort_dir, "qty")
    toggle_buy = toggle_col(sort_by, sort_dir, "buy")
    toggle_cost = toggle_col(sort_by, sort_dir, "cost")
    toggle_pl = toggle_col(sort_by, sort_dir, "pl")
    toggle_pl_pct = toggle_col(sort_by, sort_dir, "pl_pct")

    summary_toggle_symbol = toggle_col(summary_sort_by, summary_sort_dir, "symbol")
    summary_toggle_qty = toggle_col(summary_sort_by, summary_sort_dir, "qty")
    summary_toggle_cost = toggle_col(summary_sort_by, summary_sort_dir, "cost")
    summary_toggle_pl = toggle_col(summary_sort_by, summary_sort_dir, "pl")
    summary_toggle_pl_pct = toggle_col(summary_sort_by, summary_sort_dir, "pl_pct")

    hist_toggle_time = toggle_col(history_sort_by, history_sort_dir, "time")
    hist_toggle_portfolio = toggle_col(history_sort_by, history_sort_dir, "portfolio")
    hist_toggle_symbol = toggle_col(history_sort_by, history_sort_dir, "symbol")
    hist_toggle_action = toggle_col(history_sort_by, history_sort_dir, "action")
    hist_toggle_qty = toggle_col(history_sort_by, history_sort_dir, "qty")
    hist_toggle_price = toggle_col(history_sort_by, history_sort_dir, "price")

    glob_toggle_time = toggle_col(global_sort_by, global_sort_dir, "time")
    glob_toggle_portfolio = toggle_col(global_sort_by, global_sort_dir, "portfolio")
    glob_toggle_symbol = toggle_col(global_sort_by, global_sort_dir, "symbol")
    glob_toggle_action = toggle_col(global_sort_by, global_sort_dir, "action")
    glob_toggle_qty = toggle_col(global_sort_by, global_sort_dir, "qty")
    glob_toggle_price = toggle_col(global_sort_by, global_sort_dir, "price")

    error_block = f'<div class="error-box">{error}</div>' if error else ""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Portfolio Manager</title>
    <meta http-equiv="refresh" content="120">
    {STYLE_BLOCK}
</head>
<body>
<div class="page-root">
    <div class="top-header">
        <h1>Portfolio Manager</h1>
        <div class="updated">
            Auto-refreshes every 120 seconds. Data: Finnhub.io.
        </div>
        {error_block}
    </div>

    <div class="top-layout">
        <div class="top-main">
            <div class="controls">
                <div class="controls-header">
                    <h3 style="margin:0;">Portfolios</h3>
                    <button type="button" class="controls-toggle-btn" id="toggle-extra-btn">More actions</button>
                </div>
                <div class="controls-main">
                    <form method="get" action="/">
                        <label>Active</label>
                        <select name="portfolio" onchange="this.form.submit()">
                            {portfolio_options}
                        </select>
                    </form>

                    <form method="post" action="/add">
                        <input type="hidden" name="portfolio" value="{pname}">
                        <label>Add ticker</label>
                        <input type="text" name="symbol" placeholder="e.g. NVDA" required style="width:80px;">
                        <input type="submit" value="Add">
                    </form>

                    <form method="post" action="/remove">
                        <input type="hidden" name="portfolio" value="{pname}">
                        <label>Remove ticker</label>
                        <input type="text" name="symbol" placeholder="e.g. MSFT" required style="width:80px;">
                        <input type="submit" value="Remove">
                    </form>
                </div>

                <div class="filter-row" style="margin-top:0;">
                    <label>Filter tickers</label>
                    <input type="text" id="ticker-filter" placeholder="e.g. NVDA, AAPL">
                </div>

                <div class="controls-extra" id="controls-extra">
                    <div style="margin-top:2px;font-size:11px;color:#666;">
                        Portfolio management
                    </div>

                    <div style="margin:2px 0 4px 0;font-size:11px;">
                        <a href="/config/summary-order" target="_blank">
                            Change portfolio order
                        </a>
                    </div>

                    <form method="post" action="/portfolio/add">
                        <label>Add portfolio</label>
                        <input type="text" name="name" placeholder="Name" required style="width:90px;">
                        <input type="submit" value="Add">
                    </form>

                    <form method="post" action="/portfolio/rename">
                        <input type="hidden" name="oldname" value="{pname}">
                        <label>Rename</label>
                        <input type="text" name="newname" placeholder="Name" required style="width:90px;">
                        <input type="submit" value="Rename">
                    </form>

                    <form method="post" action="/portfolio/remove" onsubmit="return confirm('Remove portfolio?');">
                        <input type="hidden" name="name" value="{pname}">
                        <input type="submit" value="Remove portfolio">
                    </form>

                    <div style="margin-top:6px;font-size:11px;color:#666;">
                        Import / export portfolio
                    </div>

                    <form method="get" action="/portfolio/download">
                        <input type="hidden" name="portfolio" value="{pname}">
                        <input type="submit" value="Download XLSX">
                    </form>

                    <form method="post" action="/portfolio/upload" enctype="multipart/form-data">
                        <input type="hidden" name="portfolio" value="{pname}">
                        <label>Upload XLSX</label>
                        <input type="file" name="file" accept=".xlsx" required>
                        <input type="submit" value="Upload">
                    </form>

                    <form method="get" action="/portfolio/exportcsv">
                        <input type="hidden" name="portfolio" value="{pname}">
                        <input type="submit" value="Export CSV">
                    </form>

                    <form method="post" action="/importcsv" enctype="multipart/form-data">
                        <input type="hidden" name="portfolioname" value="{pname}">
                        <label>Import CSV into active</label>
                        <input type="file" name="file" accept=".csv" required>
                        <input type="submit" value="Import CSV">
                    </form>

                    <div style="margin-top:6px;font-size:11px;color:#666;">
                        Bulk CSV import (one click)
                    </div>

                    <form method="post" action="/importcsvmulti" enctype="multipart/form-data">
                        <div style="font-size:11px;color:#444;margin-bottom:2px;">
                            Enter portfolio names comma separated, order matches selected CSVs.
                        </div>
                        <input type="text" name="portfolionames"
                               placeholder="Watch list, RRSP, TFSA"
                               style="width:260px;font-size:11px;"><br>
                        <input type="file" name="files" accept=".csv" multiple required>
                        <input type="submit" value="Import all CSVs">
                    </form>

                    <div style="margin-top:6px;font-size:11px;color:#666;">
                        Global JSON backup
                    </div>

                    <form method="post" action="/backup/create" class="backup-btn">
                        <input type="submit" value="Create JSON backup">
                    </form>

                    <form method="post" action="/backup/restore" enctype="multipart/form-data" class="backup-btn">
                        <label>Restore JSON</label>
                        <input type="file" name="file" accept=".json" required>
                        <input type="submit" value="Restore">
                    </form>

                    <div class="tickers-list">
                        <strong>Current portfolio:</strong> {pname} |
                        <strong>Tickers:</strong> {current_list}
                    </div>
                </div>
            </div>

            <div class="panel">
                <h2>{pname} positions</h2>
                <table id="positions-table">
                    <tr>
                        <th>
                            <a href="/?portfolio={pname}&sort_by=symbol&sort_dir={toggle_symbol}">Ticker</a>
                        </th>
                        <th>
                            <a href="/?portfolio={pname}&sort_by=price&sort_dir={toggle_price}">Current price</a>
                        </th>
                        <th>
                            <a href="/?portfolio={pname}&sort_by=qty&sort_dir={toggle_qty}">Qty</a>
                        </th>
                        <th>
                            <a href="/?portfolio={pname}&sort_by=buy&sort_dir={toggle_buy}">Buy price</a>
                        </th>
                        <th>
                            <a href="/?portfolio={pname}&sort_by=cost&sort_dir={toggle_cost}">Total cost</a>
                        </th>
                        <th>
                            <a href="/?portfolio={pname}&sort_by=pl&sort_dir={toggle_pl}">P/L</a>
                        </th>
                        <th>
                            <a href="/?portfolio={pname}&sort_by=pl_pct&sort_dir={toggle_pl_pct}">P/L %</a>
                        </th>
                        <th>Note</th>
                        <th>Trade</th>
                    </tr>
                    {rows_html}
                </table>
                <div class="total-pl">
                    Total P/L (all tickers in {pname}): {total_pl_str}
                </div>
            </div>
        </div>

        <div class="sidebar">
            <div class="sidebar-card-wrapper">
                <div class="sidebar-title">Today summary</div>
                {sidebar_cards}
            </div>
            <div class="charts-wrapper">
                <div class="charts-title">Portfolio growth</div>
                {charts_html}
            </div>
        </div>
    </div>

    <div class="bottom-layout">
        <div class="panel summary-wrapper">
            <h3>Portfolios summary (all portfolios)</h3>
            <div class="filter-row">
                <label>Filter summary (text: tickers or any text, comma separated)</label>
                <input type="text" id="summary-filter" placeholder="e.g. MA, AXP, AMD">
            </div>
            <table id="summary-table">
                <tr>
                    <th class="summary-header">
                        <a href="/?portfolio={pname}&summary_sort_by=symbol&summary_sort_dir={summary_toggle_symbol}">Ticker</a>
                    </th>
                    {summary_parts["header_cells"]}
                </tr>
                <tr class="summary-tag-filter-row">
                    <td style="font-weight:bold;">Tag filter per portfolio, use labels e.g. Buy, Sell, Review Thesis</td>
                    {summary_parts["tag_filter_cells"]}
                </tr>
                {summary_parts["rows"]}
            </table>
        </div>

        <div class="panel">
            <h3>{pname} history</h3>
            <div class="filter-row">
                <label>Filter history</label>
                <input type="text" id="history-filter" placeholder="Any text in row">
            </div>
            <table id="history-table">
                <tr>
                    <th><a href="/?portfolio={pname}&history_sort_by=time&history_sort_dir={hist_toggle_time}">Time</a></th>
                    <th><a href="/?portfolio={pname}&history_sort_by=portfolio&history_sort_dir={hist_toggle_portfolio}">Portfolio</a></th>
                    <th><a href="/?portfolio={pname}&history_sort_by=symbol&history_sort_dir={hist_toggle_symbol}">Ticker</a></th>
                    <th><a href="/?portfolio={pname}&history_sort_by=action&history_sort_dir={hist_toggle_action}">Action</a></th>
                    <th><a href="/?portfolio={pname}&history_sort_by=qty&history_sort_dir={hist_toggle_qty}">Qty</a></th>
                    <th><a href="/?portfolio={pname}&history_sort_by=price&history_sort_dir={hist_toggle_price}">Price</a></th>
                    <th>Note</th>
                </tr>
                {history_rows}
            </table>
        </div>

        <div class="panel">
            <h3>All portfolios history</h3>
            <div class="filter-row">
                <label>Filter all history</label>
                <input type="text" id="global-history-filter" placeholder="Any text in row">
            </div>
            <table id="global-history-table">
                <tr>
                    <th><a href="/?portfolio={pname}&global_sort_by=time&global_sort_dir={glob_toggle_time}">Time</a></th>
                    <th><a href="/?portfolio={pname}&global_sort_by=portfolio&global_sort_dir={glob_toggle_portfolio}">Portfolio</a></th>
                    <th><a href="/?portfolio={pname}&global_sort_by=symbol&global_sort_dir={glob_toggle_symbol}">Ticker</a></th>
                    <th><a href="/?portfolio={pname}&global_sort_by=action&global_sort_dir={glob_toggle_action}">Action</a></th>
                    <th><a href="/?portfolio={pname}&global_sort_by=qty&global_sort_dir={glob_toggle_qty}">Qty</a></th>
                    <th><a href="/?portfolio={pname}&global_sort_by=price&global_sort_dir={glob_toggle_price}">Price</a></th>
                    <th>Note</th>
                </tr>
                {global_history_rows}
            </table>
        </div>
    </div>
</div>
<script>
    (function() {{
        const btn = document.getElementById('toggle-extra-btn');
        const extra = document.getElementById('controls-extra');
        if (!btn || !extra) return;
        let visible = false;
        btn.addEventListener('click', function() {{
            visible = !visible;
            extra.style.display = visible ? 'block' : 'none';
            btn.textContent = visible ? 'Less actions' : 'More actions';
        }});
    }})();

    function attachTableFilter(inputId, tableId, rowClass, skipHeaderRows) {{
        const input = document.getElementById(inputId);
        const table = document.getElementById(tableId);
        if (!input || !table) return;
        input.addEventListener('input', function() {{
            const val = input.value.trim().toUpperCase();
            let rows;
            if (rowClass) {{
                rows = table.querySelectorAll('tr.' + rowClass);
            }} else {{
                rows = Array.prototype.slice.call(table.getElementsByTagName('tr'), skipHeaderRows);
            }}
            rows.forEach(function(row) {{
                let text = row.textContent || row.innerText || '';
                text = text.toUpperCase();
                row.style.display = text.indexOf(val) !== -1 ? '' : 'none';
            }});
        }});
    }}

    (function() {{
        const filterInput = document.getElementById('ticker-filter');
        const table = document.getElementById('positions-table');
        if (!filterInput || !table) return;
        function applyFilter() {{
            const val = filterInput.value.trim().toUpperCase();
            const tokens = val.split(',').map(s => s.trim()).filter(Boolean);
            const rows = table.querySelectorAll('tr.ticker-row');
            if (tokens.length === 0) {{
                rows.forEach(r => r.style.display = '');
                return;
            }}
            rows.forEach(row => {{
                const sym = (row.getAttribute('data-symbol') || '').toUpperCase();
                const match = tokens.some(t => sym.includes(t));
                row.style.display = match ? '' : 'none';
            }});
        }}
        filterInput.addEventListener('input', applyFilter);
    }})();

    attachTableFilter('history-filter', 'history-table', 'history-row', 1);
    attachTableFilter('global-history-filter', 'global-history-table', 'global-history-row', 1);

    function parseTokens(str) {{
        return str.split(',').map(s => s.trim().toUpperCase()).filter(Boolean);
    }}

    function applySummaryFilters() {{
        const table = document.getElementById('summary-table');
        if (!table) return;
        const rows = table.querySelectorAll('tr.summary-row');
        const headerCells = table.querySelectorAll('th.summary-header-col');
        const tagFilters = table.querySelectorAll('.summary-tag-filter');
        const summaryInput = document.getElementById('summary-filter');
        const textTokens = summaryInput ? parseTokens(summaryInput.value) : [];

        const activeTagFilters = [];
        headerCells.forEach((th, idx) => {{
            const pfName = th.getAttribute('data-pfname');
            const input = tagFilters[idx];
            if (!input) return;
            const tokens = parseTokens(input.value);
            if (tokens.length > 0) {{
                activeTagFilters.push({{ pfName, tags: tokens }});
            }}
        }});

        rows.forEach(row => {{
            const symbol = (row.getAttribute('data-symbol') || '').toUpperCase();
            let visible = true;
            if (textTokens.length > 0) {{
                const rowText = (row.textContent || row.innerText || '').toUpperCase();
                const matchAny = textTokens.some(tok => symbol.includes(tok) || rowText.includes(tok));
                if (!matchAny) visible = false;
            }}
            if (visible && activeTagFilters.length > 0) {{
                for (const f of activeTagFilters) {{
                    const cell = row.querySelector('td.summary-cell[data-pfname=\"' + f.pfName + '\"]');
                    if (!cell) {{ visible = false; break; }}
                    const tag = (cell.getAttribute('data-tag') || '').toUpperCase();
                    if (!tag) {{ visible = false; break; }}
                    if (!f.tags.some(t => tag.includes(t))) {{ visible = false; break; }}
                }}
            }}
            row.style.display = visible ? '' : 'none';
        }});
    }}

    (function() {{
        const table = document.getElementById('summary-table');
        if (!table) return;
        const tagInputs = table.querySelectorAll('.summary-tag-filter');
        tagInputs.forEach(inp => {{
            inp.addEventListener('input', applySummaryFilters);
        }});
        const summaryInput = document.getElementById('summary-filter');
        if (summaryInput) {{
            summaryInput.addEventListener('input', applySummaryFilters);
        }}
    }})();
</script>
</body>
</html>
"""

    return HTMLResponse(html)


@router.get("/chart/{portfolio_name}")
async def chart(portfolio_name: str):
    if portfolio_name not in PORTFOLIO_HISTORY or not PORTFOLIO_HISTORY[portfolio_name]:
        buf = io.BytesIO()
        plt.figure(figsize=(2, 1))
        plt.axis("off")
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight", pad_inches=0)
        plt.close()
        buf.seek(0)
        return Response(content=buf.getvalue(), media_type="image/png")

    hist = PORTFOLIO_HISTORY[portfolio_name]
    times = [h["time"] for h in hist]
    values = [h["value"] for h in hist]

    plt.figure(figsize=(3, 1.5))
    plt.plot(times, values, color="#1976D2", linewidth=1.2)
    plt.fill_between(times, values, color="#BBDEFB")
    plt.xticks([])
    plt.yticks([])
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120)
    plt.close()
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")

