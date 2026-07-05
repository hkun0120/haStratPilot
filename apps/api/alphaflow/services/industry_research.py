from __future__ import annotations

from alphaflow.core.models import IndustryChainResponse, IndustryCompany, IndustryLayer


VALUATION_COLUMNS = [
    "category",
    "market_cap_usd_bn",
    "pe",
    "ps",
    "peg",
    "revenue_growth",
    "gross_margin",
    "research_priority",
]

VALUATION_COLUMNS_ZH = ["分类", "市值", "PE", "PS", "PEG", "收入增长", "毛利率", "研究优先级"]

LAYER_ZH = {
    "compute": {
        "name": "AI 计算芯片",
        "why": "训练和推理需求会先转化为加速器、自研芯片和内存带宽需求。",
        "metrics": ["数据中心收入", "加速器订单", "HBM 搭载率", "毛利率"],
    },
    "foundry-packaging": {
        "name": "晶圆代工与先进封装",
        "why": "先进制程、CoWoS 类封装和良率决定 AI 芯片供给能否扩张。",
        "metrics": ["晶圆产能", "先进封装产能", "资本开支", "交付周期"],
    },
    "memory-networking": {
        "name": "HBM、网络与光连接",
        "why": "AI 集群受带宽、时延和内存容量约束，不只是算力约束。",
        "metrics": ["HBM 收入占比", "交换芯片份额", "光模块需求", "库存"],
    },
    "cloud-platforms": {
        "name": "云平台与 AI 应用",
        "why": "云平台决定 AI 算力如何商业化，也决定资本开支被吸收的速度。",
        "metrics": ["AI capex", "云收入增长", "利用率", "自由现金流"],
    },
    "power-cooling": {
        "name": "数据中心电力与散热",
        "why": "并网、电力密度和电力设备正在成为数据中心落地的关键约束。",
        "metrics": ["电力订单", "液冷渗透率", "并网时间", "订单"],
    },
    "actuators": {
        "name": "执行器、减速器与运动控制",
        "why": "成本、可靠性、扭矩密度和寿命是人形机器人与工业机器人的核心约束。",
        "metrics": ["单位成本", "认证周期", "精度", "良率"],
    },
    "sensors-vision": {
        "name": "传感器、视觉与边缘 AI",
        "why": "机器人需要感知与本地推理，才能在复杂环境中安全运行。",
        "metrics": ["传感器融合", "边缘计算 ASP", "时延", "安全认证"],
    },
    "platforms": {
        "name": "机器人 OEM 与集成平台",
        "why": "OEM 把硬件、软件和制造流程整合成可部署系统。",
        "metrics": ["出货量", "毛利率", "服务收入", "客户试点"],
    },
    "automation": {
        "name": "工厂自动化与部署",
        "why": "真实部署取决于系统集成、安全、维护和工厂流程重构。",
        "metrics": ["订单出货比", "机器人密度", "服务附着率", "回收期"],
    },
}

CATEGORY_ZH = {
    "AI accelerator": "AI 加速器",
    "Custom silicon / networking": "自研芯片 / 网络",
    "Foundry": "晶圆代工",
    "Lithography equipment": "光刻设备",
    "HBM / memory": "HBM / 存储",
    "Cloud platform": "云平台",
    "AI server integration": "AI 服务器集成",
    "Surgical robotics": "手术机器人",
    "Automation / testing": "自动化 / 测试",
    "Industrial automation": "工业自动化",
    "Industrial robotics": "工业机器人",
    "Humanoid optionality": "人形机器人期权",
    "Robot AI compute": "机器人 AI 计算",
}

ROLE_ZH = {
    "NVDA": "控制最核心的 AI 计算层，也提供机器人仿真、边缘 AI 与软件栈。",
    "AVGO": "供应定制 AI 芯片、网络芯片和连接能力。",
    "TSM": "控制先进制程制造与先进封装瓶颈。",
    "ASML": "控制 EUV 光刻设备供给。",
    "MU": "受益于 AI 内存带宽与 HBM 需求。",
    "MSFT": "通过云和软件商业化 AI 能力。",
    "AMZN": "AWS AI 云和零售现金流平台。",
    "SMCI": "受益于 AI 服务器和液冷集成需求。",
    "ISRG": "手术机器人装机基础和耗材生态。",
    "TER": "半导体测试，并有协作机器人敞口。",
    "ROK": "工厂自动化控制层。",
    "ABB": "全球机器人与自动化供应商。",
    "TSLA": "潜在人形机器人系统集成商。",
    "6954.T": "机器人硬件和 CNC 自动化龙头。",
}

