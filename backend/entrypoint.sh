#!/bin/sh
set -e

echo "=== AAS PAAS Backend Container Startup ==="

# Run database migrations
if [ "$RUN_MIGRATIONS" != "false" ]; then
    echo "Applying database schema migrations (alembic upgrade head)..."
    alembic upgrade head || echo "Migration warning: check database connection"
fi

# Run pilot seed data if requested
if [ "$SEED_ON_STARTUP" = "true" ]; then
    echo "Running pilot campus database seeding..."
    python -m app.core.seed || echo "Seeding completed or already present"
fi

echo "Starting server process..."
exec "$@"
