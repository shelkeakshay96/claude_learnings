from dotenv import load_dotenv
import anthropic
import os
import json
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

def chat(messages, client, model, system_instruction=None, stop_sequences=[]):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": 1.0,
        "stream": False
    }
    if system_instruction:
        params["system"] = system_instruction
        
    if stop_sequences:
        params["stop_sequences"] = stop_sequences
        
    response = client.messages.create(**params)
    print("AI Assistant: ", response.content[0].text, end="", flush=True)
    return response.content[0].text

def generate_dataset(client, model):
    prompt = """
Generate an evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects, each representing task that requires Python, JSON, or a Regex to complete.

Example output:
```json
[
  {
    "task": "Description of task",
  },
  ...additional
]
```

* Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a single regex
* Focus on tasks that do not require writing much code

Please generate 3 objects.
"""
    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```json")
    text = chat(messages, client, model, stop_sequences=["```"])
    return json.loads(text)

def main():
    client = getClient()
    if (not client):
        print("Invalid API Key. Please check your .env file.")
        return

    haikuModel = getModel(client, 'haiku')
    if (not haikuModel):
        print("Could not find the 'haiku' model. Please check your model availability.")
        return

    # Generate a dataset using claude
    dataset = generate_dataset(client, haikuModel)
    print(dataset)
    
    # Save a dataset into  json
    with open('dataset.json', 'w') as f:
        json.dump(dataset, f, indent=2)
        print('Datset stored into the file successfully!')

if __name__ == "__main__":
    main()