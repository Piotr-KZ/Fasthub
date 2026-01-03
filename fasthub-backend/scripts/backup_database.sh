#!/bin/bash
#
# Manual Database Backup Script
# Creates a PostgreSQL dump and optionally uploads to S3/cloud storage
#
# Usage:
#   ./backup_database.sh [output_dir]
#
# Environment variables required:
#   DATABASE_URL - PostgreSQL connection string
#
# Optional environment variables:
#   AWS_ACCESS_KEY_ID - For S3 upload
#   AWS_SECRET_ACCESS_KEY - For S3 upload
#   S3_BACKUP_BUCKET - S3 bucket name for backups
#

set -e  # Exit on error

# Configuration
OUTPUT_DIR="${1:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="fasthub_backup_${TIMESTAMP}.sql.gz"
BACKUP_PATH="${OUTPUT_DIR}/${BACKUP_FILE}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}ERROR: DATABASE_URL environment variable is not set${NC}"
    echo "Usage: DATABASE_URL=<connection_string> ./backup_database.sh [output_dir]"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo -e "${YELLOW}Starting database backup...${NC}"
echo "Output directory: $OUTPUT_DIR"
echo "Backup file: $BACKUP_FILE"

# Extract connection details from DATABASE_URL
# Format: postgresql://user:password@host:port/database
DB_URL_REGEX="postgresql://([^:]+):([^@]+)@([^:]+):([0-9]+)/(.+)"
if [[ $DATABASE_URL =~ $DB_URL_REGEX ]]; then
    DB_USER="${BASH_REMATCH[1]}"
    DB_PASSWORD="${BASH_REMATCH[2]}"
    DB_HOST="${BASH_REMATCH[3]}"
    DB_PORT="${BASH_REMATCH[4]}"
    DB_NAME="${BASH_REMATCH[5]}"
else
    echo -e "${RED}ERROR: Invalid DATABASE_URL format${NC}"
    echo "Expected format: postgresql://user:password@host:port/database"
    exit 1
fi

# Create backup using pg_dump
echo -e "${YELLOW}Creating database dump...${NC}"
PGPASSWORD="$DB_PASSWORD" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --no-owner \
    --no-acl \
    --clean \
    --if-exists \
    | gzip > "$BACKUP_PATH"

# Check if backup was successful
if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_PATH" | cut -f1)
    echo -e "${GREEN}✓ Backup created successfully!${NC}"
    echo "  File: $BACKUP_PATH"
    echo "  Size: $BACKUP_SIZE"
else
    echo -e "${RED}✗ Backup failed!${NC}"
    exit 1
fi

# Upload to S3 if configured
if [ -n "$S3_BACKUP_BUCKET" ] && [ -n "$AWS_ACCESS_KEY_ID" ]; then
    echo -e "${YELLOW}Uploading to S3...${NC}"
    
    if command -v aws &> /dev/null; then
        aws s3 cp "$BACKUP_PATH" "s3://${S3_BACKUP_BUCKET}/backups/${BACKUP_FILE}"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Uploaded to S3: s3://${S3_BACKUP_BUCKET}/backups/${BACKUP_FILE}${NC}"
        else
            echo -e "${RED}✗ S3 upload failed${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ AWS CLI not installed, skipping S3 upload${NC}"
    fi
fi

# Cleanup old backups (keep last 7 days)
echo -e "${YELLOW}Cleaning up old backups...${NC}"
find "$OUTPUT_DIR" -name "fasthub_backup_*.sql.gz" -type f -mtime +7 -delete
echo -e "${GREEN}✓ Cleanup complete${NC}"

echo -e "${GREEN}=== Backup completed successfully ===${NC}"
echo ""
echo "To restore this backup, run:"
echo "  gunzip -c $BACKUP_PATH | psql \$DATABASE_URL"
