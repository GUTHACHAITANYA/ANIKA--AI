import logging
import sys
from datetime import datetime

# Configure UTF-8 encoding on standard streams to avoid Windows charmap issues
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

class AnikaFormatter(logging.Formatter):
    """Custom structured log formatter with clean timestamp and tags."""
    
    LEVEL_COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        color = self.LEVEL_COLORS.get(record.levelname, self.RESET)
        module = record.name
        message = record.getMessage()
        return f"[{timestamp}] {color}[{record.levelname:<7}]{self.RESET} [{module}] {message}"

def get_logger(name: str = "anika") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(AnikaFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger

logger = get_logger("anika.app")
