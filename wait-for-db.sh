#!/bin/sh
set -e

host="$1"
shift

echo "CMD is: $cmd"

echo "Waiting for Postgres at $host..."

export PGPASSWORD=$DB_PASSWORD

until psql -h "$host" -U "$DB_USER" -d "$DB_NAME" -c '\q'; do
  echo "Postgres is unavailable - sleeping 1 second..."
  sleep 1
done

echo "Postgres is up - executing server"
exec "$@"
