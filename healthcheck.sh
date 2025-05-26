#!/bin/sh

HOST="app-container"

PORT="8000"

HEALTHCHECK_PATH="/healthcheck"

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://${HOST}:${PORT}${HEALTHCHECK_PATH})


if [ "$HTTP_CODE" -eq 200 ]; then
  echo "Healthcheck successful: HTTP 200 OK"
  exit 0
else
  echo "Healthcheck failed: HTTP $HTTP_CODE"
  exit 1
fi