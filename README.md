# Hello Claude

A Claude API tutorials

Prerequisites
- Python 3

Setup

1. Create a virtual environment
```bash
python3 -m venv .venv
```
Creates an isolated Python environment named `.venv` so project dependencies don't affect the system Python.

2. Activate the virtual environment
```bash
source .venv/bin/activate
```
Activates the `.venv` environment so subsequent `pip` installs and `python` runs use the environment's interpreter and packages.

3. Upgrade `pip`
```bash
python -m pip install --upgrade pip
```
Ensures the package installer is up-to-date to avoid installation issues with newer wheels or packages.

4. Install project dependencies
```bash
pip install python-dotenv anthropic
```
- `python-dotenv`: loads environment variables from a `.env` file.
- `anthropic`: (optional) SDK used to interact with Anthropic APIs if the script requires it. Adjust packages as needed.

Run

Run the script with:
```bash
python app/4_ClaudeChatbot.py
```

Notes
- The script is located next to this README: hello_world.py

Optional: to leave the virtual environment, run `deactivate`.
