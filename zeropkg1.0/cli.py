# cli.py
"""
Interface de linha de comando do lfsmgr.
Comandos principais:
  build <meta.json>      → instala pacote (com dependências recursivas)
  list                   → lista pacotes instalados
  remove <nome>          → remove pacote instalado
"""

import argparse
import json
from pathlib import Path

import downloader
import registry
from deps import resolve_recursive
from logger_ import get_logger

logger = get_logger("cli")


def load_meta(path: str) -> dict:
    """Carrega metadados JSON de um arquivo."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Arquivo {path} não encontrado")
    return json.loads(p.read_text(encoding="utf-8"))


def cmd_build(meta_path: str):
    """Instala pacote a partir de um arquivo de metadados + dependências."""
    meta = load_meta(meta_path)
    name = meta["name"]

    # carregar metadados adicionais (pasta ./metas)
    all_metas = {name: meta}
    metas_dir = Path("metas")
    if metas_dir.exists():
        for f in metas_dir.glob("*.json"):
            try:
                m = json.loads(f.read_text(encoding="utf-8"))
                all_metas[m["name"]] = m
            except Exception as e:
                logger.warning("Falha ao carregar %s: %s", f, e)

    # resolver ordem de instalação (dependências recursivas)
    order = resolve_recursive(all_metas, name)

    for pkg in order:
        logger.info(">>> Instalando %s...", pkg)
        downloader.build_package(all_metas[pkg])


def cmd_list():
    """Lista pacotes instalados."""
    installed = registry.list_installed()
    if not installed:
        print("Nenhum pacote instalado ainda.")
        return
    for name, info in installed.items():
        print(f"{name} {info['version']} (instalado em {info['installed_at']})")


def cmd_remove(name: str):
    """Remove pacote do sistema."""
    pkg = registry.get_package(name)
    if not pkg:
        print(f"Pacote {name} não está instalado.")
        return
    downloader.remove_package(pkg)
    registry.unregister_package(name)
    print(f"Pacote {name} removido.")


def main():
    parser = argparse.ArgumentParser(prog="lfsmgr", description="Gerenciador de pacotes LFS minimalista")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # build
    p_build = sub.add_parser("build", help="instala pacote a partir de metadados")
    p_build.add_argument("meta", help="arquivo JSON com metadados do pacote")

    # list
    sub.add_parser("list", help="lista pacotes instalados")

    # remove
    p_rm = sub.add_parser("remove", help="remove pacote instalado")
    p_rm.add_argument("name", help="nome do pacote a remover")

    args = parser.parse_args()

    if args.cmd == "build":
        cmd_build(args.meta)
    elif args.cmd == "list":
        cmd_list()
    elif args.cmd == "remove":
        cmd_remove(args.name)


if __name__ == "__main__":
    main()
