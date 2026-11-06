"""Test de regression : les prix symboliques ne sont pas des prix/m2 de marche."""

import csv
import os
from decimal import Decimal

import psycopg
import pytest
from psycopg.conninfo import conninfo_to_dict

from dvf_etl.extract import sha256_file
from dvf_etl.load import load_file


@pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"),
    reason="TEST_DATABASE_URL non defini",
)
def test_prix_symboliques_exclus_du_prix_m2(tmp_path):
    db_url = os.environ["TEST_DATABASE_URL"]
    if conninfo_to_dict(db_url).get("dbname") != "dvf_test":
        pytest.fail("TEST_DATABASE_URL doit cibler exclusivement dvf_test")

    fichier = tmp_path / "prix_symboliques.csv"
    colonnes = [
        "id_mutation", "date_mutation", "numero_disposition",
        "nature_mutation", "valeur_fonciere", "code_commune",
        "nom_commune", "code_departement", "type_local",
        "surface_reelle_bati",
    ]
    valeurs = [
        [
            "2024-900001", "2024-01-10", "000001", "Vente", "1",
            "75056", "Paris", "75", "Appartement", "230",
        ],
        [
            "2024-900002", "2024-01-11", "000001", "Vente", "0.15",
            "75056", "Paris", "75", "Maison", "46",
        ],
        [
            "2024-900003", "2024-01-12", "000001", "Vente", "300000",
            "75056", "Paris", "75", "Appartement", "50",
        ],
    ]
    with fichier.open("w", newline="", encoding="utf-8") as flux:
        writer = csv.writer(flux)
        writer.writerow(colonnes)
        writer.writerows(valeurs)

    resultat = load_file(db_url, fichier, 2024, "75", sha256_file(fichier))
    resultat_second = load_file(db_url, fichier, 2024, "75", sha256_file(fichier))
    assert resultat == resultat_second == {
        "lignes_source": 3, "lignes_valides": 3, "transactions": 3,
    }

    with psycopg.connect(db_url) as connection:
        lignes = connection.execute(
            """SELECT id_mutation, valeur_fonciere, surface_bati,
                      prix_m2, prix_m2_eligible
               FROM mart.fact_transaction
               WHERE source_year = 2024 AND source_department = '75'
               ORDER BY id_mutation"""
        ).fetchall()

    assert len(lignes) == 3
    assert lignes[0][1] == Decimal("1.00")
    assert lignes[0][2] == Decimal("230.00")
    assert lignes[0][3] is None
    assert lignes[0][4] is False

    assert lignes[1][1] == Decimal("0.15")
    assert lignes[1][3] is None
    assert lignes[1][4] is False

    assert lignes[2][1] == Decimal("300000.00")
    assert lignes[2][3] == Decimal("6000.00")
    assert lignes[2][4] is True
