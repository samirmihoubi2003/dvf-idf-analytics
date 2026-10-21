"""Silver : validation et conversion prudente d'une ligne DVF.

Les clés de mutation sont volontairement conservées en texte.
Le dédoublonnage DES TRANSACTIONS est réalisé en SQL, pas ici :
plusieurs lignes représentent parfois une seule mutation.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class RawRecord:
    source_year: int
    source_department: str
    id_mutation: str
    numero_disposition: str
    date_mutation: date
    nature_mutation: str
    valeur_fonciere: Decimal | None
    code_commune: str
    nom_commune: str
    type_local: str | None
    surface_reelle_bati: Decimal | None

    def to_copy_row(self) -> tuple:
        return (
            self.source_year,
            self.source_department,
            self.id_mutation,
            self.numero_disposition,
            self.date_mutation,
            self.nature_mutation,
            self.valeur_fonciere,
            self.code_commune,
            self.nom_commune,
            self.type_local,
            self.surface_reelle_bati,
        )


def decimal_or_none(value: str | None) -> Decimal | None:
    if not value or not value.strip():
        return None
    try:
        number = Decimal(value.strip().replace(",", "."))
        return number if number.is_finite() else None
    except (InvalidOperation, ValueError):
        return None


def parse_record(raw: dict, year: int, department: str) -> RawRecord | None:
    """Ignore seulement les lignes sans clé/date/commune valides.

    Le montant ou la surface absents restent NULL et seront traités en SQL.
    """
    try:
        mutation = (raw.get("id_mutation") or "").strip()
        disposition = (raw.get("numero_disposition") or "").strip()
        commune = (raw.get("code_commune") or "").strip()
        name = (raw.get("nom_commune") or "").strip()
        if not all((mutation, disposition, commune, name)):
            return None
        day = date.fromisoformat((raw.get("date_mutation") or "").strip())
        local = (raw.get("type_local") or "").strip() or None
        return RawRecord(
            source_year=year,
            source_department=department,
            id_mutation=mutation,
            numero_disposition=disposition,
            date_mutation=day,
            nature_mutation=(raw.get("nature_mutation") or "").strip(),
            valeur_fonciere=decimal_or_none(raw.get("valeur_fonciere")),
            code_commune=commune,
            nom_commune=name,
            type_local=local,
            surface_reelle_bati=decimal_or_none(raw.get("surface_reelle_bati")),
        )
    except (ValueError, TypeError):
        return None
