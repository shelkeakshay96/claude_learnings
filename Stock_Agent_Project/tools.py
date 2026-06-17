import yfinance as yf
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta

# Current NIFTY 50 constituents (NSE symbols, without the .NS suffix).
# This is the universe used for self-analysis / "top picks" screening.
NIFTY50_SYMBOLS = [
    "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK",
    "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BEL", "BPCL",
    "BHARTIARTL", "BRITANNIA", "CIPLA", "COALINDIA", "DRREDDY",
    "EICHERMOT", "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE",
    "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK", "ITC",
    "INDUSINDBK", "INFY", "JSWSTEEL", "KOTAKBANK", "LT",
    "M&M", "MARUTI", "NTPC", "NESTLEIND", "ONGC",
    "POWERGRID", "RELIANCE", "SBILIFE", "SHRIRAMFIN", "SBIN",
    "SUNPHARMA", "TCS", "TATACONSUM", "TATAMOTORS", "TATASTEEL",
    "TECHM", "TITAN", "TRENT", "ULTRACEMCO", "WIPRO",
]


# Define the tools exposed to the model
tools = [
    {
        "name": "get_nse_stock_price",
        "description": "Get the current price of a stock from NSE (National Stock Exchange of India). Provide the stock symbol without .NS suffix (e.g., 'RELIANCE', 'INFY', 'TCS'). Returns the current stock price in INR.",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock symbol from NSE (e.g., RELIANCE, INFY, TCS, HDFC, WIPRO)"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_nse_pe_ratio",
        "description": "Get trailing and forward PE ratios for a stock on NSE. Provide the stock symbol without .NS suffix. Use this for a quick PE-only question; for a full fundamental picture use get_fundamental_analysis instead.",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock symbol from NSE (e.g., RELIANCE, INFY, TCS)"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_fundamental_analysis",
        "description": (
            "Get a comprehensive set of fundamental metrics for a single NSE stock: "
            "valuation (PE, forward PE, PEG, price-to-book, market cap), profitability "
            "(ROE, ROA, profit/operating/gross margins), growth (revenue & earnings growth), "
            "financial health (debt-to-equity, current ratio, total debt, total cash), "
            "cash flow (free cash flow, operating cash flow), and dividends (yield, payout). "
            "Use this to answer 'fundamental analysis of X' or any deep question about a single company. "
            "Provide the symbol without the .NS suffix."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock symbol from NSE (e.g., INFY, COFORGE, RELIANCE)"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_nifty50_symbols",
        "description": "Return the list of NIFTY 50 stock symbols. Call this first when the user asks for top picks 'from NIFTY50' or 'among NIFTY 50 stocks', then pass the symbols to screen_nse_stocks.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "screen_nse_stocks",
        "description": (
            "Fetch key fundamental metrics for a list of NSE stocks in one call so they can be "
            "compared and ranked. Returns, per stock: market cap, trailing PE, price-to-book, ROE, "
            "debt-to-equity, profit margin, revenue growth, free cash flow, operating cash flow and "
            "dividend yield. Use this to answer 'top N stocks with best fundamentals / strong cash flow' "
            "type questions. Pass symbols without the .NS suffix."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of NSE symbols to screen, e.g. ['INFY', 'TCS', 'WIPRO']"
                }
            },
            "required": ["symbols"]
        }
    }
]


# ----------------------------- helpers ----------------------------- #

def _round(value, ndigits=2):
    """Round a numeric value, returning None for missing/invalid input."""
    if value is None:
        return None
    try:
        return round(float(value), ndigits)
    except (TypeError, ValueError):
        return None


def _to_pct(value, ndigits=2):
    """Convert a fraction (0.25) to a percentage (25.0)."""
    if value is None:
        return None
    try:
        return round(float(value) * 100, ndigits)
    except (TypeError, ValueError):
        return None


def _to_crore(value, ndigits=2):
    """Convert an absolute INR figure to crores (1 crore = 10,000,000)."""
    if value is None:
        return None
    try:
        return round(float(value) / 1e7, ndigits)
    except (TypeError, ValueError):
        return None


