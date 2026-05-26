#!/bin/sh
set -eu

: "${AURA_API_BASE_URL:=/__backend__}"
: "${AURA_API_TIMEOUT_MS:=15000}"
: "${AURA_ASSISTANT_BASE_URL:=/__assistant__}"
: "${GOOGLE_LOGIN_ENABLED:=false}"
: "${GOOGLE_WEB_CLIENT_ID:=}"

envsubst '${AURA_API_BASE_URL} ${AURA_API_TIMEOUT_MS} ${AURA_ASSISTANT_BASE_URL} ${GOOGLE_LOGIN_ENABLED} ${GOOGLE_WEB_CLIENT_ID}' \
  < /opt/aura/runtime-config.js.template \
  > /usr/share/nginx/html/runtime-config.js
