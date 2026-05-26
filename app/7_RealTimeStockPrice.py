from dotenv import load_dotenv
import anthropic
import os
import yfinance as yf
import json

load_dotenv()

# Define the stock price tool for Claude
tools = [
    {
        "name": "get_nse_stock_price",
        "description": "Get the current price of a stock from NSE (National Stock Exchange of India). Provide the stock symbol without .NS suffix.",
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
    }
]

def get_nse_stock_price(symbol: str) -> str:
    """Fetch stock price from NSE"""
    try:
        ticker_symbol = f"{symbol.upper()}.NS"
        stock = yf.Ticker(ticker_symbol)
        data = stock.history(period="1d")
        
        if data.empty:
            return json.dumps({"error": f"No data found for {symbol}"})
        
        current_price = data['Close'].iloc[-1]
        return json.dumps({
            "symbol": symbol,
            "price": round(float(current_price), 2),
            "currency": "INR"
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

def process_tool_call(tool_name: str, tool_input: dict) -> str:
    """Execute tool calls"""
    if tool_name == "get_nse_stock_price":
        return get_nse_stock_price(tool_input["symbol"])
    return json.dumps({"error": "Unknown tool"})

def chat(user_message: str):
    """Chat with Claude using tools"""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    messages = [{"role": "user", "content": user_message}]
    
    # Keep calling until we get a final response
    while True:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            tools=tools,
            messages=messages
        )
        
        # Check if Claude wants to use a tool
        if response.stop_reason == "tool_use":
            # Find the tool use block
            for block in response.content:
                if block.type == "tool_use":
                    print(f"🔧 Claude is calling tool: {block.name}")
                    print(f"   Input: {block.input}")
                    
                    # Execute the tool
                    tool_result = process_tool_call(block.name, block.input)
                    print(f"   Result: {tool_result}\n")
                    
                    # Add assistant response and tool result to messages
                    messages.append({"role": "assistant", "content": response.content})
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
            # Final response from Claude
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"✅ Claude: {block.text}")
            break

def main():
    print("=" * 60)
    print("Stock Price Tool Use Demo with Claude")
    print("=" * 60)
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input or user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            chat(user_input)
            print()
        except KeyboardInterrupt:
            print("\n\nEnding session. Good bye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()