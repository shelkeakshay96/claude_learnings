from dotenv import load_dotenv
import anthropic
import os
load_dotenv()

# Check if an Anthropic API key is valid without using message credits.
def validateKey():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key is None or api_key.strip() == "":
        return False

    try:
        client = anthropic.Anthropic(api_key=api_key)
        client.models.list()
    except anthropic.AuthenticationError:
        return False
    return True

def main():
    if (not validateKey()):
        print("Invalid API Key. Please check your .env file.")
        return
    else:
        print("Valid API Key. Proceeding with the application...")

if __name__ == "__main__":
    main()