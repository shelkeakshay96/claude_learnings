"""Claude-Enhanced Coordinator - Uses Claude API to synthesize agent analyses."""

import sys
import json
from dotenv import load_dotenv
import os
from agents import financial_ratios_agent, earnings_growth_agent, cash_flow_agent, valuation_agent

load_dotenv()


def get_claude_client():
    """Get authenticated Anthropic client."""
    try:
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("❌ ANTHROPIC_API_KEY not set in .env file")
            return None
        client = anthropic.Anthropic(api_key=api_key)
        return client
    except Exception as e:
        print(f"❌ Error initializing Anthropic client: {e}")
        return None


def analyze_stock_with_claude(symbol: str, client) -> dict:
    """Use Claude to synthesize analyses from all agents."""

    print(f"\n📊 Analyzing {symbol} with Claude...\n")

    # Gather agent analyses
    agent_results = {
        'Financial Ratios': financial_ratios_agent.analyze(symbol),
        'Earnings & Growth': earnings_growth_agent.analyze(symbol),
        'Cash Flow': cash_flow_agent.analyze(symbol),
        'Valuation': valuation_agent.analyze(symbol),
    }

    # Check for errors
    if any('error' in r for r in agent_results.values()):
        errors = [r['error'] for r in agent_results.values() if 'error' in r]
        return {'symbol': symbol, 'error': f"Agent errors: {errors}"}

    # Prepare analysis summary for Claude
    analysis_summary = json.dumps({
        name: {
            'score': data.get('score'),
            'analysis': data.get('analysis'),
            'metrics': data.get('metrics')
        }
        for name, data in agent_results.items()
    }, indent=2)

    # Ask Claude to synthesize
    prompt = f"""You are a financial analyst synthesizing multiple expert assessments for the stock {symbol}.

Here are the individual agent analyses:

{analysis_summary}

Based on these specialized analyses, provide:
1. An overall investment recommendation (BUY, HOLD, SELL)
2. Key consensus points between agents
3. Important disagreements or concerns
4. Top 3 investment considerations
5. Risk factors to monitor

Format your response as structured JSON with these exact keys:
{{"recommendation": "...", "confidence": "...", "consensus": "...", "concerns": "...", "top_considerations": [...], "risk_factors": [...]}}

Be concise but insightful. The recommendation should be actionable."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    try:
        # Parse Claude's response
        response_text = message.content[0].text
        # Find JSON in response
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            synthesis = json.loads(json_match.group())
        else:
            synthesis = {"raw_response": response_text}
    except Exception as e:
        synthesis = {"raw_response": message.content[0].text}

    # Compile report
    scores = [data['score'] for data in agent_results.values()]
    avg_score = sum(scores) / len(scores)

    report = {
        'symbol': symbol,
        'agent_scores': {name: data['score'] for name, data in agent_results.items()},
        'aggregate_score': round(avg_score, 2),
        'claude_synthesis': synthesis,
        'detailed_analyses': agent_results,
    }

    return report


def print_claude_report(report: dict):
    """Pretty-print the Claude-synthesized report."""

    print("\n" + "=" * 80)
    print(f"CLAUDE-SYNTHESIZED ANALYSIS: {report['symbol']}")
    print("=" * 80)

    if 'error' in report:
        print(f"❌ {report['error']}")
        return

    print(f"\n📈 AGGREGATE SCORE: {report['aggregate_score']}/5.0")

    synthesis = report.get('claude_synthesis', {})

    if 'recommendation' in synthesis:
        print(f"💡 RECOMMENDATION: {synthesis['recommendation']}")
        print(f"🎯 CONFIDENCE: {synthesis.get('confidence', 'N/A')}")

    if 'consensus' in synthesis:
        print(f"\n🤝 CONSENSUS:\n   {synthesis['consensus']}")

    if 'concerns' in synthesis:
        print(f"\n⚠️  KEY CONCERNS:\n   {synthesis['concerns']}")

    if 'top_considerations' in synthesis:
        print(f"\n💭 TOP INVESTMENT CONSIDERATIONS:")
        for i, consideration in enumerate(synthesis['top_considerations'], 1):
            print(f"   {i}. {consideration}")

    if 'risk_factors' in synthesis:
        print(f"\n🚨 RISK FACTORS:")
        for risk in synthesis['risk_factors']:
            print(f"   • {risk}")

    print(f"\n📊 AGENT SCORES:")
    for agent, score in report['agent_scores'].items():
        bar = "█" * int(score * 2) + "░" * (10 - int(score * 2))
        print(f"   {agent:20} {score:>5} {bar}")

    print("\n" + "=" * 80)


def main():
    """Main entry point for Claude-enhanced coordinator."""
    client = get_claude_client()
    if not client:
        print("Falling back to standard coordinator without Claude synthesis...")
        return

    if len(sys.argv) < 2:
        print("Usage: python claude_coordinator.py <SYMBOL> [SYMBOL2] ...")
        print("Example: python claude_coordinator.py INFY TCS RELIANCE")
        sys.exit(1)

    symbols = sys.argv[1:]

    for symbol in symbols:
        report = analyze_stock_with_claude(symbol.upper(), client)
        print_claude_report(report)


if __name__ == "__main__":
    main()
