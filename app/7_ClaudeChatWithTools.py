from dotenv import load_dotenv
import anthropic
import os
from datetime import datetime, timezone, timedelta
import yfinance as yf
import json
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
load_dotenv()

from dotenv import load_dotenv
import anthropic
import os
from datetime import datetime, timezone, timedelta
import yfinance as yf
import json
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
load_dotenv()

# Global list to store dynamically fetched symbols
SYMBOLS = []

def fetch_nse_symbols():
    """Fetch large-cap and mid-cap company symbols from NSE dynamically"""
    global SYMBOLS
    
    try:
        print("Fetching NSE large-cap and mid-cap companies...")
        
        # Curated list of large-cap and mid-cap companies from NSE
        large_mid_cap_symbols = [
            # Large Cap (NIFTY 50)
            "RELIANCE", "INFY", "TCS", "HDFC", "HDFC BANK", "ICICIBANK", "BAJAJ-AUTO", "MARUTI",
            "HINDUSTAN UNILEVER", "BAJAJ FINSERV", "BHARTI AIRTEL", "ITC", "AXIS BANK", "SUNPHARMA",
            "WIPRO", "DMART", "NESTLEIND", "POWERGRID", "GAIL", "COAL INDIA", "IOC", "ONGC", "SBIN",
            "HDFCLIFE", "ICICIPRULI", "TECHM", "TITAN", "HCLTECH", "CIPLA", "LUPIN", "DIVISLAB",
            "BRITANNIA", "LT", "EICHERMOT", "ASHOKLEY", "JSWSTEEL", "NTPC", "TATAELXSI", "LTTS",
            "CUMMINSIND", "TORNTPHARM", "M&M", "SIEMENS", "INDIGO", "INDUSIND", "SAIL", "CADILAHC",
            "VEDL", "NMDC", "PIDILITIND", "ADANIPORTS", "ADANIGREEN", "COFORGE",
            # Additional Mid-Cap companies
            "ADANIENSOL", "ADANITRANS", "APOLLOHOSP", "AUBANK", "AUROPHARMA", "BERGEPAINT", "BOSCHLTD",
            "BPCL", "CHOLAFIN", "DABUR", "FEDERALBNK", "FLAIRNG", "GICRE", "GMRINFRA", "GODREJ",
            "GODREJIND", "GRINDWELL", "GUJGASLTD", "HEXAWARE", "IDFCBANK", "IPCALAB", "JKCEMENT",
            "JSWENERGY", "KAJARIACER", "KALYANKJIL", "KPIT", "LICHSGFIN", "LINDEINDIA", "MAHSEAMLESS",
            "MAHSCOOTER", "MARKSANS", "MCLAREN", "MFSL", "MINDTREE", "MIRCHTRADE", "MPHASIS",
            "MSUMI", "NAVINFLUOR", "NYKAA", "PAGEIND", "PAYTM", "PHOENIXLTD", "PIIND", "POLICYBZR",
            "PRESTIGE", "PRICERITE", "RAMCOCEM", "RANBAXY", "RECLTD", "RELINFRA", "RPOWER", "SANOFI",
            "SBICARD", "SBILIFE", "SCROLL", "SECUREEE", "SEGIND", "SHRIRAMFIN", "SHYAMMET", "SKIPPER",
            "SOBHA", "SOLARINDS", "SONATSOFTW", "SPANDANA", "SPARC", "SPEC", "SPLPETRO", "SSWINFRA",
            "STARCEMENT", "STARPAPER", "STERLINGG", "STLTECH", "STRTECH", "SUPREMEIND", "SUVNSHARMA",
            "SUZLON", "SYNGENE", "TATACHEM", "TATACOFFEE", "TATACOMM", "TATAELXSI", "TATAINVEST",
            "TATAMETALI", "TATAMOTORS", "TATAPOWER", "TATASTEEL", "TATASTLBSL", "TETJPM", "TFCILTD",
            "THERMAXYLO", "TIMKEN", "TINPLATE", "TIPSOFTW", "TITAGARH", "TMETRY", "TORNTORX", "TORRENTPHARMA",
            "TRAFFIC", "TRANSASL", "TREEHOUSE", "TRIGYN", "TRITURBINE", "TSPL", "TTCHEM", "TTMDATA"
        ]
        
        # Remove duplicates and sort
        SYMBOLS = sorted(list(set(large_mid_cap_symbols)))
        print(f"Successfully loaded {len(SYMBOLS)} large-cap and mid-cap company symbols")
        return SYMBOLS
    except Exception as e:
        print(f"Error fetching NSE symbols: {e}")
        print("Using default symbol list...")
        # Fallback to default list if fetch fails
        SYMBOLS = [
            "RELIANCE", "INFY", "TCS", "HDFC", "HDFC BANK", "ICICIBANK", "BAJAJ-AUTO", "MARUTI",
            "HINDUSTAN UNILEVER", "BAJAJ FINSERV", "BHARTI AIRTEL", "ITC", "AXIS BANK", "SUNPHARMA",
            "WIPRO", "DMART", "NESTLEIND", "POWERGRID", "GAIL", "COAL INDIA", "IOC", "ONGC", "SBIN",
            "HDFCLIFE", "ICICIPRULI", "TECHM", "TITAN", "HCLTECH", "CIPLA", "LUPIN", "DIVISLAB",
            "BRITANNIA", "LT", "EICHERMOT", "ASHOKLEY", "JSWSTEEL", "NTPC", "TATAELXSI", "LTTS",
            "CUMMINSIND", "TORNTPHARM", "M&M", "SIEMENS", "INDIGO", "INDUSIND", "SAIL", "CADILAHC",
            "VEDL", "NMDC", "PIDILITIND", "ADANIPORTS", "ADANIGREEN", "COFORGE"
        ]
        return SYMBOLS

