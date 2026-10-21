"""Configuration métier du pipeline DVF Île-de-France."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "raw"
DEPARTEMENTS_IDF = ("75", "77", "78", "91", "92", "93", "94", "95")
DATASET_URL = (
    "https://files.data.gouv.fr/geo-dvf/latest/csv/"
    "{year}/departements/{department}.csv.gz"
)
