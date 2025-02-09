#!/bin/sh

echo "Waiting for the database to be ready..."
while ! nc -z db 5432; do
  sleep 1
done

echo "Database is up. Applying migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
  echo "Migrations applied successfully."
else
  echo "Failed to apply migrations."
  exit 1
fi

echo "Starting the app..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload