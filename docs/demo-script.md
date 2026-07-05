# StratPilot Demo Script

## Positioning

StratPilot is not an auto-trading robot. It is a human-in-the-loop investment agent system:

`idea -> research -> structured strategy -> data -> factor score -> backtest -> risk veto -> portfolio -> simulated order -> ledger`

## Main Flow

1. Paste the AI infrastructure prompt.
2. Show the agent timeline: reading, checking news, searching data/tool sources, ranking factors, reviewing risk, writing the answer.
3. Show the strategy spec and selected template.
4. Show US + optional HK universes.
5. Show factor score table with price, fundamental, and event signals.
6. Show 3Y backtest chart, drawdown chart, Sharpe, max drawdown, benchmark comparison.
7. Show `通过 / 观察 / 拒绝`.
8. Confirm simulated orders and show the paper ledger.

## Judge Questions

- Why not direct auto trade? Because the agent handles research and orchestration, while the user confirms every simulated order.
- Why trust the LLM? You do not. LLM output is only a structured strategy draft. Deterministic Python code calculates signals, backtests, risk, and orders.
- What if data/API fails? The system falls back from yfinance/QVeris to local cache, then deterministic offline demo data.
- What is the moat? Strategy templates + risk veto + paper ledger + QVeris capability routing + model-readable audit trail.
