# cli.py
import argparse
import json
from pathlib import Path
from downloader import prepare_and_build
from logger_ import get_logger
from registry import register_package, list_installed
from deps import resolve_from_file

logger = get_logger("lfsmgr")

def cmd_build(args):
    meta_path = Path(args.meta)
    if not meta_path.exists():
        logger.error("Arquivo de metadados não encontrado")
        return
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    try:
        info = prepare_and_build(meta)
        # registrar (installed_files ainda vazio)
        register_package(info["name"], info["version"], meta, installed_files=[], log_path=logger.log_path)
        logger.info(f"Pacote {info['name']} ver {info['version']} construído e registrado")
    except Exception as e:
        logger.error(f"Erro: {e}")

def cmd_list(args):
    installed = list_installed()
    if not installed:
        print("Nenhum pacote instalado registrado.")
        return
    for name, data in installed.items():
        print(f"- {name} {data.get('version')} (instalado em {data.get('installed_at')})")

def cmd_resolve(args):
    meta_path = Path(args.meta)
    if not meta_path.exists():
        logger.error("Arquivo de metadados não encontrado")
        return
    metas_dir = Path("metas")
    if not metas_dir.exists():
        logger.error("Diretório 'metas/' não encontrado.")
        return
    try:
        order = resolve_from_file(meta_path, metas_dir)
        print("Ordem de build (dependências resolvidas):")
        for p in order:
            print(" -", p)
    except Exception as e:
        logger.error(f"Erro ao resolver dependências: {e}")

def main():
    p = argparse.ArgumentParser(prog="lfsmgr")
    sub = p.add_subparsers(dest="cmd")

    # build
    b = sub.add_parser("build", help="baixar+compilar+instalar a partir de arquivo de metadados")
    b.add_argument("meta", help="arquivo JSON de metadados")
    b.set_defaults(func=cmd_build)

    # list
    l = sub.add_parser("list", help="listar pacotes registrados")
    l.set_defaults(func=cmd_list)

    # resolve (abreviação: res)
    r = sub.add_parser("resolve", aliases=["res"], help="resolver dependências recursivas")
    r.add_argument("meta", help="arquivo JSON inicial")
    r.set_defaults(func=cmd_resolve)

    args = p.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        p.print_help()

if __name__ == "__main__":
    main()
