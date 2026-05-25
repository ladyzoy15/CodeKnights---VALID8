#!/bin/sh
set -eu

: "${NEXUS_API_BASE_URL:=/__backend__}"
: "${NEXUS_API_TIMEOUT_MS:=15000}"

envsubst '${NEXUS_API_BASE_URL} ${NEXUS_API_TIMEOUT_MS}' \
  < /opt/nexus/runtime-config.js.template \
  > /usr/share/nginx/html/runtime-config.js
