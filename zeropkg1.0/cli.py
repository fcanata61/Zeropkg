# cli.py
"""
CLI do lfsmgr — gerenciador minimalista de builds a partir de source.
Comandos: build, list, resolve (alias: res), remove (alias: rm).
"""

import argparse
import json
from pathlib import Path
from logger_ import get_logger
from downloader import prepare_and_build
from registry import register_package, list_installed, unregister_package, get_package
from deps import resolve_from_file

logger = get_logger("lfsmgr")


def cmd_build(args):
    meta_path = Path(args.meta)
    if not meta_path.exists():
        logger.error("Arquivo de metadados não encontrado: %s", meta_path)
        return
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    try:
        info = prepare_and_build(meta)
        # prepare_and_build deve retornar dict com keys: name, version, installed_files (lista relativa ao PREFIX)
        installed_files = info.get("installed_files", [])
        register_package(
            info["name"],
            info["version"],
            meta,
            installed_files=installed_files,
            log_path=logger.log_path,
        )
        logger.info("Pacote %s ver %s construído e registrado", info["name"], info["version"])
    except Exception as e:
        logger.error("Erro no build: %s", e)


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
        logger.error("Arquivo de metadados não encontrado: %s", meta_path)
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
        logger.error("Erro ao resolver dependências: %s", e)


def cmd_remove(args):
    name = args.name
    pkg = get_package(name)
    if not pkg:
        logger.error("Pacote %s não encontrado no registro.", name)
        return

    files = pkg.get("installed_files", [])
    if not files:
        logger.warning("Pacote %s não tinha arquivos registrados.", name)
    else:
        # import PREFIX aqui para evitar problemas de import circular
        try:
            from downloader import PREFIX
        except Exception as e:
            logger.error("Erro ao importar PREFIX do downloader: %s", e)
            return

        removed = 0
        for rel in files:
            relp = Path(rel)
            if relp.is_absolute():
                # segurança: pulamos entradas absolutas (esperamos caminhos relativos ao PREFIX)
                logger.warning("Pulando caminho absoluto não gerenciado: %s", relp)
                continue
            fpath = PREFIX / relp
            if not fpath.exists():
                logger.debug("Arquivo não existe (pulando): %s", fpath)
                continue
            try:
                if fpath.is_file() or fpath.is_symlink():
                    fpath.unlink()
                    removed += 1
                elif fpath.is_dir():
                    # tenta remover diretório caso esteja vazio
                    try:
                        fpath.rmdir()
                        removed += 1
                    except OSError:
                        logger.debug("Diretório não vazio (pulando): %s", fpath)
            except Exception as e:
                logger.error("Falha ao remover %s: %s", fpath, e)

        # tentar limpar diretórios pai (somente dentro do PREFIX)
        parent_dirs = sorted(
            { (PREFIX / Path(rel)).parent for rel in files if not Path(rel).is_absolute() },
            reverse=True
        )
        for d in parent_dirs:
            try:
                d.rmdir()
            except Exception:
                # ignora se não vazio ou outra falha
                pass

        logger.info("Removidos %d arquivos do pacote %s", removed, name)

    # por fim, remove do registro
    unregister_package(name)
    logger.info("Pacote %s removido do registro.", name)


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

    # resolve (alias: res)
    r = sub.add_parser("resolve", aliases=["res"], help="resolver dependências recursivas")
    r.add_argument("meta", help="arquivo JSON inicial")
    r.set_defaults(func=cmd_resolve)

    # remove (alias: rm)
    rm = sub.add_parser("remove", aliases=["rm"], help="remover pacote do registro (e arquivos)")
    rm.add_argument("name", help="nome do pacote a remover")
    rm.set_defaults(func=cmd_remove)

    args = p.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
