import sys
from pathlib import Path
from loguru import logger

# Ensure logs directory exists at project root
LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configure logger: stdout (INFO) + rotating file (DEBUG)
logger.remove()  # Remove default handler
logger.add(sys.stdout, level="INFO", colorize=True)
logger.add(LOG_DIR / "app.log", level="DEBUG", rotation="10 MB", retention="7 days", format="{time} | {level} | {message}")

def get_logger(name: str = "app"):
    """Return a logger bound to the supplied module name.
    Usage example:
        from .logging_config import get_logger
        logger = get_logger(__name__)
    """
    return logger.bind(module=name)
