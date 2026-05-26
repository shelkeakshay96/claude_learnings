from dotenv import load_dotenv
import os
from datetime import datetime, timezone, timedelta
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document

load_dotenv()

# Global list to store dynamically fetched symbols
SYMBOLS = []

def fetch_nse_symbols() -> list:
    """Load a curated list of large-cap and mid-cap NSE symbols.

    This function is intentionally simple and deterministic for demos.
    """
    global SYMBOLS
    if SYMBOLS:
        return SYMBOLS

    large_mid_cap_symbols = [
        "RELIANCE", "INFY", "TCS", "HDFC", "HDFC BANK", "ICICIBANK", "BAJAJ-AUTO", "MARUTI",
        "HINDUSTAN UNILEVER", "BAJAJ FINSERV", "BHARTI AIRTEL", "ITC", "AXIS BANK", "SUNPHARMA",
        "WIPRO", "DMART", "NESTLEIND", "POWERGRID", "GAIL", "COAL INDIA", "IOC", "ONGC", "SBIN",
        "HDFCLIFE", "ICICIPRULI", "TECHM", "TITAN", "HCLTECH", "CIPLA", "LUPIN", "DIVISLAB",
        "BRITANNIA", "LT", "EICHERMOT", "ASHOKLEY", "JSWSTEEL", "NTPC", "TATAELXSI", "LTTS",
        "CUMMINSIND", "TORNTPHARM", "M&M", "SIEMENS", "INDIGO", "INDUSIND", "SAIL", "CADILAHC",
        "VEDL", "NMDC", "PIDILITIND", "ADANIPORTS", "ADANIGREEN", "COFORGE"
    ]
    SYMBOLS = sorted(list(set(large_mid_cap_symbols)))
    return SYMBOLS


class StockSymbolCompleter(Completer):
    """Completer that only suggests symbols after an '@' character."""

    def get_completions(self, document: Document, complete_event):
        text = document.text_before_cursor
        if '@' not in text:
            return
        last_at_index = text.rfind('@')
        prefix = text[last_at_index + 1:]
        for symbol in SYMBOLS:
            if symbol.upper().startswith(prefix.upper()):
                yield Completion(symbol, start_position=-len(prefix), display=symbol)


def log(text: str) -> None:
    try:
        ts = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        with open('history.log', 'a', encoding='utf-8') as fh:
            fh.write(f'[{ts}] :: {text}\n')
    except Exception:
        pass


def add_user_message(messages: list, text: str) -> None:
    messages.append({"role": "user", "content": text})


def add_assistant_message(messages: list, content) -> None:
    messages.append({"role": "assistant", "content": content})


def validate_key(api_key: str):
    if api_key is None or api_key.strip() == "":
        return False
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
    except Exception:
        return False
    return client


def get_client():
    from dotenv import load_dotenv
    load_dotenv()
    client = validate_key(os.getenv("ANTHROPIC_API_KEY"))
    return client


def get_model(client, model_name: str):
    haikuModel = ''
    try:
        models = client.models.list()
        for model in models.data:
            if model_name in model.id.lower():
                haikuModel = model.id
    except Exception:
        return None
    return haikuModel
