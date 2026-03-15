#!/bin/sh

echo "🔄 Running database migrations..."

alembic upgrade head

if [ $? -eq 0 ]; then
  echo "✅ Migrations applied successfully!"
  exit 0
else
  echo "❌ Migration failed!"
  exit 1
fi