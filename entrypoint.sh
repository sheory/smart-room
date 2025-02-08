#!/bin/sh

echo "Waiting database..."
while ! nc -z db 5432; do
  sleep 1
done

echo "Database ready! apply migrations..."
alembic upgrade head

echo "Startins app..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
