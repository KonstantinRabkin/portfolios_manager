#!/bin/bash
set -euo pipefail

SRC="/home/stock-table"
DEST="/home/stock-table_bk_$(date +%Y%m%d_%H%M%S)"

# Create backup with timestamp
cp -rp "$SRC" "$DEST"
