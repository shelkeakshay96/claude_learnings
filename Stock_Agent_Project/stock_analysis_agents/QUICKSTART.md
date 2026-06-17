# Quick Start Guide

Get up and running with the Multi-Agent Stock Analysis System in 5 minutes.

## 1. Install Dependencies

```bash
cd stock_analysis_agents
pip install -r requirements.txt
```

## 2. Configure Environment (Optional for Claude)

If you want to use the Claude-enhanced coordinator:

```bash
cp .env.example .env
# Edit .env and add your API key
nano .env
```

## 3. Run Your First Analysis

### Option A: Standard Coordinator (No API Key Needed)

```bash
python coordinator.py INFY
```

Expected output:
```
📊 Analyzing INFY...

================================================================================
STOCK ANALYSIS REPORT: INFY
================================================================================

📈 AGGREGATE SCORE: 4.1/5.0
💡 RECOMMENDATION: 🟢 BUY
🎯 CONFIDENCE: 85%
...
```

### Option B: Claude-Enhanced Coordinator (With API Key)

```bash
python claude_coordinator.py INFY
```

Claude will provide in-depth synthesis and detailed reasoning.

## 4. Analyze Multiple Stocks

```bash
# Analyze 3 stocks with standard coordinator
python coordinator.py INFY TCS RELIANCE

# Or with Claude (slower, more insights)
python claude_coordinator.py INFY TCS RELIANCE HDFC WIPRO
```

## Common Use Cases

### Find Undervalued Stocks

Run analysis on a list and look for:
- Recommendation: **BUY** with high confidence
- Risk Level: **LOW**
- Valuation Agent Score: **≥4.0**

```bash
python coordinator.py INFY WIPRO TECHM HCLTECH
```

### Identify Risky Stocks

Look for:
- Cash Flow Agent Score: **<2.5**
- Disagreement between agents
- Risk Level: **HIGH**

These may need deeper investigation before investing.

### Compare Sector Peers

Analyze multiple companies in same sector:

```bash
# IT Sector
python coordinator.py INFY TCS WIPRO HCLTECH

# Banking Sector
python coordinator.py SBIN HDFC ICICIBANK AXISBANK

# Pharma Sector
python coordinator.py SUNPHARMA CIPLA LUPIN DIVISLAB
```

## Understanding the Output

### Recommendation Meanings

| Symbol | Meaning | Action |
|--------|---------|--------|
| 🟢 BUY | Strong fundamentals | Consider buying |
| 🟡 BUY (caution) | Good but watch risks | Buy with due diligence |
| 🔵 HOLD | Mixed fundamentals | Wait for clarity |
| 🟠 SELL (caution) | Weak but may recover | Reduce exposure |
| 🔴 SELL | Poor fundamentals | Avoid or exit |

### Confidence Levels

- **90%+** - All agents strongly agree
- **75-89%** - Most agents agree
- **60-74%** - Mixed signals, needs research
- **<60%** - Contradictory signals, be cautious

### Risk Levels

- 🟢 **LOW** - Fundamentals solid, safe to hold
- 🟡 **LOW (Monitor)** - One concern to watch
- 🟠 **MEDIUM** - Multiple red flags
- 🔴 **HIGH** - Significant concerns

## Agent Score Interpretation

Higher = Better

| Score | Status | Interpretation |
|-------|--------|-----------------|
| 4.5+ | ⭐⭐⭐ Excellent | Best in class |
| 4.0-4.4 | ⭐⭐ Good | Above average |
| 3.5-3.9 | ⭐ Fair | Average range |
| 3.0-3.4 | ⭐ Weak | Below average |
| <3.0 | ⚠️ Poor | Significant concerns |

## Typical Analysis Flow

1. **Start with aggregate score** - Quick assessment
2. **Check recommendation** - Action signal
3. **Review agent scores** - See which metrics are strong/weak
4. **Read detailed analysis** - Understand specific concerns
5. **Check consensus/disagreement** - Spot conflicting signals
6. **Assess risk level** - Decide if acceptable for your risk tolerance

## Tips for Better Results

### For Fundamental Analysis
- Analyze large-cap and mid-cap stocks (data quality better)
- Re-analyze quarterly after earnings releases
- Compare similar companies in same sector
- Track same stock over 6-12 months to see trends

### For Due Diligence
- Don't invest based solely on scores
- Read actual financial statements
- Check management quality and track record
- Look at industry trends and competition
- Understand business model

### For Beginners
1. Start with well-known large-cap stocks (INFY, TCS, RELIANCE)
2. Use standard coordinator first (simpler output)
3. Read the detailed analyses to understand metrics
4. Compare 2-3 similar companies side by side
5. Then analyze smaller/newer companies

## Troubleshooting

### No data available for symbol

```
❌ API Error: Symbol 'XYZ' not found
```

**Solution:** Check if symbol is listed on NSE. Try using correct symbol.

### API key error

```
❌ ANTHROPIC_API_KEY not set in .env file
```

**Solution:** Create .env file and add your API key, or use standard coordinator.py instead.

### yfinance rate limited

If you analyze too many stocks rapidly, yfinance may rate limit.

**Solution:** Add small delays between requests:

```python
import time
for symbol in ['INFY', 'TCS', 'WIPRO']:
    print(f"\nAnalyzing {symbol}...")
    time.sleep(2)  # 2 second delay
    report = analyze_stock(symbol)
```

## Next Steps

1. ✅ Run analysis on your favorite stock
2. ✅ Compare 3 stocks in same sector
3. ✅ Review detailed metrics and understand what they mean
4. ✅ Try Claude coordinator for deeper insights
5. ✅ Extend with your own agents (see README.md)

## Questions?

- Read the full [README.md](README.md) for detailed documentation
- Check individual agent files to understand scoring logic
- Review `data_fetcher.py` to see what metrics are available

## Disclaimer

This system provides analysis tools for educational and research purposes. It is not financial advice. Always do your own research and consult with a financial advisor before making investment decisions.
