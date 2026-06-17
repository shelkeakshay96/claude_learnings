"""Multi-Agent Coordinator - Synthesizes analyses from all agents."""

import sys
from agents import financial_ratios_agent, earnings_growth_agent, cash_flow_agent, valuation_agent
from tools.data_fetcher import get_stock_fundamentals


def analyze_stock(symbol: str) -> dict:
    """Orchestrate all agents to analyze a stock comprehensively."""

    print(f"\n📊 Analyzing {symbol}...\n")

    # Run all agents in parallel (conceptually)
    results = {
        'financial_ratios': financial_ratios_agent.analyze(symbol),
        'earnings_growth': earnings_growth_agent.analyze(symbol),
        'cash_flow': cash_flow_agent.analyze(symbol),
        'valuation': valuation_agent.analyze(symbol),
    }

    # Aggregate scores
    scores = [r['score'] for r in results.values() if 'score' in r and r['score'] > 0]

    if not scores:
        return {
            'symbol': symbol,
            'error': 'Could not fetch data for stock',
            'agents': results
        }

    avg_score = sum(scores) / len(scores)
    score_variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)

    # Generate recommendation
    recommendation, confidence = get_recommendation(avg_score, score_variance, len(scores))

    # Identify consensus and disagreement
    consensus, disagreement = analyze_consensus(results)

    # Risk assessment
    risk_level = assess_risk(results, score_variance)

    # Compile final report
    report = {
        'symbol': symbol,
        'aggregate_score': round(avg_score, 2),
        'recommendation': recommendation,
        'confidence': f"{confidence}%",
        'consensus': consensus,
        'disagreement': disagreement,
        'risk_level': risk_level,
        'agent_scores': {
            'Financial Ratios': results['financial_ratios'].get('score', 'N/A'),
            'Earnings & Growth': results['earnings_growth'].get('score', 'N/A'),
            'Cash Flow': results['cash_flow'].get('score', 'N/A'),
            'Valuation': results['valuation'].get('score', 'N/A'),
        },
        'detailed_analyses': results,
    }

    return report


def get_recommendation(avg_score: float, variance: float, agent_count: int) -> tuple:
    """Generate buy/hold/sell recommendation with confidence level."""

    if avg_score >= 4.0:
        rec = "🟢 BUY"
        confidence = min(90, 50 + int((avg_score - 3) * 20))
    elif avg_score >= 3.5:
        rec = "🟡 BUY (with caution)"
        confidence = min(85, 40 + int((avg_score - 3) * 15))
    elif avg_score >= 3.0:
        rec = "🔵 HOLD"
        confidence = 60
    elif avg_score >= 2.5:
        rec = "🟠 SELL (with caution)"
        confidence = min(75, 40 + int((3 - avg_score) * 15))
    else:
        rec = "🔴 SELL"
        confidence = min(90, 50 + int((3 - avg_score) * 20))

    # Reduce confidence if agents disagree significantly
    if variance > 0.5:
        confidence = int(confidence * 0.7)

    return rec, max(30, confidence)


def analyze_consensus(results: dict) -> tuple:
    """Identify areas of agreement and disagreement between agents."""

    scores = {k: v.get('score', 0) for k, v in results.items()}
    consensus_list = []
    disagreement_list = []

    # Find consensus (similar scores)
    avg = sum(scores.values()) / len(scores)
    high_consensus = [k for k, v in scores.items() if abs(v - avg) < 0.5]
    low_consensus = [k for k, v in scores.items() if abs(v - avg) > 0.8]

    if len(high_consensus) >= 3:
        consensus_list.append(f"{len(high_consensus)} agents agree on overall assessment")

    # Check specific disagreements
    financials_agree = abs(scores['financial_ratios'] - scores['cash_flow']) < 0.5
    growth_valuation_agree = abs(scores['earnings_growth'] - scores['valuation']) < 0.5

    if not financials_agree:
        disagreement_list.append("Financial strength vs. cash flow differ")

    if not growth_valuation_agree:
        disagreement_list.append("Growth outlook vs. valuation have different views")

    consensus_text = " | ".join(consensus_list) if consensus_list else "Mixed agreement across agents"
    disagreement_text = " | ".join(disagreement_list) if disagreement_list else "No major disagreements"

    return consensus_text, disagreement_text


def assess_risk(results: dict, variance: float) -> str:
    """Assess overall investment risk level."""

    factors = 0
    concerns = []

    # Check cash flow (most important risk indicator)
    cash_flow_score = results['cash_flow'].get('score', 3)
    if cash_flow_score < 2.5:
        factors += 2
        concerns.append("Weak cash flow")

    # Check debt/leverage
    ratios_analysis = results['financial_ratios'].get('analysis', '')
    if 'High leverage' in ratios_analysis or 'High debt' in ratios_analysis:
        factors += 1
        concerns.append("High leverage")

    # Check growth
    growth_score = results['earnings_growth'].get('score', 3)
    if growth_score < 2.0:
        factors += 1
        concerns.append("Declining growth")

    # Check agent disagreement
    if variance > 0.8:
        factors += 1
        concerns.append("Agent disagreement on outlook")

    if factors >= 3:
        return f"🔴 HIGH - {', '.join(concerns)}"
    elif factors == 2:
        return f"🟠 MEDIUM - {', '.join(concerns)}"
    elif factors == 1:
        return f"🟡 LOW - {concerns[0] if concerns else 'Monitor closely'}"
    else:
        return "🟢 LOW - Fundamentals appear stable"


def print_report(report: dict):
    """Pretty-print the analysis report."""

    print("\n" + "=" * 80)
    print(f"STOCK ANALYSIS REPORT: {report['symbol']}")
    print("=" * 80)

    if 'error' in report:
        print(f"❌ {report['error']}")
        return

    print(f"\n📈 AGGREGATE SCORE: {report['aggregate_score']}/5.0")
    print(f"💡 RECOMMENDATION: {report['recommendation']}")
    print(f"🎯 CONFIDENCE: {report['confidence']}")

    print(f"\n🤝 CONSENSUS: {report['consensus']}")
    print(f"⚡ DISAGREEMENT: {report['disagreement']}")

    print(f"\n⚠️  RISK LEVEL: {report['risk_level']}")

    print(f"\n📊 AGENT SCORES:")
    for agent, score in report['agent_scores'].items():
        bar = "█" * int(score * 2) + "░" * (10 - int(score * 2)) if isinstance(score, (int, float)) else "N/A"
        print(f"   {agent:20} {score:>5} {bar}")

    print(f"\n📋 DETAILED ANALYSES:")
    for agent_name, analysis in report['detailed_analyses'].items():
        if 'error' not in analysis:
            print(f"\n   {analysis['agent']}:")
            print(f"      Score: {analysis['score']}/5.0")
            print(f"      {analysis['analysis']}")

    print("\n" + "=" * 80)


def main():
    """Main entry point for the coordinator."""
    if len(sys.argv) < 2:
        print("Usage: python coordinator.py <SYMBOL> [SYMBOL2] ...")
        print("Example: python coordinator.py INFY TCS RELIANCE")
        sys.exit(1)

    symbols = sys.argv[1:]

    for symbol in symbols:
        report = analyze_stock(symbol.upper())
        print_report(report)


if __name__ == "__main__":
    main()
