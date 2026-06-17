# Multi-Agent Stock Analysis System

A sophisticated stock analysis framework that uses multiple specialized AI agents to evaluate NSE (National Stock Exchange) stocks based on fundamental analysis. Each agent specializes in a different aspect of financial analysis, and a coordinator synthesizes their findings into actionable recommendations.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│           COORDINATOR (Orchestrator)                │
│  ┌──────────────────────────────────────────────┐  │
│  │  • Calls all agents in parallel              │  │
│  │  • Aggregates scores (1-5 scale)             │  │
│  │  • Analyzes consensus/disagreement           │  │
│  │  • Assesses risk level                       │  │
│  │  • Generates final recommendation            │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
         ↓      ↓      ↓      ↓
    ┌────┴──────┴──────┴──────┴────┐
    │                              │
    ▼        ▼        ▼        ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌────────┐
│Financial│ │Earnings│ │  Cash   │ │Valuation│
│ Ratios  │ │Growth  │ │  Flow   │ │         │
│ Agent   │ │ Agent  │ │ Agent   │ │ Agent   │
└────────┘ └────────┘ └──────────┘ └────────┘
    │        │        │        │
    └────────┴────────┴────────┘
           ▼ (all use)
    ┌─────────────────────┐
    │  Data Fetcher       │
    │ (yfinance adapter)  │
    └─────────────────────┘
```

## Agents

### 1. Financial Ratios Agent
**Analyzes:** Profitability and financial health
- **Metrics:** ROE, Profit Margin, Debt-to-Equity, ROA
- **Scoring:** Strong ROE (>20%) = +1.0 | Low margins = -0.5 | High leverage = -1.0

### 2. Earnings & Growth Agent
**Analyzes:** Revenue and earnings trajectory
- **Metrics:** Revenue Growth, Earnings Growth, PE Ratio, Price Momentum
- **Scoring:** Strong growth (>20%) = +1.0 | Declining earnings = -1.0 | Attractive PEG = +0.5

### 3. Cash Flow Agent
**Analyzes:** Operational sustainability and cash generation
- **Metrics:** Operating Cash Flow, Free Cash Flow, FCF-to-Market-Cap, Quality of Earnings
- **Scoring:** Positive FCF = +1.0 | Negative FCF = -1.0 | High capex burden = -0.5

### 4. Valuation Agent
**Analyzes:** Stock pricing relative to fundamentals
- **Metrics:** PE Ratio, Forward PE, PB Ratio, Dividend Yield
- **Scoring:** Undervalued PE (<15) = +1.0 | Overvalued (PE >25) = -1.0 | Good dividend = +0.5

## Coordinator Functions

The coordinator (orchestrator) synthesizes all agent analyses:

1. **Aggregation:** Averages the four agent scores (1-5 scale)
2. **Recommendation:** Converts aggregate score to BUY/HOLD/SELL
3. **Consensus Analysis:** Identifies where agents agree/disagree
4. **Risk Assessment:** Flags concerns (weak cash flow, high debt, declining growth)
5. **Confidence Scoring:** Adjusts confidence based on agent agreement

## Usage

### Standard Coordinator (Python-only)

Analyzes stocks using agent scores and basic synthesis:

```bash
python coordinator.py INFY TCS RELIANCE
```

**Output Example:**
```
================================================================================
STOCK ANALYSIS REPORT: INFY
================================================================================

📈 AGGREGATE SCORE: 4.1/5.0
💡 RECOMMENDATION: 🟢 BUY
🎯 CONFIDENCE: 85%

🤝 CONSENSUS: 3 agents agree on overall assessment
⚡ DISAGREEMENT: Growth outlook vs. valuation have different views

⚠️  RISK LEVEL: 🟡 LOW - Monitor closely

📊 AGENT SCORES:
   Financial Ratios    4.1 ████████░░
   Earnings & Growth   4.3 ████████░░
   Cash Flow           3.9 ███████░░░
   Valuation           4.0 ████████░░
