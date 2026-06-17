import logging
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] :: %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%SZ'
)

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('history.log')
file_handler.setFormatter(logging.Formatter('[%(asctime)s] :: %(message)s', datefmt='%Y-%m-%dT%H:%M:%SZ'))
logger.addHandler(file_handler)


def log(text: str) -> None:
    """Log text to history.log with ISO timestamp."""
    try:
        ts = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        with open('history.log', 'a', encoding='utf-8') as fh:
            fh.write(f'[{ts}] :: {text}\n')
    except Exception:
        pass
