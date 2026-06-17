"""Financial Ratios Agent - Analyzes profitability and efficiency metrics."""

from tools.data_fetcher import get_stock_fundamentals


def analyze(symbol: str) -> dict:
    """Analyze financial health using ROE, margins, debt-to-equity, etc."""
    data = get_stock_fundamentals(symbol)

    if 'error' in data:
        return {
            'agent': 'Financial Ratios',
            'symbol': symbol,
            'score': 0,
            'error': data['error'],
            'analysis': 'Unable to fetch data'
        }

    roe = data.get('roe', 0)
    profit_margin = data.get('profit_margin', 0)
    debt_to_equity = data.get('debt_to_equity', 0)
    roa = data.get('roa', 0)

    # Scoring logic (0-5 scale, 3 is neutral)
    score = 3.0
    reasons = []

    # ROE analysis (target: >15%)
    if roe > 0.20:
        score += 1.0
        reasons.append(f"Strong ROE: {roe:.1%}")
    elif roe > 0.15:
        score += 0.5
        reasons.append(f"Good ROE: {roe:.1%}")
    elif roe < 0.05:
        score -= 1.0
        reasons.append(f"Weak ROE: {roe:.1%}")

    # Profit margin analysis (target: >10%)
    if profit_margin > 0.15:
        score += 0.5
        reasons.append(f"Excellent profit margin: {profit_margin:.1%}")
    elif profit_margin < 0.05:
        score -= 0.5
        reasons.append(f"Low profit margin: {profit_margin:.1%}")

    # Debt analysis (lower is better, target: <1.0)
    if debt_to_equity < 0.5:
        score += 0.5
        reasons.append(f"Low debt burden: D/E {debt_to_equity:.2f}")
    elif debt_to_equity > 2.0:
        score -= 1.0
        reasons.append(f"High leverage: D/E {debt_to_equity:.2f}")

    # ROA analysis (target: >5%)
    if roa > 0.10:
        score += 0.5
        reasons.append(f"Strong ROA: {roa:.1%}")

    # Clamp score between 1-5
    score = max(1.0, min(5.0, score))

    return {
        'agent': 'Financial Ratios',
        'symbol': symbol,
        'score': round(score, 2),
        'metrics': {
            'roe': f"{roe:.1%}",
            'profit_margin': f"{profit_margin:.1%}",
            'debt_to_equity': f"{debt_to_equity:.2f}",
            'roa': f"{roa:.1%}",
        },
        'analysis': ' | '.join(reasons) if reasons else "Metrics within average range"
    }
