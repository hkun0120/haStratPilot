# Nginx Reverse Proxy

StratPilot runs two local app ports:

- Web: `127.0.0.1:3100`
- API: `127.0.0.1:8100`
- HTTPS SNI backend: `127.0.0.1:9445`

Nginx owns public `80/443` and routes:

- public `ha.clawhome.fun:443` -> Nginx stream SNI -> `127.0.0.1:9445`
- `/` -> web
- `/api/*` -> API
- `/health`, `/docs`, `/redoc`, `/openapi.json` -> API

These configs are intentionally scoped to `server_name ha.clawhome.fun;`. Do not remove or edit existing Nginx sites for `clawhome.fun` or `stock.clawhome.fun`.

## Install

```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
```

## Deploy App

```bash
git clone https://github.com/hkun0120/haStratPilot.git
cd haStratPilot
cp .env.production.example .env
# edit .env and add real API keys
docker compose up -d --build
```

## Enable Nginx Site

```bash
bash deploy/nginx/enable-ha-site.sh
```

## Enable HTTPS / SNI

Issue a certificate for this exact subdomain without asking Certbot to rewrite other site configs:

```bash
sudo certbot certonly --webroot -w /var/www/letsencrypt -d ha.clawhome.fun --cert-name ha.clawhome.fun
bash deploy/nginx/enable-ha-sni.sh
```

The SNI config uses:

```nginx
listen 127.0.0.1:9445 ssl http2;
server_name ha.clawhome.fun;
ssl_certificate /etc/letsencrypt/live/ha.clawhome.fun/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/ha.clawhome.fun/privkey.pem;
```

If `http://ha.clawhome.fun/` still shows the Ubuntu default page, do not delete unrelated sites. Check whether the `ha.clawhome.fun` server block is loaded:

```bash
sudo nginx -T | grep -n "server_name ha.clawhome.fun"
sudo ls -l /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Then verify that the local app ports are up on the server:

```bash
docker compose ps
curl -I http://127.0.0.1:3100
curl -fsS http://127.0.0.1:8100/health
```

Verify the HTTPS/SNI certificate:

```bash
curl -I https://ha.clawhome.fun/
openssl s_client -connect ha.clawhome.fun:443 -servername ha.clawhome.fun </dev/null 2>/dev/null | openssl x509 -noout -subject -issuer
```

If the default page still appears after the site is enabled, check for duplicate `ha.clawhome.fun` server blocks or a missed reload. An exact `server_name ha.clawhome.fun` should win over the default site when loaded correctly.

```bash
sudo nginx -T | grep -n -B 2 -A 4 "ha.clawhome.fun"
sudo nginx -T | grep -n "ha.clawhome.fun 127.0.0.1:9445"
curl -I -H "Host: ha.clawhome.fun" http://127.0.0.1
sudo nginx -t
sudo systemctl reload nginx
```