KEY_METRIC_ZH = {
    "NVDA": "数据中心收入、GPU 供给、机器人平台采用",
    "AVGO": "AI 网络与定制 ASIC 收入",
    "TSM": "先进制程利用率与 CoWoS 产能",
    "ASML": "EUV 订单与 High-NA 采用",
    "MU": "HBM 收入占比与存储价格",
    "MSFT": "Azure AI 贡献与 capex 效率",
    "AMZN": "AWS 增长与经营利润率",
    "SMCI": "AI 服务器收入与毛利质量",
    "ISRG": "手术量增长与装机基础",
    "TER": "半导体测试复苏与机器人订单",
    "ROK": "自动化订单与订单出货比",
    "ABB": "机器人订单与利润率",
    "TSLA": "Optimus 里程碑与汽车现金流",
    "6954.T": "机器人订单与中国工厂自动化",
}

RISK_ZH = {
    "NVDA": "估值依赖持续领先和高利润率，机器人收入目前还不是主要估值驱动。",
    "AVGO": "客户集中度和集成复杂度。",
    "TSM": "地缘政治和资本开支周期风险。",
    "ASML": "出口管制和订单周期波动。",
    "MU": "存储行业仍具周期性且资本开支强。",
    "MSFT": "AI capex 回收期可能长于预期。",
    "AMZN": "零售利润率和云竞争。",
    "SMCI": "治理、毛利压力和营运资本波动。",
    "ISRG": "高预期和医院资本开支周期。",
    "TER": "测试需求周期波动。",
    "ROK": "工业周期放缓。",
    "ABB": "欧洲和中国工业需求敞口。",
    "TSLA": "机器人价值仍主要是远期期权。",
    "6954.T": "工厂自动化周期风险。",
}


def _zh_layer(layer: IndustryLayer) -> IndustryLayer:
    translated = LAYER_ZH.get(layer.id)
    if not translated:
        return layer
    return layer.model_copy(
        update={
            "name": translated["name"],
            "why_it_matters": translated["why"],
            "key_metrics": translated["metrics"],
        }
    )


def _zh_company(company: IndustryCompany) -> IndustryCompany:
    return company.model_copy(
        update={
            "layer": LAYER_ZH.get(_layer_id_from_name(company.layer), {}).get("name", company.layer),
            "category": CATEGORY_ZH.get(company.category, company.category),
            "role": ROLE_ZH.get(company.symbol, company.role),
            "key_metric": KEY_METRIC_ZH.get(company.symbol, company.key_metric),
            "risk": RISK_ZH.get(company.symbol, company.risk),
        }
    )


def _layer_id_from_name(name: str) -> str:
    for layer_id, translated in LAYER_ZH.items():
        if translated["name"] == name:
            return layer_id
    english = {
        "AI compute chips": "compute",
        "Foundry and advanced packaging": "foundry-packaging",
        "HBM, networking, and optical links": "memory-networking",
        "Cloud platforms and AI applications": "cloud-platforms",
        "Data-center power and cooling": "power-cooling",
        "Actuators, reducers, and motion control": "actuators",
        "Sensors, vision, and edge AI": "sensors-vision",
        "Robot OEM and integration platforms": "platforms",
        "Factory automation and deployment": "automation",
    }
    return english.get(name, name)


