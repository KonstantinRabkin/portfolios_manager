# routers/ui_constants.py

TAG_LABELS = [
    "Hold",
    "Buy",
    "Buy order",
    "Sell",
    "Sell order",
    "Increase",
    "Reduce",
    "Pause",
    "Rebalance",
    "Rotate",
    "De-risk",
    "Review Thesis",
]

MAX_TAG_INDEX = len(TAG_LABELS) - 1

STYLE_BLOCK = """
    <style>
        html, body { height: 100%; margin: 0; padding: 0; }
        body {
            font-family: Arial, sans-serif;
            background: #e0e0e0;
            display: flex;
            flex-direction: column;
        }
        .page-root {
            flex: 1 1 auto;
            display: flex;
            flex-direction: column;
            padding: 12px 20px 20px 20px;
            box-sizing: border-box;
            gap: 12px;
        }
        .top-header { flex: 0 0 auto; }
        .updated { color: #666; font-size: 12px; margin-top: 4px; }
        .top-layout {
            display: flex;
            gap: 16px;
            align-items: flex-start;
        }
        .top-main {
            flex: 3 1 0;
            min-width: 0;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .sidebar {
            flex: 0 0 280px;
            max-width: 280px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .bottom-layout {
            flex: 1 1 auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .panel {
            background: white;
            padding: 10px 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }
        table {
            border-collapse: collapse;
            width: 100%;
            background: white;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin: 8px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 6px 8px;
            text-align: left;
            font-size: 13px;
            vertical-align: middle;
        }
        th {
            background: #4CAF50;
            color: white;
            font-weight: bold;
            white-space: nowrap;
        }
        th a { color: #FFF; text-decoration: none; }
        th a:hover { text-decoration: underline; }
        a {
            color: #2196F3;
            text-decoration: none;
            font-weight: bold;
        }
        a:hover { text-decoration: underline; }
        h1 { color: #333; margin: 0 0 4px 0; }
        h2 { color: #333; margin: 12px 0 6px 0; font-size: 17px; }
        h3 { color: #333; margin: 8px 0 4px 0; font-size: 14px; }
        .controls {
            background: white;
            padding: 8px 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            margin-bottom: 10px;
            font-size: 12px;
        }
        .controls-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            margin-bottom: 6px;
        }
        .controls-main {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
        }
        .controls-main form { margin: 0; }
        .controls-main label {
            font-size: 12px;
            margin-right: 4px;
        }
        .controls-extra {
            margin-top: 6px;
            padding-top: 6px;
            border-top: 1px dashed #ccc;
            display: none;
        }
        .controls-extra form {
            margin: 4px 4px 0 0;
            display: inline-block;
        }
        .controls-toggle-btn {
            padding: 3px 8px;
            font-size: 11px;
        }
        input[type="text"], input[type="number"] {
            padding: 4px;
            font-size: 12px;
        }
        input[type="submit"], button {
            padding: 4px 8px;
            font-size: 12px;
            margin-left: 3px;
        }
        select {
            padding: 3px;
            font-size: 12px;
        }
        .tickers-list {
            font-size: 12px;
            color: #444;
            margin-top: 4px;
        }
        .total-pl {
            font-weight: bold;
            margin-top: 6px;
            font-size: 13px;
        }
        .error-box {
            background: #ffe6e6;
            color: #b30000;
            border: 1px solid #ff9999;
            padding: 6px 10px;
            border-radius: 3px;
            margin-bottom: 8px;
            font-size: 12px;
        }
        .summary-wrapper h3 {
            margin-top: 0;
            font-size: 13px;
        }
        .summary-symbol {
            font-weight: bold;
            background: #fafafa;
        }
        .summary-header {
            background: #1976D2;
            color: white;
            font-size: 12px;
            text-align: center;
        }
        .summary-cell {
            white-space: nowrap;
            font-size: 11px;
            color: #222;
        }
        .cell-part {
            margin-right: 2px;
        }
        .cell-empty {
            color: #bbb;
        }
        .trade-cell {
            white-space: nowrap;
        }
        .trade-form {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            white-space: nowrap;
        }
        .trade-input {
            width: 70px;
            font-size: 11px;
        }
        .trade-input.price {
            width: 80px;
        }
        .trade-input.note {
            width: 120px;
        }
        .sidebar-card-wrapper {
            background: white;
            padding: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            font-size: 12px;
        }
        .sidebar-title {
            font-weight: bold;
            font-size: 13px;
            margin-bottom: 6px;
        }
        .pf-card {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 6px 8px;
            margin-bottom: 6px;
            background: #fafafa;
        }
        .pf-title {
            font-weight: bold;
            margin-bottom: 4px;
        }
        .pf-line {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
        }
        .pf-line span:last-child {
            font-weight: bold;
        }
        .pf-line .pos { color: #2e7d32; }
        .pf-line .neg { color: #c62828; }
        .charts-wrapper {
            background: white;
            padding: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            margin-top: 0;
            font-size: 12px;
        }
        .charts-title {
            font-weight: bold;
            font-size: 13px;
            margin-bottom: 4px;
        }
        .chart-placeholder {
            margin-bottom: 8px;
        }
        .chart-title {
            font-size: 12px;
            margin-bottom: 2px;
        }
        .chart-box {
            border: 1px solid #ccc;
            border-radius: 4px;
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #fafafa;
            overflow: hidden;
        }
        .filter-row {
            font-size: 12px;
            color: #444;
        }
        #ticker-filter {
            width: 140px;
            font-size: 12px;
            padding: 3px;
        }
        #summary-filter, #history-filter, #global-history-filter {
            width: 220px;
            font-size: 12px;
            padding: 3px;
            margin-top: 4px;
        }
        .backup-btn {
            margin-top: 4px;
            display: inline-block;
        }
        .summary-tag-select {
            font-size: 10px;
            padding: 1px 2px;
        }
        .summary-tag-form {
            display: inline-block;
            margin-left: 2px;
        }
        .summary-tag-filter-row td {
            background: #e3f2fd;
            font-size: 11px;
            padding: 4px 6px;
        }
        .summary-tag-filter {
            font-size: 11px;
            padding: 1px 2px;
        }
    </style>
"""

