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
    return haikuModel

def log(text):
    try:
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        with open("history.log", "a", encoding="utf-8") as fh:
            fh.write(f"[{ts}] :: {text}\n")
    except Exception:
        pass

def main():
    client = getClient()
    if (not client):
        print("Invalid API Key. Please check your .env file.")
        return

    haikuModel = getModel(client, 'haiku')
    if (not haikuModel):
        print("Could not find the 'haiku' model. Please check your model availability.")
        return

    # Interactive chat loop with history
    history = []
    print("Interactive chat (type '/exit' to quit)")
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

        # Adding role: user for the user's message before sending to the model
        history.append({"role": "user", "content": user_text})
        # log the user's message
        log(f"USER: {user_text}")

        try:
            message = client.messages.create(
                model=haikuModel,
                max_tokens=300,
                messages=history
            )

            # Robust extraction of assistant text from different SDK shapes
            try:
                content = getattr(message, "content", None)
            except Exception:
                content = None

            if content is None:
                print("No assistant text returned; raw response:\n", message)
            else:
                assistant_text = None
                try:
                    assistant_text = content[0].text
                except Exception:
                    try:
                        assistant_text = content[0].message
                    except Exception:
                        assistant_text = str(content[0])

                print("AI Assistant: ", assistant_text)
                # Add the assistant's response to history with assistant role
                history.append({"role": "assistant", "content": assistant_text})
                log(f"AI ASSISTANT: {assistant_text}")

        except Exception as e:
            print("Error calling the model:", e)
            break

if __name__ == "__main__":
    main()