```

### Claude-Enhanced Coordinator (with Claude API)

Uses Claude to intelligently synthesize analyses with natural language reasoning:

```bash
python claude_coordinator.py INFY TCS RELIANCE
```

**Output Example:**
```
CLAUDE-SYNTHESIZED ANALYSIS: INFY

📈 AGGREGATE SCORE: 4.1/5.0
💡 RECOMMENDATION: Strong Buy - Growing profitability with reasonable valuation
🎯 CONFIDENCE: 88%

🤝 CONSENSUS:
   All agents agree on the company's strong fundamentals and sustainable
   profitability. Financial ratios and cash flow metrics are particularly strong.

⚠️  KEY CONCERNS:
   Slight overvaluation relative to sector peers. Monitor upcoming earnings
   for guidance on future growth rates.

💭 TOP INVESTMENT CONSIDERATIONS:
   1. Consistent 15%+ EPS growth over past 3 years
   2. Strong ROE above 20% indicates efficient capital deployment
   3. Positive free cash flow supports future dividends

🚨 RISK FACTORS:
   • Sector-level competition from both domestic and global players
   • Currency fluctuations impact (significant international revenue)
```

## Setup

### 1. Create .env file

```bash
cp .env.example .env
# Add your Anthropic API key if using claude_coordinator.py
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

**Key packages:**
- `yfinance` - Fetch stock data from Yahoo Finance / NSE
- `python-dotenv` - Load API keys from .env
- `anthropic` - Optional, only for claude_coordinator.py

### 3. Run analysis

```bash
# Standard coordinator (no API key needed)
python coordinator.py INFY

# Claude-enhanced (requires ANTHROPIC_API_KEY)
python claude_coordinator.py INFY TCS RELIANCE
```

## Files Structure

```
stock_analysis_agents/
├── coordinator.py           # Standard multi-agent orchestrator
├── claude_coordinator.py    # Claude API-enhanced coordinator
├── agents/                  # Specialized agent modules
│   ├── financial_ratios_agent.py
│   ├── earnings_growth_agent.py
│   ├── cash_flow_agent.py
│   └── valuation_agent.py
├── tools/
│   └── data_fetcher.py      # yfinance wrapper for fundamentals
└── .env.example             # Environment variable template
```

## Scoring System

All agents use a **1-5 scale** with 3 as neutral:

| Score | Interpretation |
|-------|-----------------|
| 4.5-5.0 | Excellent fundamentals |
| 3.5-4.4 | Good fundamentals |
| 2.5-3.4 | Average / Hold |
| 1.5-2.4 | Weak fundamentals |
| 1.0-1.4 | Poor fundamentals |

**Aggregate Score → Recommendation:**
- **≥4.0** → 🟢 BUY
- **3.5-3.9** → 🟡 BUY (with caution)
- **3.0-3.4** → 🔵 HOLD
- **2.5-2.9** → 🟠 SELL (with caution)
- **<2.5** → 🔴 SELL

## Example: Analyzing INFY

```bash
$ python coordinator.py INFY

📊 Analyzing INFY...

================================================================================
STOCK ANALYSIS REPORT: INFY
================================================================================

📈 AGGREGATE SCORE: 4.1/5.0
💡 RECOMMENDATION: 🟢 BUY
🎯 CONFIDENCE: 85%

🤝 CONSENSUS: 3 agents agree on overall assessment
⚡ DISAGREEMENT: Growth outlook vs. valuation have different views

⚠️  RISK LEVEL: 🟡 LOW - Monitor growth trends

📊 AGENT SCORES:
   Financial Ratios    4.1 ████████░░
   Earnings & Growth   4.3 ████████░░
   Cash Flow           3.9 ███████░░░
   Valuation           4.0 ████████░░

📋 DETAILED ANALYSES:

   Financial Ratios:
      Score: 4.1/5.0
      Strong ROE: 22.5% | Good profit margin: 14.2% | Low debt burden: D/E 0.45

   Earnings & Growth:
      Score: 4.3/5.0
      Strong revenue growth: 12.3% | Good earnings growth: 15.8% | Attractive valuation: PEG 1.1

   Cash Flow:
      Score: 3.9/5.0
      Positive free cash flow | Good FCF yield: 2.1% | High quality earnings (OCF > NI)

   Valuation:
      Score: 4.0/5.0
      Fair valuation: PE 24.5 (near market avg) | Growth expected: Forward PE < Trailing PE | Dividend support: 1.2% yield
```

