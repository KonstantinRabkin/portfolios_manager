#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /path/to/backup-YYYYMMDD-HHMMSS.json"
  exit 1
fi

BACKUP_FILE="$1"

if [[ ! -f "$BACKUP_FILE" ]]; then
  echo "Backup file not found: $BACKUP_FILE"
  exit 1
fi

NEW_CONTAINER_NAME="stock-app-new"
HOST_BACKUP_DIR_NEW="/srv/stock-table-backups-new"
IMAGE_NAME="stock-table:latest"
NEW_PORT="8081"

mkdir -p "$HOST_BACKUP_DIR_NEW"

echo "Copying backup into new host backup dir..."
cp "$BACKUP_FILE" "$HOST_BACKUP_DIR_NEW/backup-restore.json"

echo "Stopping/removing old container with same name (if any)..."
docker stop "$NEW_CONTAINER_NAME" >/dev/null 2>&1 || true
docker rm "$NEW_CONTAINER_NAME" >/dev/null 2>&1 || true

echo "Starting new container..."
docker run -d \
  --name "$NEW_CONTAINER_NAME" \
  -p "${NEW_PORT}:8000" \
  -v "$HOST_BACKUP_DIR_NEW":/app/backups \
  "$IMAGE_NAME"

echo "Waiting a few seconds for app to start..."
sleep 5

echo "Restoring JSON into new container via /backup/restore..."
curl -s -X POST \
  -F "file=@${HOST_BACKUP_DIR_NEW}/backup-restore.json" \
  "http://localhost:${NEW_PORT}/backup/restore" >/dev/null

echo "Restore completed. New app available at: http://localhost:${NEW_PORT}"

