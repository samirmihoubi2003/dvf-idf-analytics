"""Entrée : python -m dvf_etl.cli [options]."""

import argparse
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from dvf_etl.config import DATA_DIR, DEPARTEMENTS_IDF
from dvf_etl.extract import download_dvf, sha256_file
from dvf_etl.load import load_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline DVF / Île-de-France")
    parser.add_argument("--year", type=int, default=2025, choices=range(2021, 2026))
    parser.add_argument("--departments", nargs="+", default=["75"])
    parser.add_argument("--local-file", type=Path, help="CSV ou CSV.GZ local (test hors ligne)")
    parser.add_argument("--force-download", action="store_true")
    args = parser.parse_args()

    for department in args.departments:
        if department not in DEPARTEMENTS_IDF:
            parser.error(f"Département francilien invalide : {department}")
    if args.local_file and len(args.departments) != 1:
        parser.error("--local-file nécessite exactement un département")

    load_dotenv()
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        parser.error("DATABASE_URL est absent : copier .env.example vers .env")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    for department in args.departments:
        if args.local_file:
            source = args.local_file
            if not source.is_file():
                parser.error(f"Fichier absent : {source}")
        else:
            source = DATA_DIR / str(args.year) / f"{department}.csv.gz"
            logging.info("Extraction %s / %s", args.year, department)
            download_dvf(args.year, department, source, args.force_download)
        logging.info("Traitement %s", source)
        stats = load_file(database_url, source, args.year, department, sha256_file(source))
        logging.info("Résultat %s/%s : %s", args.year, department, stats)


if __name__ == "__main__":
    main()