## How Agents Work

Each agent:
1. Fetches fundamental data using `data_fetcher.py`
2. Calculates key metrics for their specialization
3. Applies scoring logic based on industry benchmarks and best practices
4. Returns a score (1-5) with detailed reasoning

**Example Flow for Financial Ratios Agent:**

```
Input: Symbol = "INFY"
  ↓
Fetch Data: ROE=22.5%, Margin=14.2%, D/E=0.45, ROA=8.1%
  ↓
Apply Scoring:
  • Strong ROE (22.5% > 20%) → +1.0
  • Good profit margin (14.2% > 10%) → +0.5
  • Low debt (D/E 0.45 < 0.5) → +0.5
  • Strong ROA (8.1% > 5%) → +0.5
  Base score (3.0) + Adjustments (2.5) = 5.5 → Clamped to 5.0
  ↓
Output: Score = 4.1/5.0, Analysis = "Strong ROE: 22.5% | Good profit margin: 14.2%..."
```

## Coordinator Logic

The coordinator:
1. **Calls all 4 agents** with the stock symbol
2. **Collects scores** and analyses from each agent
3. **Computes average score** and variance (to measure agreement)
4. **Generates recommendation** (higher score = BUY signal)
5. **Analyzes consensus** (which agents agree)
6. **Assesses risk** (using cash flow, leverage, growth trends)
7. **Adjusts confidence** based on how much agents agree (high variance = lower confidence)

## Extending the System

### Add a New Agent

Create `agents/custom_agent.py`:

```python
from tools.data_fetcher import get_stock_fundamentals

def analyze(symbol: str) -> dict:
    data = get_stock_fundamentals(symbol)
    
    score = 3.0
    analysis = "Your custom analysis here"
    
    return {
        'agent': 'Custom Agent Name',
        'symbol': symbol,
        'score': round(score, 2),
        'metrics': {...},
        'analysis': analysis
    }
```

Then add to coordinator:

```python
from agents import custom_agent
results['custom'] = custom_agent.analyze(symbol)
```

### Add New Data Sources

Extend `tools/data_fetcher.py` with:
- Different API sources (BSE, REST APIs)
- Fundamental indicators (EBITDA, Interest Coverage)
- Market data (VIX, sector performance)

## Limitations

- **NSE data via yfinance:** Limited fundamental data; some metrics may be None
- **Agent scoring:** Based on general thresholds; may not apply to all sectors
- **Single timestamp:** Analysis is point-in-time; trends require historical comparison
- **No insider data:** Uses only public market data

## Recommendations

1. **Use both coordinators:** Standard for quick analysis, Claude for in-depth synthesis
2. **Monitor disagreement:** If agents strongly disagree, do additional research
3. **Check cash flow first:** Most reliable indicator of financial health
4. **Combine with technical analysis:** Fundamentals + technicals provide better signals
5. **Regular reviews:** Re-analyze quarterly as companies release new results

## Future Enhancements

- [ ] Add technical analysis agent (support/resistance, moving averages)
- [ ] Add sentiment analysis agent (news, social media)
- [ ] Implement trend tracking over time (monthly snapshots)
- [ ] Add portfolio analysis (diversification, correlation)
- [ ] Multi-stock comparison (sector performance)
- [ ] Integration with Claude API tool use for real-time analysis
- [ ] Database storage for historical analysis results
