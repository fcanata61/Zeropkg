# registry.py
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

DB_PATH = Path.home() / ".lfsmgr" / "db.json"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def _load() -> Dict[str, Any]:
    if not DB_PATH.exists():
        return {"installed": {}}
    return json.loads(DB_PATH.read_text(encoding="utf-8"))

def _save(db: Dict[str, Any]) -> None:
    DB_PATH.write_text(json.dumps(db, indent=2), encoding="utf-8")

def register_package(name: str, version: str, metadata: dict, installed_files: list, log_path: str):
    db = _load()
    db["installed"][name] = {
        "version": version,
        "metadata": metadata,
        "installed_files": installed_files,
        "log": log_path,
        "installed_at": datetime.utcnow().isoformat() + "Z"
    }
    _save(db)

def unregister_package(name: str):
    db = _load()
    if name in db["installed"]:
        del db["installed"][name]
        _save(db)
        return True
    return False

def list_installed():
    db = _load()
    return db["installed"]

def get_package(name: str):
    db = _load()
    return db["installed"].get(name)
