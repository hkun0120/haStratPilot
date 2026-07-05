#!/usr/bin/env bash
set -euo pipefail

SITE_NAME="stratpilot-ha"
DOMAIN="ha.clawhome.fun"
SOURCE_CONF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/ha.clawhome.fun.conf"
AVAILABLE_CONF="/etc/nginx/sites-available/${SITE_NAME}.conf"
ENABLED_CONF="/etc/nginx/sites-enabled/${SITE_NAME}.conf"

if [[ ! -f "${SOURCE_CONF}" ]]; then
  echo "Missing ${SOURCE_CONF}" >&2
  exit 1
fi

echo "Installing Nginx site for ${DOMAIN} only."
echo "This script does not modify clawhome.fun, stock.clawhome.fun, or the default site."

sudo cp "${SOURCE_CONF}" "${AVAILABLE_CONF}"
sudo ln -sf "${AVAILABLE_CONF}" "${ENABLED_CONF}"

echo "Checking that Nginx can see the ${DOMAIN} server block..."
if ! sudo nginx -T 2>/dev/null | grep -q "server_name ${DOMAIN}"; then
  echo "Nginx did not load ${DOMAIN}. Check include paths under /etc/nginx/nginx.conf." >&2
  exit 1
fi

sudo nginx -t
sudo systemctl reload nginx

echo "Enabled ${DOMAIN}. Next checks:"
echo "  curl -I http://${DOMAIN}"
echo "  curl -fsS http://127.0.0.1:3100 | head"
echo "  curl -fsS http://127.0.0.1:8100/health"
