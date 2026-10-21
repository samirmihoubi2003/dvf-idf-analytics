"""Exécution en CI quand TEST_DATABASE_URL est disponible."""

import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"),
    reason="TEST_DATABASE_URL non défini : test PostgreSQL réservé à la CI / Docker",
)


def test_grain_transaction_et_calcul_prix_m2():
    import psycopg

    from dvf_etl.extract import sha256_file
    from dvf_etl.load import load_file

    db_url = os.environ["TEST_DATABASE_URL"]
    file = Path(__file__).parent / "fixtures" / "dvf_sample.csv"
    first = load_file(db_url, file, 2025, "75", sha256_file(file))
    second = load_file(db_url, file, 2025, "75", sha256_file(file))
    assert first == second == {
        "lignes_source": 8, "lignes_valides": 7, "transactions": 4
    }
    with psycopg.connect(db_url) as conn:
        rows = conn.execute(
            """SELECT id_mutation, valeur_fonciere, prix_m2, prix_m2_eligible
               FROM mart.fact_transaction
               WHERE source_year = 2025 AND source_department = '75'
               ORDER BY id_mutation"""
        ).fetchall()
    assert len(rows) == 4
    assert rows[0][1] == 300000  # pas 600000 : prix non multiplié par 2
    assert rows[0][2] == 6000
    assert rows[0][3] is True
    assert rows[1][2] == 5000
    assert rows[2][2] is None  # deux appartements : prix/m2 ambigu
    assert rows[3][2] is None  # surface manquante
