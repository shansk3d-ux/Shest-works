#!/bin/bash
# Restores a database dump and (optionally) a media archive produced by
# backup.sh. Destructive: overwrites the current database and media files.
# See README.md -> "Бэкапы" for details.
set -euo pipefail

cd "$(dirname "$0")/.."

COMPOSE=(docker compose -f docker-compose.prod.yml)

DB_DUMP="${1:-}"
MEDIA_ARCHIVE="${2:-}"

if [ -z "$DB_DUMP" ]; then
    echo "Usage: $0 <db-dump.sql.gz> [media-archive.tar.gz]" >&2
    exit 1
fi

POSTGRES_USER=$(grep -E '^POSTGRES_USER=' .env | cut -d= -f2-)
POSTGRES_DB=$(grep -E '^POSTGRES_DB=' .env | cut -d= -f2-)

echo "This will OVERWRITE the current database ($POSTGRES_DB)$( [ -n "$MEDIA_ARCHIVE" ] && echo " and media files")."
read -r -p "Type 'yes' to continue: " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

echo "Stopping web to avoid writes during restore..."
"${COMPOSE[@]}" stop web

echo "Restoring database from $DB_DUMP..."
gunzip -c "$DB_DUMP" | "${COMPOSE[@]}" exec -T db psql -U "$POSTGRES_USER" "$POSTGRES_DB"

if [ -n "$MEDIA_ARCHIVE" ]; then
    echo "Restoring media from $MEDIA_ARCHIVE..."
    "${COMPOSE[@]}" exec -T web sh -c "rm -rf /app/media/* && tar xzf - -C /app" < "$MEDIA_ARCHIVE"
fi

echo "Starting web again..."
"${COMPOSE[@]}" start web

echo "Restore complete."
