# downloader.py
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
    logger.info(f"Baixando {url} -> {dest}")
    with urllib.request.urlopen(url) as resp:
        with open(dest, "wb") as f:
            shutil.copyfileobj(resp, f)
    logger.debug("Download completo")

def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def verify_checksum(path: Path, expected: Optional[str]) -> bool:
    if not expected:
        logger.warning("Nenhum checksum fornecido; pulando verificação")
        return True
    actual = sha256_of_file(path)
    ok = actual.lower() == expected.lower()
    if ok:
        logger.info("Checksum OK")
    else:
        logger.error(f"Checksum mismatch: esperado {expected}, obtido {actual}")
    return ok

def extract_archive(archive: Path, dest_dir: Path) -> Path:
    logger.info(f"Extraindo {archive} para {dest_dir}")
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
    logger.info(f"Aplicando patch {patch_file} em {src_dir}")
    if not patch_file.exists():
        logger.error("Patch não encontrado")
        return False
    proc = subprocess.run(["patch", "-p1", "-i", str(patch_file)], cwd=src_dir, capture_output=True, text=True)
    logger.debug(proc.stdout)
    if proc.returncode != 0:
        logger.error(f"patch falhou: {proc.stderr}")
        return False
    return True

def run_steps(src_dir: Path, steps: list, env=None) -> bool:
    for step in steps:
        logger.info(f"Executando: {step}")
        proc = subprocess.run(step, shell=True, cwd=src_dir, env=env)
        if proc.returncode != 0:
            logger.error(f"Comando falhou: {step} (rc={proc.returncode})")
            return False
    return True

def collect_files(destdir: Path) -> List[str]:
    """Lista todos os arquivos instalados em destdir relativo ao PREFIX."""
    files = []
    for path in destdir.rglob("*"):
        if path.is_file():
            rel = path.relative_to(PREFIX)
            files.append(str(rel))
    return files

def prepare_and_build(meta: dict) -> dict:
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
    patches = meta.get("patches", [])
    for p in patches:
        ppath = Path(p)
        if not ppath.is_absolute():
            ppath = Path.cwd() / p
        ok = apply_patch(src_root, ppath)
        if not ok:
            raise RuntimeError(f"Falha ao aplicar patch {p}")

    build = meta.get("build", {})
    configure = build.get("configure", [])
    build_steps = build.get("build", [])
    install_steps = build.get("install", [])

    env = {"DESTDIR": str(PREFIX), **dict(**os.environ)}

    if configure:
        if not run_steps(src_root, configure, env=env):
            raise RuntimeError("Falha no configure")
    if build_steps:
        if not run_steps(src_root, build_steps, env=env):
            raise RuntimeError("Falha no build")
    if install_steps:
        if not run_steps(src_root, install_steps, env=env):
            raise RuntimeError("Falha no install")

    installed_files = collect_files(PREFIX)
    return {"name": name, "version": version, "src_root": str(src_root), "installed_files": installed_files}
