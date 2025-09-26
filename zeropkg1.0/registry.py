# registry.py
"""
Registro de pacotes do lfsmgr.
Armazena informações em ~/.lfsmgr/registry.json
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from logger_ import get_logger

logger = get_logger("registry")

REGISTRY_DIR = Path.home() / ".lfsmgr"
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)

REGISTRY_FILE = REGISTRY_DIR / "registry.json"


def _load_registry() -> Dict[str, Any]:
    """Carrega registro JSON ou retorna {} se não existir."""
    if not REGISTRY_FILE.exists():
        return {}
    try:
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error("Falha ao ler registry.json: %s", e)
        return {}


def _save_registry(data: Dict[str, Any]) -> None:
    """Salva dicionário em registry.json."""
    try:
        REGISTRY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as e:
        logger.error("Falha ao salvar registry.json: %s", e)


def register_package(
    name: str,
    version: str,
    meta: Dict[str, Any],
    installed_files: list,
    log_path: Optional[str] = None,
) -> None:
    """Adiciona/atualiza entrada no registro."""
    reg = _load_registry()
    reg[name] = {
        "name": name,
        "version": version,
        "meta": meta,
        "installed_files": installed_files,
        "log": str(log_path) if log_path else None,
        "installed_at": datetime.utcnow().isoformat() + "Z",
    }
    _save_registry(reg)
    logger.info("Registrado pacote %s (%s)", name, version)


def unregister_package(name: str) -> bool:
    """Remove entrada do registro. Retorna True se existia."""
    reg = _load_registry()
    if name in reg:
        del reg[name]
        _save_registry(reg)
        logger.info("Removido pacote %s do registro", name)
        return True
    else:
        logger.warning("Pacote %s não estava no registro", name)
        return False


def list_installed() -> Dict[str, Any]:
    """Retorna dicionário de pacotes instalados."""
    return _load_registry()


def get_package(name: str) -> Optional[Dict[str, Any]]:
    """Retorna info de um pacote específico ou None."""
    reg = _load_registry()
    return reg.get(name)
