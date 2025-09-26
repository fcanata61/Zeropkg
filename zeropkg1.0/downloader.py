# downloader.py
"""
Módulo responsável por baixar, extrair, compilar e instalar pacotes a partir
de metadados. Usa DESTDIR/PREFIX para isolar a instalação em ~/.lfsmgr/prefix.
"""

import os
import hashlib
import shutil
import subprocess
from pathlib import Path
import tarfile
import zipfile
import urllib.request
from typing import Optional, List
from logger_ import get_logger

WORKDIR = Path.cwd() / "build"
WORKDIR.mkdir(parents=True, exist_ok=True)

PREFIX = Path.home() / ".lfsmgr" / "prefix"
PREFIX.mkdir(parents=True, exist_ok=True)

logger = get_logger("downloader")


def download_url(url: str, dest: Path) -> None:
    """Baixa um arquivo de URL para dest."""
    logger.info("Baixando %s -> %s", url, dest)
    with urllib.request.urlopen(url) as resp:
        with open(dest, "wb") as f:
            shutil.copyfileobj(resp, f)
    logger.debug("Download completo")


def sha256_of_file(path: Path) -> str:
    """Calcula sha256 de um arquivo."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_checksum(path: Path, expected: Optional[str]) -> bool:
    """Verifica sha256 de path contra esperado."""
    if not expected:
        logger.warning("Nenhum checksum fornecido; pulando verificação")
        return True
    actual = sha256_of_file(path)
    ok = actual.lower() == expected.lower()
    if ok:
        logger.info("Checksum OK")
    else:
        logger.error("Checksum mismatch: esperado %s, obtido %s", expected, actual)
    return ok


def extract_archive(archive: Path, dest_dir: Path) -> Path:
    """Extrai tar.* ou zip em dest_dir. Retorna diretório raiz."""
    logger.info("Extraindo %s para %s", archive, dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    if tarfile.is_tarfile(archive):
        with tarfile.open(archive, "r:*") as tf:
            tf.extractall(dest_dir)
        members = [m for m in dest_dir.iterdir()]
        if len(members) == 1 and members[0].is_dir():
            return members[0]
        return dest_dir
    elif zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(dest_dir)
        members = [m for m in dest_dir.iterdir()]
        if len(members) == 1 and members[0].is_dir():
            return members[0]
        return dest_dir
    else:
        raise RuntimeError("Formato de arquivo não suportado para extração.")


def apply_patch(src_dir: Path, patch_file: Path) -> bool:
    """Aplica patch -p1 em src_dir."""
    logger.info("Aplicando patch %s em %s", patch_file, src_dir)
    if not patch_file.exists():
        logger.error("Patch não encontrado: %s", patch_file)
        return False
    proc = subprocess.run(
        ["patch", "-p1", "-i", str(patch_file)],
        cwd=src_dir,
        capture_output=True,
        text=True,
    )
    logger.debug(proc.stdout)
    if proc.returncode != 0:
        logger.error("patch falhou: %s", proc.stderr)
        return False
    return True


def run_steps(src_dir: Path, steps: list, env=None) -> bool:
    """Executa lista de comandos shell dentro de src_dir."""
    for step in steps:
        logger.info("Executando: %s", step)
        proc = subprocess.run(step, shell=True, cwd=src_dir, env=env)
        if proc.returncode != 0:
            logger.error("Comando falhou: %s (rc=%d)", step, proc.returncode)
            return False
    return True


def collect_files(prefix: Path) -> List[str]:
    """Lista todos os arquivos dentro do prefix como caminhos relativos."""
    files = []
    for path in prefix.rglob("*"):
        if path.is_file():
            rel = path.relative_to(prefix)
            files.append(str(rel))
    return files


def prepare_and_build(meta: dict) -> dict:
    """Pipeline: baixar → verificar → extrair → patch → configure/build/install → listar arquivos."""
    name = meta.get("name")
    version = meta.get("version", "0")
    src = meta["source"]["url"]
    sha = meta["source"].get("sha256")

    pkgdir = WORKDIR / f"{name}-{version}"
    pkgdir.mkdir(parents=True, exist_ok=True)
    archive = pkgdir / Path(src).name

    download_url(src, archive)
    if not verify_checksum(archive, sha):
        raise RuntimeError("Checksum inválido")

    src_root = extract_archive(archive, pkgdir / "src")

    # aplicar patches
    patches = meta.get("patches", [])
    for p in patches:
        ppath = Path(p)
        if not ppath.is_absolute():
            ppath = Path.cwd() / p
        ok = apply_patch(src_root, ppath)
        if not ok:
            raise RuntimeError(f"Falha ao aplicar patch {p}")

    # steps de build
    build = meta.get("build", {})
    configure = build.get("configure", [])
    build_steps = build.get("build", [])
    install_steps = build.get("install", [])

    env = os.environ.copy()
    env["DESTDIR"] = str(PREFIX)

    if configure and not run_steps(src_root, configure, env=env):
        raise RuntimeError("Falha no configure")
    if build_steps and not run_steps(src_root, build_steps, env=env):
        raise RuntimeError("Falha no build")
    if install_steps and not run_steps(src_root, install_steps, env=env):
        raise RuntimeError("Falha no install")

    installed_files = collect_files(PREFIX)

    return {
        "name": name,
        "version": version,
        "src_root": str(src_root),
        "installed_files": installed_files,
        }
