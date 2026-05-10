from dotenv import load_dotenv
import anthropic
import os
from datetime import datetime, timezone
load_dotenv()

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

def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
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
    print("AI Assistant: ", end="")
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
    while True:
        try:
            user_text = input("You: ")
        except EOFError:
            print("\nExiting chat.")
            break
        if not user_text:
            continue
        if user_text.strip().lower() in ("/exit", "exit", "quit", "stop"):
            print("Exiting chat. Thank you for chatting!")
            break

        try:
            system_instruction = """
            You are a human-like chatbot that helps users with their questions.
            Be helpful, concise and precise in your answers.
            """
            # system_instruction += """If not needed jsut answer the question without any extra information.
            # Always try to answer in a single sentence if possible."""

            add_user_message(messages, user_text)
            # assistant_response = chat(messages, client, model, system_instruction)
            # assistant_response = stream_linear_chat(messages, client, model, system_instruction)
            assistant_response = stream_optimized_chat(messages, client, model, system_instruction)
            add_assistant_message(messages, assistant_response)

            log(f"USER: {user_text}")
            log(f"AI ASSISTANT: {assistant_response}")
        except Exception as e:
            print("Error calling the model:", e)

def main():
    client = getClient()
    if (not client):
        print("Invalid API Key. Please check your .env file.")
        return

    haikuModel = getModel(client, 'haiku')
    if (not haikuModel):
        print("Could not find the 'haiku' model. Please check your model availability.")
        return

    chat_session(client, haikuModel)

if __name__ == "__main__":
    main()