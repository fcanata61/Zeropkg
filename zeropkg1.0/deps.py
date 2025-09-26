# deps.py
"""
Resolução de dependências recursivas do lfsmgr.
Cada pacote pode ter um campo "depends" em seu arquivo de metadados (lista de nomes).
Exemplo:
{
  "name": "nano",
  "version": "7.2",
  "source": {...},
  "build": {...},
  "depends": ["ncurses", "gettext"]
}
"""

from typing import Dict, List, Set
from registry import list_installed
from logger_ import get_logger

logger = get_logger("deps")


def resolve_dependencies(meta: Dict) -> List[str]:
    """
    Recebe metadados de um pacote e retorna a lista de dependências faltantes
    (que ainda não estão instaladas).
    """
    installed = list_installed()
    deps = meta.get("depends", [])

    missing = [d for d in deps if d not in installed]
    if missing:
        logger.info("Dependências faltando: %s", ", ".join(missing))
    else:
        logger.info("Todas as dependências já estão satisfeitas.")

    return missing


def resolve_recursive(all_metas: Dict[str, Dict], target: str) -> List[str]:
    """
    Resolve dependências de forma recursiva.
    all_metas: dicionário {nome: metadados}
    target: nome do pacote a instalar

    Retorna lista ordenada de pacotes que precisam ser instalados,
    sem duplicatas e já na ordem correta.
    """
    resolved: List[str] = []
    visited: Set[str] = set()

    def dfs(pkg: str):
        if pkg in visited:
            return
        visited.add(pkg)

        meta = all_metas.get(pkg)
        if not meta:
            logger.error("Metadados do pacote %s não encontrados!", pkg)
            return

        for dep in meta.get("depends", []):
            dfs(dep)

        resolved.append(pkg)

    dfs(target)

    # Remove os já instalados
    installed = list_installed()
    final_list = [p for p in resolved if p not in installed]

    logger.info("Ordem de instalação calculada: %s", " → ".join(final_list))
    return final_list
