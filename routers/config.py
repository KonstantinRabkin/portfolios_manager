from typing import Optional, List

from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from backup_utils import PORTFOLIOS
from config.summary_order import (
    get_portfolio_summary_order,
    set_portfolio_summary_order,
)

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/summary-order", response_class=HTMLResponse)
async def show_summary_order():
    names = list(PORTFOLIOS.keys())
    current_order = get_portfolio_summary_order()

    # Render a simple form: user enters comma-separated portfolio names
    textarea_value = ", ".join(current_order)

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Configure summary order</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f4f4f4;
            margin: 0;
            padding: 20px;
        }}
        .panel {{
            background: white;
            padding: 16px 20px;
            max-width: 600px;
            margin: 0 auto;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }}
        h1 {{
            margin-top: 0;
        }}
        textarea {{
            width: 100%;
            height: 80px;
            font-size: 13px;
            padding: 6px;
            box-sizing: border-box;
        }}
        .hint {{
            font-size: 12px;
            color: #555;
            margin-top: 4px;
        }}
        .current-list {{
            font-size: 12px;
            margin-top: 8px;
        }}
        input[type="submit"] {{
            margin-top: 10px;
            padding: 6px 10px;
            font-size: 13px;
        }}
        a {{
            font-size: 12px;
        }}
    </style>
</head>
<body>
<div class="panel">
    <h1>Portfolios summary order</h1>
    <form method="post" action="/config/summary-order">
        <label for="order">Desired order (comma-separated portfolio names):</label><br>
        <textarea id="order" name="order">{textarea_value}</textarea>
        <div class="hint">
            Example: <code>Watch list, RRSP, TFSA, Cash</code><br>
            Any missing portfolios will be appended automatically at the end.
        </div>
        <div class="current-list">
            <strong>Existing portfolios:</strong> {", ".join(names) if names else "(none)"}
        </div>
        <input type="submit" value="Save order">
    </form>
    <p><a href="/">Back to main page</a></p>
</div>
</body>
</html>
"""
    return HTMLResponse(html)


@router.post("/summary-order")
async def update_summary_order(order: Optional[str] = Form(None)):
    if order is None:
        # Just ignore and go back
        return RedirectResponse(url="/config/summary-order", status_code=303)

    # Split by comma, trim spaces
    tokens: List[str] = [t.strip() for t in order.split(",") if t.strip()]

    set_portfolio_summary_order(tokens)

    # Redirect back to config page
    return RedirectResponse(url="/config/summary-order", status_code=303)

