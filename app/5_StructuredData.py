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

def structured_chat(messages, client, model, system_instruction=None):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": 0.1,
        "stop_sequences": ['```'],  # Stop generation when the assistant finishes its response with a closing code block
        "stream": False
    }
    if system_instruction:
        params["system"] = system_instruction

    message = client.messages.create(**params)
    
    assistant_text = message.content[0].text
    print("AI Assistant: ", assistant_text)

    return assistant_text

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
            add_user_message(messages, user_text)
            add_assistant_message(messages, '```bash') # Adding a code block start to signal the assistant's response for better parsing
            assistant_structured_response = structured_chat(messages, client, model)
            log(f"USER: {user_text}")
            log(f"AI ASSISTANT: {assistant_structured_response}")
        except Exception as e:
            print("Error calling the model:", e)

def main():
    client = getClient()
    if (not client):
        print("Invalid API Key. Please check your .env file.")

    haikuModel = getModel(client, 'haiku')
    if (not haikuModel):
        print("Could not find the 'haiku' model. Please check your model availability.")

    chat_session(client, haikuModel)

if __name__ == "__main__":
    main()