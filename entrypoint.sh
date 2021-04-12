#!/usr/bin/env sh

set -e

trap "exit 0" 1 2 3 15


case $1 in
    "runserver")
    echo "Wait database"
    wait-for-it -t 30 "$DATABASE_HOST:$DATABASE_PORT"
    echo "Run server"
    uvicorn main:app --port 80 --host 0.0.0.0
    ;;
    *)
    exec "$@"
    ;;
esac
