"""Fetch financial fundamentals for NSE stocks using yfinance."""

import yfinance as yf
from datetime import datetime


def get_stock_fundamentals(symbol: str) -> dict:
    """Fetch fundamental data for an NSE stock symbol."""
    try:
        # NSE symbols in yfinance need .NS suffix
        if not symbol.endswith('.NS'):
            ticker = f"{symbol}.NS"
        else:
            ticker = symbol

        stock = yf.Ticker(ticker)
        info = stock.info

        fundamentals = {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'price': info.get('currentPrice', 0),
            'market_cap': info.get('marketCap', 0),

            # Profitability ratios
            'pe_ratio': info.get('trailingPE', 0),
            'pb_ratio': info.get('priceToBook', 0),
            'profit_margin': info.get('profitMargins', 0),
            'roe': info.get('returnOnEquity', 0),
            'roa': info.get('returnOnAssets', 0),

            # Growth metrics
            'revenue_growth': info.get('revenueGrowth', 0),
            'earnings_growth': info.get('earningsGrowth', 0),
            'forward_pe': info.get('forwardPE', 0),

            # Debt metrics
            'debt_to_equity': info.get('debtToEquity', 0),
            'current_ratio': info.get('currentRatio', 0),
            'quick_ratio': info.get('quickRatio', 0),

            # Cash flow & dividend
            'free_cash_flow': info.get('freeCashflow', 0),
            'operating_cash_flow': info.get('operatingCashflow', 0),
            'dividend_yield': info.get('dividendYield', 0),
            'payout_ratio': info.get('payoutRatio', 0),

            'last_updated': datetime.now().isoformat(),
        }

        return fundamentals

    except Exception as e:
        return {
            'symbol': symbol,
            'error': str(e),
            'last_updated': datetime.now().isoformat(),
        }


def get_historical_data(symbol: str, period: str = '1y') -> dict:
    """Get historical price data for trend analysis."""
    try:
        if not symbol.endswith('.NS'):
            ticker = f"{symbol}.NS"
        else:
            ticker = symbol

        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if len(hist) == 0:
            return {'error': 'No historical data found'}

        current_price = hist['Close'].iloc[-1]
        price_1m_ago = hist['Close'].iloc[-22] if len(hist) >= 22 else hist['Close'].iloc[0]
        price_3m_ago = hist['Close'].iloc[-66] if len(hist) >= 66 else hist['Close'].iloc[0]
        price_1y_ago = hist['Close'].iloc[0]

        return {
            'symbol': symbol,
            'current_price': current_price,
            '1m_return': ((current_price - price_1m_ago) / price_1m_ago * 100),
            '3m_return': ((current_price - price_3m_ago) / price_3m_ago * 100),
            '1y_return': ((current_price - price_1y_ago) / price_1y_ago * 100),
            '52w_high': hist['Close'].max(),
            '52w_low': hist['Close'].min(),
        }

    except Exception as e:
        return {'symbol': symbol, 'error': str(e)}
