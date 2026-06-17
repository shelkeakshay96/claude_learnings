"""Valuation Agent - Determines if stock is fairly valued or mispriced."""

from tools.data_fetcher import get_stock_fundamentals


def analyze(symbol: str) -> dict:
    """Analyze valuation metrics to assess if stock is cheap, fair, or expensive."""
    data = get_stock_fundamentals(symbol)

    if 'error' in data:
        return {
            'agent': 'Valuation',
            'symbol': symbol,
            'score': 0,
            'error': data['error'],
            'analysis': 'Unable to fetch data'
        }

    pe_ratio = data.get('pe_ratio', 0)
    pb_ratio = data.get('pb_ratio', 0)
    dividend_yield = data.get('dividend_yield', 0)
    forward_pe = data.get('forward_pe', 0)
    roe = data.get('roe', 0)

    score = 3.0
    reasons = []

    # PE ratio analysis (NSE average ~18-20)
    if pe_ratio > 0:
        if pe_ratio < 15:
            score += 1.0
            reasons.append(f"Undervalued: PE {pe_ratio:.1f} (below market avg)")
        elif pe_ratio < 20:
            score += 0.5
            reasons.append(f"Fair valuation: PE {pe_ratio:.1f} (near market avg)")
        elif pe_ratio > 25:
            score -= 1.0
            reasons.append(f"Overvalued: PE {pe_ratio:.1f} (premium pricing)")

    # Forward PE vs Trailing PE (if company is improving)
    if forward_pe > 0 and pe_ratio > 0 and forward_pe < pe_ratio:
        score += 0.5
        reasons.append("Growth expected: Forward PE < Trailing PE")
    elif forward_pe > pe_ratio * 1.2:
        score -= 0.5
        reasons.append("Deteriorating outlook: Forward PE > Trailing PE")

    # PB ratio analysis (for quality stocks, PB should correlate with ROE)
    if pb_ratio > 0:
        if pb_ratio < 3 and roe > 0.15:
            score += 0.5
            reasons.append(f"Attractive PB: {pb_ratio:.2f} with strong ROE")
        elif pb_ratio > 5:
            score -= 0.5
            reasons.append(f"High PB ratio: {pb_ratio:.2f}")

    # Dividend yield (if paying dividends, good sign of stability)
    if dividend_yield > 0.02:
        score += 0.5
        reasons.append(f"Dividend support: {dividend_yield:.1%} yield")
    elif dividend_yield > 0:
        reasons.append(f"Dividend payout: {dividend_yield:.1%} yield")

    # Value score based on PE and PB combination
    value_score = (5 - min(pe_ratio / 30, 2.5)) + (5 - min(pb_ratio / 5, 2.5))
    if value_score > 6:
        reasons.append("Strong value characteristics")

    score = max(1.0, min(5.0, score))

    return {
        'agent': 'Valuation',
        'symbol': symbol,
        'score': round(score, 2),
        'metrics': {
            'pe_ratio': f"{pe_ratio:.2f}",
            'forward_pe': f"{forward_pe:.2f}" if forward_pe > 0 else "N/A",
            'pb_ratio': f"{pb_ratio:.2f}",
            'dividend_yield': f"{dividend_yield:.1%}",
        },
        'analysis': ' | '.join(reasons) if reasons else "Valuation metrics within normal range"
    }