def _dividend_yield_pct(info):
    """Compute dividend yield as a percentage.

    yfinance reports `dividendYield` inconsistently across versions (sometimes a
    fraction, sometimes already a percentage), so derive it from the dividend
    rate and price when possible for a reliable number.
    """
    rate = info.get("dividendRate") or info.get("trailingAnnualDividendRate")
    price = (
        info.get("currentPrice")
        or info.get("regularMarketPrice")
        or info.get("previousClose")
    )
    if rate and price:
        try:
            return round(float(rate) / float(price) * 100, 2)
        except (TypeError, ValueError, ZeroDivisionError):
            pass
    # Fall back to the raw field, normalising an obvious fraction to a percentage.
    dy = info.get("dividendYield")
    if dy is None:
        return None
    try:
        dy = float(dy)
    except (TypeError, ValueError):
        return None
    return round(dy * 100, 2) if dy < 1 else round(dy, 2)


def _get_info(symbol):
    """Fetch the yfinance info dict for an NSE symbol (raises on failure)."""
    ticker_symbol = f"{symbol.upper()}.NS"
    stock = yf.Ticker(ticker_symbol)
    info = stock.info if hasattr(stock, "info") else {}
    return info or {}


# ----------------------------- tools ----------------------------- #

def get_nse_stock_price(symbol: str) -> str:
    """Fetch stock price from NSE (National Stock Exchange of India)."""
    try:
        ticker_symbol = f"{symbol.upper()}.NS"
        stock = yf.Ticker(ticker_symbol)
        data = stock.history(period="1d")

        if data.empty:
            return json.dumps({
                "error": f"Could not fetch data for symbol {symbol}. Please check if the symbol is valid.",
                "symbol": symbol
            })

        current_price = data['Close'].iloc[-1]
        ist = timezone(timedelta(hours=5, minutes=30))
        current_time = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
        return json.dumps({
            "symbol": symbol,
            "price": round(float(current_price), 2),
            "currency": "INR",
            "date": current_time,
            "message": f"Stock: {symbol} (NSE) | Current Price: ₹{current_price:.2f} | Time: {current_time} IST"
        })
    except Exception as e:
        return json.dumps({
            "error": f"Error fetching stock price for {symbol}: {str(e)}",
            "symbol": symbol
        })


def get_nse_pe_ratio(symbol: str) -> str:
    """Fetch trailing and forward PE ratios for an NSE stock using yfinance."""
    try:
        info = _get_info(symbol)
        return json.dumps({
            "symbol": symbol,
            "trailingPE": _round(info.get("trailingPE")),
            "forwardPE": _round(info.get("forwardPE"))
        })
    except Exception as e:
        return json.dumps({"error": f"Error fetching PE for {symbol}: {str(e)}"})


