FUNDAMENTAL_SCORES: dict[str, dict[str, float | str]] = {
    "NVDA": {"quality": 0.95, "growth": 0.97, "valuation": 0.38, "cashflow": 0.9, "note": "AI accelerator leader; valuation risk is high."},
    "AMD": {"quality": 0.72, "growth": 0.76, "valuation": 0.5, "cashflow": 0.68, "note": "AI GPU challenger with execution sensitivity."},
    "AVGO": {"quality": 0.88, "growth": 0.79, "valuation": 0.55, "cashflow": 0.92, "note": "Custom silicon and networking exposure."},
    "TSM": {"quality": 0.92, "growth": 0.84, "valuation": 0.66, "cashflow": 0.86, "note": "Foundry bottleneck with geopolitics risk."},
    "ARM": {"quality": 0.78, "growth": 0.82, "valuation": 0.32, "cashflow": 0.7, "note": "IP royalty upside; valuation demanding."},
    "SMCI": {"quality": 0.45, "growth": 0.82, "valuation": 0.48, "cashflow": 0.35, "note": "Server growth with governance and margin risk."},
    "MU": {"quality": 0.62, "growth": 0.74, "valuation": 0.58, "cashflow": 0.5, "note": "Memory cycle and HBM exposure."},
    "ASML": {"quality": 0.94, "growth": 0.68, "valuation": 0.62, "cashflow": 0.9, "note": "Lithography bottleneck; export-control risk."},
    "MSFT": {"quality": 0.95, "growth": 0.77, "valuation": 0.61, "cashflow": 0.96, "note": "Cloud AI monetization and strong cash flow."},
    "GOOGL": {"quality": 0.88, "growth": 0.67, "valuation": 0.72, "cashflow": 0.91, "note": "AI infra plus search/ads resilience."},
    "AMZN": {"quality": 0.82, "growth": 0.73, "valuation": 0.6, "cashflow": 0.78, "note": "AWS and retail margin leverage."},
    "META": {"quality": 0.86, "growth": 0.7, "valuation": 0.68, "cashflow": 0.91, "note": "Ad cash flow funding AI capex."},
    "0700.HK": {"quality": 0.84, "growth": 0.55, "valuation": 0.7, "cashflow": 0.86, "note": "HK tech bellwether with China policy exposure."},
    "9988.HK": {"quality": 0.72, "growth": 0.45, "valuation": 0.74, "cashflow": 0.7, "note": "Cloud and commerce turnaround risk."},
    "3690.HK": {"quality": 0.7, "growth": 0.62, "valuation": 0.57, "cashflow": 0.68, "note": "Local services platform; margin competition risk."},
    "9618.HK": {"quality": 0.64, "growth": 0.48, "valuation": 0.65, "cashflow": 0.58, "note": "E-commerce and logistics exposure."},
    "1810.HK": {"quality": 0.5, "growth": 0.46, "valuation": 0.63, "cashflow": 0.42, "note": "Consumer electronics cyclicality."},
    "2018.HK": {"quality": 0.66, "growth": 0.5, "valuation": 0.62, "cashflow": 0.55, "note": "Health-tech platform risk."},
    "9999.HK": {"quality": 0.62, "growth": 0.44, "valuation": 0.64, "cashflow": 0.5, "note": "Online media and games exposure."},
}


def get_fundamental_score(symbol: str) -> dict[str, float | str]:
    if symbol in FUNDAMENTAL_SCORES:
        return FUNDAMENTAL_SCORES[symbol]
    if symbol.endswith(".HK"):
        return {"quality": 0.55, "growth": 0.5, "valuation": 0.55, "cashflow": 0.5, "note": "Fallback HK fundamental profile; verify with HKEX filings."}
    if symbol in {"SPY", "QQQ", "SMH", "SOXX", "XLK", "TLT", "GLD", "IWM", "XLU", "XLV", "SHY"}:
        return {"quality": 0.65, "growth": 0.55, "valuation": 0.6, "cashflow": 0.65, "note": "ETF proxy score based on liquidity and diversification."}
    return {"quality": 0.5, "growth": 0.5, "valuation": 0.5, "cashflow": 0.5, "note": "Fallback fundamental score; needs primary-source verification."}
