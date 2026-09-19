#!/bin/sh
set -e

if [ -z "${APP_BUILT_AT:-}" ]; then
  if [ -f /app/.built_at ]; then
    export APP_BUILT_AT="$(cat /app/.built_at)"
  else
    export APP_BUILT_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  fi
fi

exec "$@"
