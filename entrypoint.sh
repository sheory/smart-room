#!/bin/sh
set -e

export $(grep -v '^#' .env | xargs)

echo "Waiting for the database to be ready..."
while ! nc -z db 5432; do
  sleep 1
done

echo "Database is up. Checking for migrations..."

# Check if the migration folder is initialized or if we need to apply migrations
if alembic current | grep -q "No rows"; then
  echo "Applying migrations..."
  alembic upgrade head
else
  echo "Migrations are already applied."
fi

echo "Starting the app..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