def _localize_response(response: IndustryChainResponse, language: str) -> IndustryChainResponse:
    if language.lower() not in {"zh", "cn", "zh-cn"}:
        return response
    if response.theme == "robotics":
        return response.model_copy(
            update={
                "title": "机器人产业链研究",
                "summary": "先看执行器、减速器和运动控制，再验证感知、边缘 AI、OEM 集成与部署经济性。",
                "scarce_layers": ["执行器、减速器与运动控制", "传感器、视觉与边缘 AI"],
                "layers": [_zh_layer(layer) for layer in response.layers],
                "companies": [_zh_company(company) for company in response.companies],
                "valuation_columns": VALUATION_COLUMNS_ZH,
                "methodology": "研究口径：先按产业链层级寻找瓶颈，再看公司所处位置、证据强度、PEG、增长、毛利率、估值信号与主要风险。PEG 只作为估值校验，不直接生成买卖结论。",
                "disclaimer": "仅用于研究辅助。估值字段为演示参考，正式决策前需要用公告、财报电话会和最新市场数据复核。",
            }
        )
    return response.model_copy(
        update={
            "title": "AI 基础设施产业链研究",
            "summary": "先从晶圆代工/先进封装、AI 计算、HBM/网络、云商业化和电力散热约束开始排查。",
            "scarce_layers": ["晶圆代工与先进封装", "AI 计算芯片", "HBM、网络与光连接"],
            "layers": [_zh_layer(layer) for layer in response.layers],
            "companies": [_zh_company(company) for company in response.companies],
            "valuation_columns": VALUATION_COLUMNS_ZH,
            "methodology": "研究口径：先排产业链瓶颈层级，再比较公司位置、证据强度、PEG、收入增长、毛利率和风险点。估值分层用于确定研究优先级，不等同于直接交易信号。",
            "disclaimer": "仅用于研究辅助。估值字段为演示参考，不构成直接交易建议。",
        }
    )


def _ai_layers() -> list[IndustryLayer]:
    return [
        IndustryLayer(
            id="compute",
            name="AI compute chips",
            direction="upstream",
            bottleneck_score=0.92,
            why_it_matters="Training and inference demand first translate into accelerators, custom silicon, and memory bandwidth needs.",
            key_metrics=["Data-center revenue", "accelerator backlog", "HBM attach rate", "gross margin"],
        ),
        IndustryLayer(
            id="foundry-packaging",
            name="Foundry and advanced packaging",
            direction="upstream",
            bottleneck_score=0.95,
            why_it_matters="Advanced nodes, CoWoS-style packaging, and yield determine whether AI chip supply can scale.",
            key_metrics=["wafer capacity", "advanced packaging capacity", "capex", "lead time"],
        ),
        IndustryLayer(
            id="memory-networking",
            name="HBM, networking, and optical links",
            direction="midstream",
            bottleneck_score=0.88,
            why_it_matters="AI clusters are constrained by bandwidth, latency, and memory capacity as much as raw compute.",
            key_metrics=["HBM revenue mix", "switch silicon share", "optical module demand", "inventory"],
        ),
        IndustryLayer(
            id="cloud-platforms",
            name="Cloud platforms and AI applications",
            direction="downstream",
            bottleneck_score=0.68,
            why_it_matters="Cloud platforms monetize AI capacity and decide the pace of capex absorption.",
            key_metrics=["AI capex", "cloud revenue growth", "utilization", "free cash flow"],
        ),
        IndustryLayer(
            id="power-cooling",
            name="Data-center power and cooling",
            direction="infrastructure",
            bottleneck_score=0.82,
            why_it_matters="Grid connection, thermal density, and power equipment increasingly gate data-center deployment.",
            key_metrics=["power backlog", "liquid cooling adoption", "grid interconnect timing", "orders"],
        ),
    ]


def _robotics_layers() -> list[IndustryLayer]:
    return [
        IndustryLayer(
            id="actuators",
            name="Actuators, reducers, and motion control",
            direction="upstream",
            bottleneck_score=0.9,
            why_it_matters="Cost, reliability, torque density, and lifetime are core constraints for humanoid and industrial robots.",
            key_metrics=["unit cost", "qualification cycle", "precision", "yield"],
        ),
        IndustryLayer(
            id="sensors-vision",
            name="Sensors, vision, and edge AI",
            direction="midstream",
            bottleneck_score=0.78,
            why_it_matters="Robots need perception and local inference to operate safely in variable environments.",
            key_metrics=["sensor fusion", "edge compute ASP", "latency", "safety certification"],
        ),
        IndustryLayer(
            id="platforms",
            name="Robot OEM and integration platforms",
            direction="downstream",
            bottleneck_score=0.72,
            why_it_matters="OEMs integrate hardware, software, and manufacturing processes into deployable systems.",
            key_metrics=["shipments", "gross margin", "service revenue", "customer pilots"],
        ),
        IndustryLayer(
            id="automation",
            name="Factory automation and deployment",
            direction="infrastructure",
            bottleneck_score=0.74,
            why_it_matters="Real deployment depends on systems integration, safety, maintenance, and factory workflow redesign.",
            key_metrics=["book-to-bill", "robot density", "service attach", "payback period"],
        ),
    ]


