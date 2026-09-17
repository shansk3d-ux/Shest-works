#!/bin/bash
# Dumps the database and archives media/, keeping the last RETENTION_DAYS days.
# Intended to run daily via host cron against a running docker-compose.prod.yml
# stack. See README.md -> "Бэкапы" for the restore procedure.
set -euo pipefail

cd "$(dirname "$0")/.."

COMPOSE=(docker compose -f docker-compose.prod.yml)
BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

POSTGRES_USER=$(grep -E '^POSTGRES_USER=' .env | cut -d= -f2-)
POSTGRES_DB=$(grep -E '^POSTGRES_DB=' .env | cut -d= -f2-)

mkdir -p "$BACKUP_DIR"

echo "Dumping database ($POSTGRES_DB)..."
"${COMPOSE[@]}" exec -T db pg_dump -U "$POSTGRES_USER" --clean --if-exists "$POSTGRES_DB" \
    | gzip > "$BACKUP_DIR/db-$TIMESTAMP.sql.gz"

echo "Archiving media/..."
"${COMPOSE[@]}" exec -T web tar czf - -C /app media > "$BACKUP_DIR/media-$TIMESTAMP.tar.gz"

echo "Removing backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -type f -name 'db-*.sql.gz' -mtime "+$RETENTION_DAYS" -delete
find "$BACKUP_DIR" -type f -name 'media-*.tar.gz' -mtime "+$RETENTION_DAYS" -delete

echo "Done: $BACKUP_DIR/db-$TIMESTAMP.sql.gz, $BACKUP_DIR/media-$TIMESTAMP.tar.gz"
