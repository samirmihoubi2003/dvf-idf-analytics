from decimal import Decimal

from dvf_etl.transform import decimal_or_none, parse_record


VALID = {
    "id_mutation": "2025-123456",
    "numero_disposition": "000001",
    "date_mutation": "2025-02-01",
    "nature_mutation": "Vente",
    "valeur_fonciere": "250000.50",
    "code_commune": "75056",
    "nom_commune": "Paris",
    "type_local": "Appartement",
    "surface_reelle_bati": "45",
}


def test_valeurs_decimales():
    assert decimal_or_none("123,45") == Decimal("123.45")
    assert decimal_or_none("NaN") is None
    assert decimal_or_none("") is None


def test_parse_conserve_les_codes_avec_zeros():
    row = parse_record(VALID, 2025, "75")
    assert row is not None
    assert row.numero_disposition == "000001"
    assert row.code_commune == "75056"
    assert row.valeur_fonciere == Decimal("250000.50")


def test_date_invalide_ignoree():
    assert parse_record({**VALID, "date_mutation": "2025-40-40"}, 2025, "75") is None


def test_surface_absente_ne_supprime_pas_la_transaction():
    row = parse_record({**VALID, "surface_reelle_bati": ""}, 2025, "75")
    assert row is not None
    assert row.surface_reelle_bati is None


def test_id_manquant_ignore():
    assert parse_record({**VALID, "id_mutation": ""}, 2025, "75") is None
