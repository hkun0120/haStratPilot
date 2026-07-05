import asyncio

from alphaflow.clients.qveris import QVerisClient
from alphaflow.clients.volc import VolcArkClient
from alphaflow.core.config import get_settings
from alphaflow.core.models import AgentRunRequest
from alphaflow.services.agent import run_agent
from alphaflow.storage.config_store import read_runtime_config


async def main() -> None:
    settings = get_settings()
    request = AgentRunRequest(
        query="我想做一个 AI 芯片和云计算相关的美股组合，希望跑赢 QQQ，但最大回撤不要超过 15%。",
        strategy_id="ai_infra_momentum",
        initial_cash=100000,
        max_drawdown=0.15,
    )
    config = read_runtime_config(settings.runtime_config_path, settings)
    volc = VolcArkClient(config["volc_ark"]["api_key"], config["volc_ark"]["base_url"], config["volc_ark"]["model"])
    qveris = QVerisClient(config["qveris"]["api_key"], config["qveris"]["base_url"])
    response = await run_agent(request, settings.data_cache_dir, volc, qveris, config["data_sources"])
    print(
        {
            "run_id": response.run_id,
            "decision": response.risk.decision,
            "data_source": response.data_source,
            "templates": len(response.templates),
            "rankings": len(response.factor_rankings),
            "orders": len(response.orders),
            "total_return": response.metrics.total_return,
            "max_drawdown": response.metrics.max_drawdown,
            "sharpe": response.metrics.sharpe_ratio,
        }
    )


if __name__ == "__main__":
    asyncio.run(main())
