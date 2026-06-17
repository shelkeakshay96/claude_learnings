"""Earnings & Growth Agent - Analyzes revenue and earnings trends."""

from tools.data_fetcher import get_stock_fundamentals, get_historical_data


def analyze(symbol: str) -> dict:
    """Analyze growth potential using earnings growth, revenue growth, and price trends."""
    data = get_stock_fundamentals(symbol)

    if 'error' in data:
        return {
            'agent': 'Earnings & Growth',
            'symbol': symbol,
            'score': 0,
            'error': data['error'],
            'analysis': 'Unable to fetch data'
        }

    revenue_growth = data.get('revenue_growth', 0)
    earnings_growth = data.get('earnings_growth', 0)
    pe_ratio = data.get('pe_ratio', 0)
    forward_pe = data.get('forward_pe', 0)

    # Get historical price data
    hist = get_historical_data(symbol)
    price_momentum = hist.get('1y_return', 0)

    # Scoring logic
    score = 3.0
    reasons = []

    # Revenue growth (target: >10% annually)
    if revenue_growth > 0.20:
        score += 1.0
        reasons.append(f"Strong revenue growth: {revenue_growth:.1%}")
    elif revenue_growth > 0.10:
        score += 0.5
        reasons.append(f"Good revenue growth: {revenue_growth:.1%}")
    elif revenue_growth < 0:
        score -= 1.0
        reasons.append(f"Declining revenue: {revenue_growth:.1%}")

    # Earnings growth (target: >10% annually)
    if earnings_growth > 0.20:
        score += 1.0
        reasons.append(f"Excellent earnings growth: {earnings_growth:.1%}")
    elif earnings_growth > 0.10:
        score += 0.5
        reasons.append(f"Good earnings growth: {earnings_growth:.1%}")
    elif earnings_growth < 0:
        score -= 1.0
        reasons.append(f"Declining earnings: {earnings_growth:.1%}")

    # PEG ratio analysis (PE / Growth rate, target: <1)
    if earnings_growth > 0 and pe_ratio > 0:
        peg = pe_ratio / (earnings_growth * 100)
        if peg < 1:
            score += 0.5
            reasons.append(f"Attractive valuation: PEG {peg:.2f}")
        elif peg > 2:
            score -= 0.5
            reasons.append(f"Expensive relative to growth: PEG {peg:.2f}")

    # Price momentum (1-year returns)
    if price_momentum > 30:
        score += 0.5
        reasons.append(f"Strong uptrend: {price_momentum:.1f}% YoY")
    elif price_momentum < -20:
        score -= 0.5
        reasons.append(f"Bearish trend: {price_momentum:.1f}% YoY")

    score = max(1.0, min(5.0, score))

    return {
        'agent': 'Earnings & Growth',
        'symbol': symbol,
        'score': round(score, 2),
        'metrics': {
            'revenue_growth': f"{revenue_growth:.1%}",
            'earnings_growth': f"{earnings_growth:.1%}",
            'pe_ratio': f"{pe_ratio:.2f}",
            '1y_return': f"{price_momentum:.1f}%",
        },
        'analysis': ' | '.join(reasons) if reasons else "Growth metrics within average range"
    }
