#!/bin/sh
set -euo pipefail

waitfor() {
    while ! nc -z $1 $2; do
        echo "Waiting for $1..."
        sleep 1
    done
}

if [ $# -eq 1 -a "${1:-}" = start ]; then
    # Wait for Postgres and Redis
    waitfor postgres 5432
    waitfor redis 6379

    set -- uwsgi --ini uwsgi.ini
fi

if [ $# -eq 1 -a "${1:-}" = watcher ]; then
    set -- watch.sh $0 start
fi

if [ $# -eq 1 -a "${1:-}" = reload ]; then
    set -- touch /reload
fi

exec "$@"