AI_COMPANIES = [
    IndustryCompany(symbol="NVDA", name="NVIDIA", market="US", layer="AI compute chips", category="AI accelerator", role="Controls the most visible compute layer", market_cap_usd_bn=3200, pe=46, ps=25, peg=1.3, revenue_growth=0.78, gross_margin=0.73, valuation_signal="expensive", evidence_strength="strong", key_metric="Data-center revenue growth and GPU supply", risk="Valuation assumes sustained dominance and high margins.", research_priority=0.92),
    IndustryCompany(symbol="AVGO", name="Broadcom", market="US", layer="HBM, networking, and optical links", category="Custom silicon / networking", role="Supplies custom AI silicon and networking", market_cap_usd_bn=780, pe=34, ps=17, peg=1.7, revenue_growth=0.32, gross_margin=0.69, valuation_signal="fair", evidence_strength="strong", key_metric="AI networking and custom ASIC revenue", risk="Customer concentration and integration complexity.", research_priority=0.86),
    IndustryCompany(symbol="TSM", name="TSMC", market="US", layer="Foundry and advanced packaging", category="Foundry", role="Controls advanced-node manufacturing bottleneck", market_cap_usd_bn=900, pe=28, ps=11, peg=1.2, revenue_growth=0.26, gross_margin=0.55, valuation_signal="fair", evidence_strength="strong", key_metric="Advanced-node utilization and CoWoS capacity", risk="Geopolitical and capex-cycle exposure.", research_priority=0.95),
    IndustryCompany(symbol="ASML", name="ASML", market="US", layer="Foundry and advanced packaging", category="Lithography equipment", role="Controls EUV lithography supply", market_cap_usd_bn=410, pe=36, ps=13, peg=1.8, revenue_growth=0.14, gross_margin=0.51, valuation_signal="fair", evidence_strength="strong", key_metric="EUV backlog and high-NA adoption", risk="Export controls and order-cycle lumpiness.", research_priority=0.88),
    IndustryCompany(symbol="MU", name="Micron", market="US", layer="HBM, networking, and optical links", category="HBM / memory", role="Benefits from AI memory bandwidth demand", market_cap_usd_bn=150, pe=22, ps=5, peg=0.9, revenue_growth=0.45, gross_margin=0.36, valuation_signal="watch", evidence_strength="medium", key_metric="HBM mix and memory pricing", risk="Memory remains cyclical and capital intensive.", research_priority=0.78),
    IndustryCompany(symbol="MSFT", name="Microsoft", market="US", layer="Cloud platforms and AI applications", category="Cloud platform", role="Monetizes AI through cloud and software", market_cap_usd_bn=3400, pe=35, ps=12, peg=2.0, revenue_growth=0.16, gross_margin=0.69, valuation_signal="fair", evidence_strength="strong", key_metric="Azure AI contribution and capex efficiency", risk="AI capex payback may take longer than expected.", research_priority=0.76),
    IndustryCompany(symbol="AMZN", name="Amazon", market="US", layer="Cloud platforms and AI applications", category="Cloud platform", role="AI cloud and retail cash-flow platform", market_cap_usd_bn=2100, pe=38, ps=3.5, peg=1.4, revenue_growth=0.13, gross_margin=0.49, valuation_signal="fair", evidence_strength="strong", key_metric="AWS growth and operating margin", risk="Retail margin and cloud competition.", research_priority=0.72),
    IndustryCompany(symbol="SMCI", name="Super Micro Computer", market="US", layer="Data-center power and cooling", category="AI server integration", role="Benefits from AI server demand and liquid cooling", market_cap_usd_bn=45, pe=18, ps=1.4, peg=0.7, revenue_growth=0.55, gross_margin=0.14, valuation_signal="watch", evidence_strength="medium", key_metric="AI server revenue and gross margin quality", risk="Governance, margin pressure, and working-capital volatility.", research_priority=0.66),
]