def get_fundamental_analysis(symbol: str) -> str:
    """Fetch a comprehensive set of fundamental metrics for a single NSE stock."""
    try:
        info = _get_info(symbol)
        if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
            return json.dumps({
                "error": f"Could not fetch fundamentals for {symbol}. Please check the symbol.",
                "symbol": symbol
            })

        return json.dumps({
            "symbol": symbol,
            "name": info.get("longName") or info.get("shortName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "currency": "INR",
            "valuation": {
                "market_cap_cr": _to_crore(info.get("marketCap")),
                "trailing_pe": _round(info.get("trailingPE")),
                "forward_pe": _round(info.get("forwardPE")),
                "peg_ratio": _round(info.get("pegRatio")),
                "price_to_book": _round(info.get("priceToBook")),
                "enterprise_value_cr": _to_crore(info.get("enterpriseValue")),
            },
            "profitability": {
                "roe_pct": _to_pct(info.get("returnOnEquity")),
                "roa_pct": _to_pct(info.get("returnOnAssets")),
                "profit_margin_pct": _to_pct(info.get("profitMargins")),
                "operating_margin_pct": _to_pct(info.get("operatingMargins")),
                "gross_margin_pct": _to_pct(info.get("grossMargins")),
            },
            "growth": {
                "revenue_growth_pct": _to_pct(info.get("revenueGrowth")),
                "earnings_growth_pct": _to_pct(info.get("earningsGrowth")),
                "earnings_qtr_growth_pct": _to_pct(info.get("earningsQuarterlyGrowth")),
            },
            "financial_health": {
                "debt_to_equity": _round(info.get("debtToEquity")),
                "current_ratio": _round(info.get("currentRatio")),
                "quick_ratio": _round(info.get("quickRatio")),
                "total_debt_cr": _to_crore(info.get("totalDebt")),
                "total_cash_cr": _to_crore(info.get("totalCash")),
            },
            "cash_flow": {
                "free_cash_flow_cr": _to_crore(info.get("freeCashflow")),
                "operating_cash_flow_cr": _to_crore(info.get("operatingCashflow")),
            },
            "dividends": {
                "dividend_yield_pct": _dividend_yield_pct(info),
                "payout_ratio_pct": _to_pct(info.get("payoutRatio")),
            },
            "per_share": {
                "trailing_eps": _round(info.get("trailingEps")),
                "forward_eps": _round(info.get("forwardEps")),
                "book_value": _round(info.get("bookValue")),
            },
            "price": {
                "current": _round(info.get("currentPrice") or info.get("regularMarketPrice")),
                "fifty_two_week_high": _round(info.get("fiftyTwoWeekHigh")),
                "fifty_two_week_low": _round(info.get("fiftyTwoWeekLow")),
                "beta": _round(info.get("beta")),
            },
        })
    except Exception as e:
        return json.dumps({"error": f"Error fetching fundamentals for {symbol}: {str(e)}", "symbol": symbol})


def get_nifty50_symbols() -> str:
    """Return the list of NIFTY 50 constituent symbols."""
    return json.dumps({"count": len(NIFTY50_SYMBOLS), "symbols": NIFTY50_SYMBOLS})


def _compact_metrics(symbol: str) -> dict:
    """Fetch a compact, comparison-friendly metric set for one symbol."""
    try:
        info = _get_info(symbol)
        if not info:
            return {"symbol": symbol, "error": "no data"}
        return {
            "symbol": symbol,
            "name": info.get("longName") or info.get("shortName"),
            "sector": info.get("sector"),
            "market_cap_cr": _to_crore(info.get("marketCap")),
            "trailing_pe": _round(info.get("trailingPE")),
            "price_to_book": _round(info.get("priceToBook")),
            "roe_pct": _to_pct(info.get("returnOnEquity")),
            "debt_to_equity": _round(info.get("debtToEquity")),
            "profit_margin_pct": _to_pct(info.get("profitMargins")),
            "revenue_growth_pct": _to_pct(info.get("revenueGrowth")),
            "free_cash_flow_cr": _to_crore(info.get("freeCashflow")),
            "operating_cash_flow_cr": _to_crore(info.get("operatingCashflow")),
            "dividend_yield_pct": _dividend_yield_pct(info),
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}


def screen_nse_stocks(symbols: list) -> str:
    """Fetch key fundamentals for many NSE stocks in parallel for ranking."""
    if not symbols:
        return json.dumps({"error": "No symbols provided."})
    try:
        # Parallelise the per-stock network calls; yfinance .info is the bottleneck.
        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(_compact_metrics, symbols))
        return json.dumps({"count": len(results), "stocks": results})
    except Exception as e:
        return json.dumps({"error": f"Error screening stocks: {str(e)}"})


def process_tool_call(tool_name: str, tool_input: dict) -> str:
    """Process tool calls from Claude."""
    if tool_name == "get_nse_stock_price":
        return get_nse_stock_price(tool_input["symbol"])
    elif tool_name == "get_nse_pe_ratio":
        return get_nse_pe_ratio(tool_input["symbol"])
    elif tool_name == "get_fundamental_analysis":
        return get_fundamental_analysis(tool_input["symbol"])
    elif tool_name == "get_nifty50_symbols":
        return get_nifty50_symbols()
    elif tool_name == "screen_nse_stocks":
        return screen_nse_stocks(tool_input["symbols"])
    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