class StockSymbolCompleter(Completer):
    """Custom completer that shows dynamic large-cap and mid-cap symbols after @ symbol"""
    
    def get_completions(self, document: Document, complete_event):
        text = document.text_before_cursor
        
        # Check if @ exists in the text
        if '@' not in text:
            return
        
        # Get the text after the last @
        last_at_index = text.rfind('@')
        symbol_prefix = text[last_at_index + 1:]
        
        # Provide completions from dynamic SYMBOLS list
        # Match symbols that start with the prefix (case-insensitive)
        for symbol in SYMBOLS:
            if symbol.upper().startswith(symbol_prefix.upper()):
                # Calculate the completion text (what will replace the prefix)
                yield Completion(
                    symbol,
                    start_position=-len(symbol_prefix),
                    display=symbol,
                    display_meta="NSE Large-Cap/Mid-Cap"
                )

# Define the stock price tool
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
        "description": "Get trailing and forward PE ratios for a stock on NSE. Provide the stock symbol without .NS suffix.",
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
    }
]

def get_nse_stock_price(symbol: str) -> str:
    """Fetch stock price from NSE (National Stock Exchange of India)"""
    try:
        ticker_symbol = f"{symbol.upper()}.NS"
        stock = yf.Ticker(ticker_symbol)
        
        # Get the latest data
        data = stock.history(period="1d")
        
        if data.empty:
            return json.dumps({
                "error": f"Could not fetch data for symbol {symbol}. Please check if the symbol is valid.",
                "symbol": symbol
            })
        
        current_price = data['Close'].iloc[-1]
        # Get current time in IST (Indian Standard Time: UTC+5:30)
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
        ticker_symbol = f"{symbol.upper()}.NS"
        stock = yf.Ticker(ticker_symbol)
        info = stock.info if hasattr(stock, "info") else {}
        trailing_pe = info.get("trailingPE")
        forward_pe = info.get("forwardPE")
        return json.dumps({
            "symbol": symbol,
            "trailingPE": None if trailing_pe is None else round(float(trailing_pe), 2),
            "forwardPE": None if forward_pe is None else round(float(forward_pe), 2)
        })
    except Exception as e:
        return json.dumps({"error": f"Error fetching PE for {symbol}: {str(e)}"})


def process_tool_call(tool_name: str, tool_input: dict) -> str:
    """Process tool calls from Claude"""
    if tool_name == "get_nse_stock_price":
        return get_nse_stock_price(tool_input["symbol"])
    elif tool_name == "get_nse_pe_ratio":
        return get_nse_pe_ratio(tool_input["symbol"])
    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})

# Check if an Anthropic API key is valid without using message credits.
def validateKey(api_key):
    if api_key is None or api_key.strip() == "":
        return False

    try:
        client = anthropic.Anthropic(api_key=api_key)
    except anthropic.AuthenticationError:
        return False
    return client

def getClient():
    client = validateKey(os.getenv("ANTHROPIC_API_KEY"))
    if client:
        print("Valid API Key. Proceeding with the application...")
        return client
    else:
        return None

def getModel(client, model_name):
    haikuModel = ''
    try:
        models = client.models.list()
        for model in models.data:
            if model_name in model.id.lower():
                haikuModel = model.id
    except Exception as e:
        print(f"Error retrieving the '{model_name}' model: {e}")
        return None
    print(f"Using model: {haikuModel}")
    print('------------------------------------------')
    return haikuModel

def log(text):
    try:
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        with open("history.log", "a", encoding="utf-8") as fh:
            fh.write(f"[{ts}] :: {text}\n")
    except Exception:
        pass
    
