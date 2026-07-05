#!/usr/bin/env bash
set -euo pipefail

SITE_NAME="stratpilot-ha"
DOMAIN="ha.clawhome.fun"
SOURCE_CONF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/ha.clawhome.fun.sni.conf"
AVAILABLE_CONF="/etc/nginx/sites-available/${SITE_NAME}.conf"
ENABLED_CONF="/etc/nginx/sites-enabled/${SITE_NAME}.conf"
CERT_DIR="/etc/letsencrypt/live/${DOMAIN}"

if [[ ! -f "${SOURCE_CONF}" ]]; then
  echo "Missing ${SOURCE_CONF}" >&2
  exit 1
fi

if [[ ! -f "${CERT_DIR}/fullchain.pem" || ! -f "${CERT_DIR}/privkey.pem" ]]; then
  echo "Missing certificate for ${DOMAIN}." >&2
  echo "Run first: sudo certbot certonly --nginx -d ${DOMAIN}" >&2
  exit 1
fi

echo "Installing HTTPS/SNI Nginx site for ${DOMAIN} only."
echo "This script does not modify clawhome.fun, stock.clawhome.fun, or any other server block."

sudo cp "${SOURCE_CONF}" "${AVAILABLE_CONF}"
sudo ln -sf "${AVAILABLE_CONF}" "${ENABLED_CONF}"

echo "Checking that Nginx can see the ${DOMAIN} HTTPS server block..."
if ! sudo nginx -T 2>/dev/null | grep -q "server_name ${DOMAIN}"; then
  echo "Nginx did not load ${DOMAIN}. Check include paths under /etc/nginx/nginx.conf." >&2
  exit 1
fi

sudo nginx -t
sudo systemctl reload nginx

echo "Enabled HTTPS/SNI for ${DOMAIN}. Next checks:"
echo "  curl -I https://${DOMAIN}"
echo "  openssl s_client -connect ${DOMAIN}:443 -servername ${DOMAIN} </dev/null 2>/dev/null | openssl x509 -noout -subject -issuer"
