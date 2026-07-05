# Nginx Reverse Proxy

StratPilot runs two local Docker ports:

- Web: `127.0.0.1:3000`
- API: `127.0.0.1:8000`

Nginx owns public `80/443` and routes:

- `/` -> web
- `/api/*` -> API
- `/health`, `/docs`, `/redoc`, `/openapi.json` -> API

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
sudo cp deploy/nginx/ha.clawhome.fun.conf /etc/nginx/sites-available/stratpilot.conf
sudo ln -sf /etc/nginx/sites-available/stratpilot.conf /etc/nginx/sites-enabled/stratpilot.conf
sudo nginx -t
sudo systemctl reload nginx
```

## Enable HTTPS

```bash
sudo certbot --nginx -d ha.clawhome.fun --redirect
sudo nginx -t
sudo systemctl reload nginx
```

If the domain still shows the Ubuntu default page or a mismatched certificate, disable the conflicting default site and rerun Certbot:

```bash
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d ha.clawhome.fun --redirect
```
