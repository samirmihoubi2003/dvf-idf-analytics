"""Bronze : télécharger les sources CSV .gz sans les modifier."""

import hashlib
from pathlib import Path

import requests

from dvf_etl.config import DATASET_URL


def download_dvf(year: int, department: str, destination: Path, force: bool = False) -> Path:
    """Télécharge de façon atomique ; réutilise la copie locale sauf --force-download."""
    if destination.exists() and destination.stat().st_size > 0 and not force:
        return destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    url = DATASET_URL.format(year=year, department=department)
    temp = destination.with_suffix(destination.suffix + ".part")
    try:
        with requests.get(url, stream=True, timeout=(15, 180)) as response:
            response.raise_for_status()
            with temp.open("wb") as output:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        output.write(chunk)
        if temp.stat().st_size == 0:
            raise ValueError(f"Le téléchargement est vide : {url}")
        temp.replace(destination)
    finally:
        temp.unlink(missing_ok=True)
    return destination


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
