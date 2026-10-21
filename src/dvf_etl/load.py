"""Gold : COPY PostgreSQL, contrôle du grain et chargement atomique."""

import csv
import gzip
from pathlib import Path

import psycopg

from dvf_etl.config import ROOT
from dvf_etl.transform import parse_record

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
    """Une transaction DB par fichier : rollback complet si une étape échoue."""
    total, valid = 0, 0
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute((ROOT / "sql" / "schema.sql").read_text(encoding="utf-8"))
            cursor.execute(STAGING_DDL)
            opener = gzip.open if source.suffix == ".gz" else open
            with opener(source, mode="rt", encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                required = {
                    "id_mutation", "numero_disposition", "date_mutation", "nature_mutation",
                    "valeur_fonciere", "code_commune", "nom_commune", "type_local",
                    "surface_reelle_bati"
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
            cursor.execute("""
                CREATE INDEX idx_staging_mutation
                ON staging_file(source_year, source_department, id_mutation, numero_disposition)
            """)
            # Le fichier SQL contient un DELETE paramétré ; exécuter chaque
            # instruction séparément sans interpolation des paramètres.
            sql = (ROOT / "sql" / "load.sql").read_text(encoding="utf-8")
            before_delete, after_delete = sql.split("DELETE FROM mart.fact_transaction", 1)
            cursor.execute(before_delete)
            delete_statement, insert_statement = after_delete.split("INSERT INTO mart.fact_transaction", 1)
            cursor.execute("DELETE FROM mart.fact_transaction" + delete_statement, (year, department))
            cursor.execute("INSERT INTO mart.fact_transaction" + insert_statement)
            cursor.execute(
                "SELECT COUNT(*) FROM mart.fact_transaction "
                "WHERE source_year = %s AND source_department = %s",
                (year, department),
            )
            loaded = cursor.fetchone()[0]
            cursor.execute((ROOT / "sql" / "views.sql").read_text(encoding="utf-8"))
            cursor.execute(
                """INSERT INTO mart.etl_runs
                   (source_year, source_department, source_sha256,
                    lignes_source, lignes_valides, transactions_chargees)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (year, department, checksum, total, valid, loaded),
            )
    return {"lignes_source": total, "lignes_valides": valid, "transactions": loaded}
