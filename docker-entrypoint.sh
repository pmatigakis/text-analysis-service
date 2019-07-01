#!/bin/bash
set -e

if [ "$1" = "run" ]; then
    cd /app/configuration
    exec tas-cli server
fi

exec "$@"