def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)

def add_assistant_message(messages, content):
    # Handle both string and content block messages
    if isinstance(content, str):
        assistant_message = {"role": "assistant", "content": content}
    elif isinstance(content, list):
        assistant_message = {"role": "assistant", "content": content}
    else:
        assistant_message = {"role": "assistant", "content": content}
    messages.append(assistant_message)

def chat(messages, client, model, system_instruction=None):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": 0.1,
        "stream": False
    }
    if system_instruction:
        params["system"] = system_instruction
        
    message = client.messages.create(**params)
    if (message[0].text):
        print("AI Assistant: ", message[0].text, end="", flush=True)
    return message[0].text

def stream_linear_chat(messages, client, model, system_instruction=None):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": 0.1,
        "stream": True
    }
    if system_instruction:
        params["system"] = system_instruction
        
    stream = client.messages.create(**params)
    assistant_response = ''
    for event in stream:
        if event.type == "content_block_delta":
            content = event.delta.text
            print(content, end="")

            if content and len(content) > 0:
                assistant_response += content
    print()  # for newline after the assistant finishes responding
    return assistant_response

def stream_optimized_chat(messages, client, model, system_instruction=None):
    # stram using with
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": 0.1
    }
    if system_instruction:
        params["system"] = system_instruction

    # Calling with stram instead of create to get the context manager for better resource handling
    assistant_response = ''
    with client.messages.stream(**params) as stream:
        print("AI Assistant: ", end="")
        for event in stream.text_stream:
            print(event, end="")
    print()

    return stream.get_final_message().content[0].text

def chat_session(client, model):
    messages = []
    # Create a PromptSession with custom completer for @ symbols
    stock_completer = StockSymbolCompleter()
    prompt_session = PromptSession(completer=stock_completer)
    
    while True:
        try:
            # Use prompt_toolkit for input with autocomplete
            user_text = prompt_session.prompt("You > ")
        except EOFError:
            print("\nExiting chat.")
            break
        except KeyboardInterrupt:
            print("\n\nEnding the session. Good bye!")
            return
        
        if not user_text:
            continue
        if user_text.strip().lower() in ("/exit", "exit", "quit", "stop"):
            print("Exiting chat. Thank you for chatting!")
            break

        try:
            system_instruction = """
            You are a financial helper chatbot that can help users with their questions.
            You have access to a tool to get real-time stock prices from the Indian stock market (NSE).
            When a user asks about stock prices, use the get_nse_stock_price tool to fetch current prices.
            Be helpful, concise and precise in your answers.
            """

            add_user_message(messages, user_text)
            
            # Keep making requests until we get a final text response (not tool_use)
            while True:
                assistant_response = ""
                
                # Use streaming for real-time response
                print("AI Assistant: ", end="", flush=True)
                with client.messages.stream(
                    model=model,
                    max_tokens=1000,
                    messages=messages,
                    tools=tools,
                    temperature=0.1,
                    system=system_instruction
                ) as stream:
                    # Stream text chunks in real-time
                    for text in stream.text_stream:
                        print(text, end="", flush=True)
                        assistant_response += text
                    
                    # Get the final message to check for tool_use
                    response = stream.get_final_message()
                
                print()  # New line after streaming
                
                # Check if we need to handle tool calls
                if response.stop_reason == "tool_use":
                    # Find and execute tool calls
                    for block in response.content:
                        if block.type == "tool_use":
                            # Process the tool call
                            tool_result = process_tool_call(block.name, block.input)
                            
                            # Add assistant's tool use response to messages
                            messages.append({
                                "role": "assistant",
                                "content": response.content
                            })
                            
                            # Add tool result to messages
                            messages.append({
                                "role": "user",
                                "content": [
                                    {
                                        "type": "tool_result",
                                        "tool_use_id": block.id,
                                        "content": tool_result
                                    }
                                ]
                            })
                            break
                else:
                    # Final text response - add to messages and break
                    if assistant_response:
                        add_assistant_message(messages, assistant_response)
                    
                    log(f"USER: {user_text}")
                    log(f"AI ASSISTANT: {assistant_response}")
                    break
            
        except Exception as e:
            print("Error calling the model:", e)

def main():
    # Fetch large-cap and mid-cap company symbols dynamically
    fetch_nse_symbols()
    
    client = getClient()
    if (not client):
        print("Invalid API Key. Please check your .env file.")
        return

    haikuModel = getModel(client, 'haiku')
    if (not haikuModel):
        print("Could not find the 'haiku' model. Please check your model availability.")
        return

    try:
        chat_session(client, haikuModel)
    except KeyboardInterrupt:
        print("\n\nEnding the session. Good bye!")

if __name__ == "__main__":
    main()