# StratPilot 策略驾驶舱

StratPilot = Strategy + Pilot。它不是自动交易机器人，而是一个 human-in-the-loop 的港美股策略工作台：把用户的策略想法转成结构化策略、在线行情、因子打分、vectorbt 回测、回撤分析、风控结论和模拟订单。

LLM 负责解析和解释；股票组合选择、回测、回撤、风控和模拟订单都由确定性 Python 代码执行。

## Quick Start

```bash
npm install
npm run install:all
npm run dev
```

Open:

- Web: http://localhost:3000
- Workbench: http://localhost:3000/workbench
- Strategy Center: http://localhost:3000/strategies
- Settings: http://localhost:3000/settings
- API: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Environment

Create `.env`, edit `.env.example`, or export variables before running the API. The API reads `.env`, `.env.local`, `.env.example`, and `.env copy.example` in that order so local demos can run even when a separate `.env` file is unavailable.

```bash
VOLC_ARK_API_KEY=
VOLC_ARK_MODEL=doubao-seed-2-1-pro-260628
VOLC_ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
QVERIS_API_KEY=
QVERIS_BASE_URL=https://qveris.ai/api/v1
```

Do not commit real keys. `.env*` is ignored by git except `.env.example` and `.env.production.example`, which must keep placeholder values only.

## Data And Backtest

- Price data is online-first when cache is missing, then cached under `data/cache`.
- Backtests run through `vectorbt==0.28.2` using target-percent orders, shared cash, fees, slippage, and automatic call sequencing.
- Settings lets you configure the data source portfolio for price prediction, fundamentals, event/NLP, macro, and volatility tasks.

## Volc Ark Usage Troubleshooting

If Volc Engine / Ark console shows no API usage:

1. Confirm the active env or Settings page contains the Ark API key.
2. Restart the API server after editing env values.
3. Run a request that reaches `/api/agent/run`; Ark is used for strategy parsing.
4. If the key is absent or the Ark request fails, StratPilot falls back to local rule parsing, so no Volc usage will appear.
5. Keep `VOLC_ARK_MODEL=doubao-seed-2-1-pro-260628` aligned with the model enabled in your Ark account.

## QVeris Usage Troubleshooting

QVeris is used during `/api/agent/run` for the discovery step.

1. Confirm the active env or Settings page contains the QVeris API key.
2. Restart the API server after editing env values.
3. Run an agent request. The response field `qveris_status.discovery` shows whether discovery was attempted, which REST endpoint was used, and how many results came back.
4. If the key is absent, StratPilot skips QVeris discovery and uses deterministic fallback context.

## GitHub

This folder is currently ready to become a git repository:

```bash
git init
git add .
git commit -m "Initial StratPilot hackathon build"
git branch -M main
git remote add origin git@github.com:<your-org-or-user>/stratpilot.git
git push -u origin main
```

Before pushing, verify no real secrets exist in `.env.example`, `.env.production.example`, docs, or screenshots.

## Singapore Server Deployment

Assume an Ubuntu server with Docker, Docker Compose, Nginx, and Certbot installed. Nginx owns public `80/443`; Docker only binds local ports for the web and API services.

1. Point a DNS `A` record to the server public IP. The current demo domain is `ha.clawhome.fun`.
2. Copy the project to the server or `git clone` it.
3. Create a server-only `.env` from the production template:

```bash
cp .env.production.example .env
```

4. Edit `.env` with the real API keys. For this deployment, keep `CORS_ORIGINS=https://ha.clawhome.fun`, `WEB_PORT=3000`, and `API_PORT=8000`.
5. Start the stack:

```bash
docker compose up -d --build
```

6. Install the Nginx reverse proxy for `ha.clawhome.fun` only:

```bash
bash deploy/nginx/enable-ha-site.sh
```

7. Issue HTTPS certificate:

```bash
sudo certbot --nginx -d ha.clawhome.fun --redirect
sudo nginx -t
sudo systemctl reload nginx
```

Nginx routes `/` to `127.0.0.1:3000`, and `/api/*`, `/health`, `/docs`, `/redoc`, `/openapi.json` to `127.0.0.1:8000`. After DNS resolves to the Singapore server, the app should be available at `https://ha.clawhome.fun`.

Do not edit or disable existing Nginx sites for `clawhome.fun` or `stock.clawhome.fun`; this deployment is scoped only to `server_name ha.clawhome.fun`.

## Demo Inputs

```text
回测「ETF 动量轮动」预制策略，区间 2023-07-04 至 2026-07-04，初始资金 100000 美元，最大回撤阈值 5%，查看收益、最大回撤和风控结果。
```

```text
我想做一个 AI 芯片和云计算相关的美股组合，希望跑赢 QQQ，但最大回撤不要超过 15%。
```
