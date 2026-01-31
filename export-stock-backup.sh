#!/usr/bin/env bash
set -euo pipefail

# CONFIG
HOST_BACKUP_DIR="/srv/stock-table-backups"   # where container writes JSON
EXPORT_DIR="$HOME/stock-table-export"        # where you want to store exports

mkdir -p "$EXPORT_DIR"

# Find latest backup JSON
latest=$(ls -1t "$HOST_BACKUP_DIR"/backup-*.json 2>/dev/null | head -n 1 || true)
if [[ -z "$latest" ]]; then
  echo "No backup-*.json found in $HOST_BACKUP_DIR"
  exit 1
fi

ts=$(date +"%Y%m%d-%H%M%S")
dest="$EXPORT_DIR/backup-${ts}.json"

cp "$latest" "$dest"

echo "Exported $latest -> $dest"

