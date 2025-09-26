# deps.py
import json
from pathlib import Path
from typing import Dict, List, Set

class DependencyError(Exception):
    pass

def load_meta(pkgname: str, metas_dir: Path) -> dict:
    """Carrega arquivo JSON de metadados para um pacote."""
    path = metas_dir / f"{pkgname}.json"
    if not path.exists():
        raise DependencyError(f"Metadados não encontrados para {pkgname} em {path}")
    return json.loads(path.read_text(encoding="utf-8"))

def resolve_deps(pkgmeta: dict, metas_dir: Path, seen: Set[str]=None, stack: Set[str]=None) -> List[str]:
    """
    Resolve dependências recursivamente e retorna ordem de build.
    Usa DFS + detecção de ciclos.
    """
    if seen is None:
        seen = set()
    if stack is None:
        stack = set()

    order: List[str] = []

    name = pkgmeta["name"]
    if name in stack:
        raise DependencyError(f"Ciclo detectado em dependências: {name}")
    if name in seen:
        return []

    stack.add(name)
    deps = pkgmeta.get("depends", [])
    for dep in deps:
        depname = dep.split(">=")[0].strip()  # simplificação: ignora versão
        depmeta = load_meta(depname, metas_dir)
        order += resolve_deps(depmeta, metas_dir, seen, stack)

    stack.remove(name)
    if name not in seen:
        seen.add(name)
        order.append(name)
    return order

def resolve_from_file(meta_file: Path, metas_dir: Path) -> List[str]:
    """Resolve dependências a partir de um arquivo JSON inicial."""
    pkgmeta = json.loads(meta_file.read_text(encoding="utf-8"))
    return resolve_deps(pkgmeta, metas_dir)
