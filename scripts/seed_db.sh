#!/bin/bash
set -e

# Verify required variables are set
REQUIRED_VARS=(
  DB_HOST DB_PORT DB_NAME DB_USERNAME DB_PASSWORD
  SOURCE_DB_HOST SOURCE_DB_PORT SOURCE_DB_NAME SOURCE_DB_USERNAME SOURCE_DB_PASSWORD
)

for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var}" ]; then
    echo "❌ Environment variable $var is not set."
    exit 1
  fi
done

# Confirm before proceeding
DB="$DB_HOST:$DB_PORT/$DB_NAME"
SOURCE_DB="$SOURCE_DB_HOST:$SOURCE_DB_PORT/$SOURCE_DB_NAME"
read -p "⚠️ This will erase all data in $DB and replace it with data from $SOURCE_DB. Continue? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "❌ Aborted."
  exit 1
fi

# Clear existing data in the target database first
echo "🧹 Truncating all tables in $DB_NAME..."
PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USERNAME" -d "$DB_NAME" -Atc \
"SELECT 'TRUNCATE TABLE ' || tablename || ' CASCADE;'
 FROM pg_tables
 WHERE schemaname = 'public';" | \
PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USERNAME" -d "$DB_NAME"

# Dump data-only from source and import into target
echo "📥 Copying data from $SOURCE_DB_NAME to $DB_NAME..."
PGPASSWORD=$SOURCE_DB_PASSWORD pg_dump \
  -h "$SOURCE_DB_HOST" -U "$SOURCE_DB_USERNAME" "$SOURCE_DB_NAME" | \
PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USERNAME" "$DB_NAME"

echo "✅ Data transfer complete!"
