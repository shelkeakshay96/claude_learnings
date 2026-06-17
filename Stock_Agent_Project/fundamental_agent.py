from dotenv import load_dotenv
from prompt_toolkit import PromptSession

from utils import (
    fetch_nse_symbols,
    StockSymbolCompleter,
    add_user_message,
    add_assistant_message,
    get_client,
    get_model,
)

from tools import (
    tools,
    process_tool_call,
)

from logger import log

load_dotenv()


SYSTEM_INSTRUCTION = """
You are an equity research assistant specialising in the Indian stock market (NSE).
You help users with the FUNDAMENTAL analysis of stocks.

You can do two kinds of work:

1. Single-stock analysis — when the user asks about one company
   (e.g. "What is the PE ratio of Coforge?", "Fundamental analysis of Infosys").
   - For a quick PE-only question, use get_nse_pe_ratio.
   - For anything deeper, use get_fundamental_analysis to pull valuation,
     profitability, growth, financial health, cash flow and dividend metrics,
     then explain what the numbers mean in plain language.

2. Screening / top picks — when the user asks for the best stocks by some
   fundamental criteria (e.g. "Top 5 NIFTY50 stocks with the best fundamentals
   and strong cash flow").
   - If the universe is NIFTY 50, call get_nifty50_symbols first to get the list.
   - Then call screen_nse_stocks with those symbols to fetch comparable metrics
     in one shot.
   - Rank the stocks against the user's stated criteria and present the top N.

Guidelines:
- Always base your analysis on the tool data, not memory. Stock data changes daily.
- When you recommend or rank stocks, give the SPECIFIC numbers (PE, ROE,
  debt-to-equity, free cash flow, etc.) that justify each pick.
- Note when a metric is missing (some companies, especially banks/financials,
  don't report certain ratios) instead of guessing.
- All monetary figures from the tools are in INR; "_cr" means crores.
- Be concise and well-structured. Prefer short tables or bullet lists.
- End any buy/sell-style discussion with a brief reminder that this is
  educational information, not financial advice.
"""


def chat_session(client, model):
    """Run an interactive fundamental-analysis chat session."""
    messages = []
    stock_completer = StockSymbolCompleter()
    prompt_session = PromptSession(completer=stock_completer)

    while True:
        try:
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
            add_user_message(messages, user_text)

            # Agentic loop: keep calling the model until it stops requesting tools.
            while True:
                assistant_response = ""

                print("AI Assistant: ", end="", flush=True)
                with client.messages.stream(
                    model=model,
                    max_tokens=2000,
                    messages=messages,
                    tools=tools,
                    temperature=0.1,
                    system=SYSTEM_INSTRUCTION,
                ) as stream:
                    for text in stream.text_stream:
                        print(text, end="", flush=True)
                        assistant_response += text

                    response = stream.get_final_message()

                print()

                if response.stop_reason == "tool_use":
                    # Serialize the assistant turn (text + tool_use blocks) so it
                    # can be replayed back to the API on the next request.
                    content_blocks = [
                        {
                            "type": "text",
                            "text": block.text,
                        } if block.type == "text" else {
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        }
                        for block in response.content
                    ]
                    messages.append({"role": "assistant", "content": content_blocks})

                    # Execute every requested tool and return one result per call.
                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            print(f"  [calling {block.name} {block.input}]", flush=True)
                            result = process_tool_call(block.name, block.input)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result,
                            })

                    messages.append({"role": "user", "content": tool_results})
                    # Loop again so the model can use the tool results.
                else:
                    if assistant_response:
                        add_assistant_message(messages, assistant_response)

                    log(f"USER: {user_text}")
                    log(f"AI ASSISTANT: {assistant_response}")
                    break

        except Exception as e:
            print("Error calling the model:", e)


def main():
    """Initialize and run the fundamental-analysis agent."""
    fetch_nse_symbols()

    client = get_client()
    if not client:
        print("Invalid API Key. Please check your .env file.")
        return

    model = get_model(client, 'haiku')
    if not model:
        print("Could not find the 'haiku' model. Please check your model availability.")
        return

    print("Fundamental Analysis Agent (NSE). Ask about a stock or request top picks.")
    print("Examples:")
    print("  - What is the PE ratio of Coforge?")
    print("  - What is the fundamental analysis of Infosys?")
    print("  - Give me top 5 NIFTY50 stocks with the best fundamentals and strong cash flow")
    print("Type 'exit' to quit.\n")

    try:
        chat_session(client, model)
    except KeyboardInterrupt:
        print("\n\nEnding the session. Good bye!")


if __name__ == "__main__":
    main()
