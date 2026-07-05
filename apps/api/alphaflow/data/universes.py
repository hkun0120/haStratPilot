UNIVERSES: dict[str, list[str]] = {
    "ai_chips_cloud_us": [
        "NVDA",
        "AMD",
        "AVGO",
        "TSM",
        "ARM",
        "SMCI",
        "MU",
        "ASML",
        "MSFT",
        "GOOGL",
        "AMZN",
        "META",
        "QQQ",
    ],
    "mega_cap_us": ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "AVGO", "TSLA", "QQQ"],
    "etf_rotation": ["SPY", "QQQ", "SMH", "SOXX", "XLK", "TLT", "GLD", "IWM"],
    "defensive_etf": ["SPY", "QQQ", "TLT", "GLD", "XLU", "XLV", "SHY"],
    "hk_tech": ["0700.HK", "9988.HK", "3690.HK", "9618.HK", "1810.HK", "2018.HK", "9999.HK", "2800.HK"],
    "global_ai": [
        "NVDA",
        "AMD",
        "AVGO",
        "TSM",
        "ASML",
        "MSFT",
        "GOOGL",
        "AMZN",
        "0700.HK",
        "9988.HK",
        "3690.HK",
    ],
}

BENCHMARKS = {
    "US": "QQQ",
    "HK": "2800.HK",
    "GLOBAL": "QQQ",
}


def normalize_symbols(symbols: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for raw in symbols:
        symbol = raw.strip().upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        result.append(symbol)
    return result


def infer_universe_key(query: str, market: str | None = None) -> str:
    text = query.lower()
    if "港" in query or "hk" in text or market == "HK":
        return "hk_tech"
    if "etf" in text or "轮动" in query:
        return "etf_rotation"
    if "防御" in query or "低回撤" in query or "defensive" in text:
        return "defensive_etf"
    if "ai" in text or "芯片" in query or "云" in query:
        return "ai_chips_cloud_us"
    return "mega_cap_us"
