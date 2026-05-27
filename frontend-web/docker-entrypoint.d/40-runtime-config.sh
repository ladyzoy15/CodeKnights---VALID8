#!/bin/sh
set -eu

: "${NEXUS_API_BASE_URL:=/__backend__}"
: "${NEXUS_API_TIMEOUT_MS:=15000}"
: "${GOOGLE_WEB_CLIENT_ID:=${VITE_GOOGLE_WEB_CLIENT_ID:-}}"

envsubst '${NEXUS_API_BASE_URL} ${NEXUS_API_TIMEOUT_MS} ${GOOGLE_WEB_CLIENT_ID}' \
  < /opt/nexus/runtime-config.js.template \
  > /usr/share/nginx/html/runtime-config.js
