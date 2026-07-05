# Nginx Reverse Proxy

StratPilot runs two local Docker ports:

- Web: `127.0.0.1:3000`
- API: `127.0.0.1:8000`

Nginx owns public `80/443` and routes:

- `/` -> web
- `/api/*` -> API
- `/health`, `/docs`, `/redoc`, `/openapi.json` -> API

This config is intentionally scoped to `server_name ha.clawhome.fun;`. Do not remove or edit existing Nginx sites for `clawhome.fun` or `stock.clawhome.fun`.

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

## Enable HTTPS

```bash
sudo certbot --nginx -d ha.clawhome.fun --redirect
sudo nginx -t
sudo systemctl reload nginx
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
curl -I http://127.0.0.1:3000
curl -fsS http://127.0.0.1:8000/health
```

If the default page still appears after the site is enabled, check for duplicate `ha.clawhome.fun` server blocks or a missed reload. An exact `server_name ha.clawhome.fun` should win over the default site when loaded correctly.

```bash
sudo nginx -T | grep -n -B 2 -A 4 "ha.clawhome.fun"
curl -I -H "Host: ha.clawhome.fun" http://127.0.0.1
sudo nginx -t
sudo systemctl reload nginx
```
