# logger_.py
import logging
from pathlib import Path
from datetime import datetime

LOG_DIR = Path.home() / ".lfsmgr" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def get_logger(name: str):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    # console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(ch)
    # file handler (per-run)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fh = logging.FileHandler(LOG_DIR / f"{name}-{timestamp}.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(fh)
    # attach path for callers
    logger.log_path = fh.baseFilename
    return logger
