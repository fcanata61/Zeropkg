# logger_.py
"""
Sistema de logging unificado do lfsmgr.
Cada logger escreve tanto na tela (stdout) quanto em um arquivo dentro de ~/.lfsmgr/logs/.
"""

import logging
from pathlib import Path
from datetime import datetime

LOG_DIR = Path.home() / ".lfsmgr" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    """Cria e retorna um logger com saída em console e arquivo."""

    logger = logging.getLogger(name)
    if logger.handlers:
        # já configurado
        return logger

    logger.setLevel(logging.DEBUG)

    # formato de log
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # saída para console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # saída para arquivo (um por dia)
    logfile = LOG_DIR / f"{datetime.utcnow().date()}_{name}.log"
    fh = logging.FileHandler(logfile, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # guardamos caminho do log no próprio objeto (útil no registry)
    logger.log_path = str(logfile)

    return logger
