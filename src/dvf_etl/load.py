
"""Gold : chargement atomique DVF avec mesure du temps par étape."""

import csv
import gzip
import logging
from pathlib import Path
from time import perf_counter

import psycopg

from dvf_etl.config import ROOT
from dvf_etl.transform import parse_record

logger = logging.getLogger(__name__)

COPY_COLUMNS = (
    "source_year, source_department, id_mutation, numero_disposition, "
    "date_mutation, nature_mutation, valeur_fonciere, code_commune, "
    "nom_commune, type_local, surface_reelle_bati"
)

STAGING_DDL = """
CREATE TEMP TABLE staging_file (
    source_year INTEGER NOT NULL,
    source_department TEXT NOT NULL,
    id_mutation TEXT NOT NULL,
    numero_disposition TEXT NOT NULL,
    date_mutation DATE NOT NULL,
    nature_mutation TEXT,
    valeur_fonciere NUMERIC,
    code_commune TEXT NOT NULL,
    nom_commune TEXT NOT NULL,
    type_local TEXT,
    surface_reelle_bati NUMERIC
) ON COMMIT DROP;
"""


def load_file(
    database_url: str, source: Path, year: int, department: str, checksum: str
) -> dict[str, int]:
    """Charge un fichier dans une seule transaction, avec chronométrage SQL."""
    total, valid = 0, 0
    started = perf_counter()
    previous = started

    def report(stage: str) -> None:
        nonlocal previous
        current = perf_counter()
        logger.info(
            "PERF | %-25s | etape=%.3fs | cumul=%.3fs",
            stage,
            current - previous,
            current - started,
        )
        previous = current

    with psycopg.connect(database_url) as connection:
        report("connexion PostgreSQL")
        with connection.cursor() as cursor:
            cursor.execute((ROOT / "sql" / "schema.sql").read_text(encoding="utf-8"))
            report("schema SQL")

            cursor.execute(STAGING_DDL)
            report("table staging")

            opener = gzip.open if source.suffix == ".gz" else open
            with opener(source, mode="rt", encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                required = {
                    "id_mutation", "numero_disposition", "date_mutation", "nature_mutation",
                    "valeur_fonciere", "code_commune", "nom_commune", "type_local",
                    "surface_reelle_bati",
                }
                missing = required - set(reader.fieldnames or [])
                if missing:
                    raise ValueError(f"Colonnes manquantes dans {source}: {sorted(missing)}")

                with cursor.copy(f"COPY staging_file ({COPY_COLUMNS}) FROM STDIN") as copy:
                    for raw in reader:
                        total += 1
                        record = parse_record(raw, year, department)
                        if record is not None:
                            copy.write_row(record.to_copy_row())
                            valid += 1
            report("lecture CSV et COPY")

            cursor.execute("""
                CREATE INDEX idx_staging_mutation
                ON staging_file(source_year, source_department, id_mutation, numero_disposition)
            """)
            report("index staging")

            sql = (ROOT / "sql" / "load.sql").read_text(encoding="utf-8")
            before_delete, after_delete = sql.split("DELETE FROM mart.fact_transaction", 1)
            delete_statement, insert_statement = after_delete.split(
                "INSERT INTO mart.fact_transaction", 1
            )

            cursor.execute(before_delete)
            report("aggregation et dimensions")

            cursor.execute(
                "DELETE FROM mart.fact_transaction" + delete_statement,
                (year, department),
            )
            report("suppression ancien lot")

            cursor.execute("INSERT INTO mart.fact_transaction" + insert_statement)
            report("insertion transactions")

            cursor.execute(
                "SELECT COUNT(*) FROM mart.fact_transaction "
                "WHERE source_year = %s AND source_department = %s",
                (year, department),
            )
            loaded = cursor.fetchone()[0]
            report("comptage transactions")

            cursor.execute((ROOT / "sql" / "views.sql").read_text(encoding="utf-8"))
            report("vues Power BI")

            cursor.execute(
                """INSERT INTO mart.etl_runs
                   (source_year, source_department, source_sha256,
                    lignes_source, lignes_valides, transactions_chargees)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (year, department, checksum, total, valid, loaded),
            )
            report("historique ETL")

    report("commit et fermeture")
    return {"lignes_source": total, "lignes_valides": valid, "transactions": loaded}
