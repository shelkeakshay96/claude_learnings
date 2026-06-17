"""Cash Flow Agent - Analyzes operational and free cash flow health."""

from tools.data_fetcher import get_stock_fundamentals


def analyze(symbol: str) -> dict:
    """Analyze cash flow quality and sustainability."""
    data = get_stock_fundamentals(symbol)

    if 'error' in data:
        return {
            'agent': 'Cash Flow',
            'symbol': symbol,
            'score': 0,
            'error': data['error'],
            'analysis': 'Unable to fetch data'
        }

    ocf = data.get('operating_cash_flow', 0)
    fcf = data.get('free_cash_flow', 0)
    net_income = data.get('profit_margin', 0)
    market_cap = data.get('market_cap', 1)

    score = 3.0
    reasons = []

    # Check if FCF is positive
    if fcf > 0:
        score += 1.0
        reasons.append("Positive free cash flow")

        # FCF to market cap ratio (indicator of cash generation power)
        fcf_to_mcap = fcf / market_cap if market_cap > 0 else 0
        if fcf_to_mcap > 0.05:
            score += 0.5
            reasons.append(f"Strong FCF yield: {fcf_to_mcap:.1%}")
    else:
        score -= 1.0
        reasons.append("Negative free cash flow - concerning")

    # Operating cash flow analysis
    if ocf > 0:
        score += 0.5
        reasons.append("Healthy operating cash flow")

        # FCF margin (FCF as % of OCF)
        if fcf > 0:
            fcf_margin = fcf / ocf if ocf > 0 else 0
            if fcf_margin > 0.5:
                score += 0.5
                reasons.append(f"Good cash conversion: {fcf_margin:.1%} OCF converts to FCF")
            elif fcf_margin < 0:
                score -= 0.5
                reasons.append("High capex requirements limiting FCF")
    else:
        score -= 1.0
        reasons.append("Negative operating cash flow")

    # Cash generation quality (OCF > Net Income indicates quality earnings)
    if ocf > 0 and net_income > 0 and ocf > net_income:
        score += 0.5
        reasons.append("High quality earnings (OCF > NI)")
    elif ocf > 0 and net_income > 0 and ocf < net_income * 0.5:
        score -= 0.5
        reasons.append("Earnings quality concern (OCF < NI)")

    score = max(1.0, min(5.0, score))

    return {
        'agent': 'Cash Flow',
        'symbol': symbol,
        'score': round(score, 2),
        'metrics': {
            'operating_cash_flow': f"₹{ocf/1e7:.1f}Cr" if ocf > 0 else f"₹{ocf/1e7:.1f}Cr",
            'free_cash_flow': f"₹{fcf/1e7:.1f}Cr" if fcf > 0 else f"₹{fcf/1e7:.1f}Cr",
            'fcf_to_market_cap': f"{(fcf/market_cap if market_cap > 0 else 0):.1%}",
        },
        'analysis': ' | '.join(reasons) if reasons else "Cash flow metrics within average range"
    }