ROBOTICS_COMPANIES = [
    IndustryCompany(symbol="ISRG", name="Intuitive Surgical", market="US", layer="Robot OEM and integration platforms", category="Surgical robotics", role="Installed-base and recurring instrument ecosystem", market_cap_usd_bn=210, pe=65, ps=20, peg=3.1, revenue_growth=0.17, gross_margin=0.66, valuation_signal="expensive", evidence_strength="strong", key_metric="Procedure growth and installed base", risk="High expectations and hospital capex cycles.", research_priority=0.74),
    IndustryCompany(symbol="TER", name="Teradyne", market="US", layer="Factory automation and deployment", category="Automation / testing", role="Semiconductor testing plus collaborative robotics exposure", market_cap_usd_bn=25, pe=29, ps=6, peg=1.8, revenue_growth=0.12, gross_margin=0.58, valuation_signal="fair", evidence_strength="medium", key_metric="Semi test recovery and robotics orders", risk="Cyclical testing demand.", research_priority=0.68),
    IndustryCompany(symbol="ROK", name="Rockwell Automation", market="US", layer="Factory automation and deployment", category="Industrial automation", role="Factory automation control layer", market_cap_usd_bn=34, pe=31, ps=4.2, peg=2.0, revenue_growth=0.08, gross_margin=0.41, valuation_signal="watch", evidence_strength="strong", key_metric="Automation orders and book-to-bill", risk="Industrial cycle slowdown.", research_priority=0.64),
    IndustryCompany(symbol="ABB", name="ABB", market="US", layer="Robot OEM and integration platforms", category="Industrial robotics", role="Global robotics and automation supplier", market_cap_usd_bn=115, pe=30, ps=3.4, peg=1.9, revenue_growth=0.07, gross_margin=0.36, valuation_signal="fair", evidence_strength="strong", key_metric="Robotics orders and margin", risk="Europe/China industrial exposure.", research_priority=0.7),
    IndustryCompany(symbol="TSLA", name="Tesla", market="US", layer="Robot OEM and integration platforms", category="Humanoid optionality", role="Potential humanoid robotics integrator", market_cap_usd_bn=850, pe=75, ps=8.5, peg=3.4, revenue_growth=0.08, gross_margin=0.18, valuation_signal="expensive", evidence_strength="weak", key_metric="Optimus milestones and auto cash generation", risk="Robotics value is still mostly optionality.", research_priority=0.52),
    IndustryCompany(symbol="NVDA", name="NVIDIA", market="US", layer="Sensors, vision, and edge AI", category="Robot AI compute", role="Supplies simulation, edge AI, and robotics software stack", market_cap_usd_bn=3200, pe=46, ps=25, peg=1.3, revenue_growth=0.78, gross_margin=0.73, valuation_signal="expensive", evidence_strength="strong", key_metric="Robotics platform adoption and edge AI revenue", risk="Robotics revenue is not yet the main valuation driver.", research_priority=0.76),
    IndustryCompany(symbol="6954.T", name="Fanuc", market="GLOBAL", layer="Actuators, reducers, and motion control", category="Industrial robotics", role="Controls robot hardware and CNC automation", market_cap_usd_bn=28, pe=27, ps=4.8, peg=2.2, revenue_growth=0.04, gross_margin=0.39, valuation_signal="watch", evidence_strength="strong", key_metric="Robot orders and China factory automation", risk="Factory automation cycle risk.", research_priority=0.67),
]


def get_industry_chain(theme: str = "ai", language: str = "zh") -> IndustryChainResponse:
    selected = "robotics" if theme.lower() in {"robot", "robotics", "机器人"} else "ai"
    if selected == "robotics":
        response = IndustryChainResponse(
            theme="robotics",
            title="Robotics value-chain research",
            summary="Start from actuators and motion control, then verify perception, edge AI, OEM integration, and deployment economics.",
            scarce_layers=["Actuators, reducers, and motion control", "Sensors, vision, and edge AI"],
            layers=_robotics_layers(),
            companies=ROBOTICS_COMPANIES,
            valuation_columns=VALUATION_COLUMNS,
            methodology="Rank layers before companies. PEG is treated as a valuation sanity check, not a buy/sell trigger.",
            disclaimer="Research support only. Metrics are demo references and should be verified with filings, transcripts, and current market data before decisions.",
        )
        return _localize_response(response, language)
    response = IndustryChainResponse(
        theme="ai",
        title="AI infrastructure value-chain research",
        summary="Start with foundry/packaging, AI compute, memory/networking, cloud monetization, and power/cooling constraints.",
        scarce_layers=["Foundry and advanced packaging", "AI compute chips", "HBM, networking, and optical links"],
        layers=_ai_layers(),
        companies=AI_COMPANIES,
        valuation_columns=VALUATION_COLUMNS,
        methodology="Rank scarce layers first, then compare companies by chain position, evidence quality, PEG, growth, margin, and risk.",
        disclaimer="Research support only. Valuation fields are demo references and not direct trading instructions.",
    )
    return _localize_response(response, language)
