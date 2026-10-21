# DVF Île-de-France — Pipeline ETL & Dashboard Immobilier

**Python • PostgreSQL • Docker • GitHub Actions • Power BI / DAX**

Projet de portfolio Data Engineering / Business Intelligence : ingestion des
transactions immobilières DVF géolocalisées, contrôle qualité, consolidation
à la granularité transaction, entrepôt SQL en étoile et dashboard Power BI.

> Les données brutes et le fichier Power BI ne sont pas fournis : les données
> sont à récupérer depuis data.gouv.fr et le dashboard est à construire.

## Architecture

`DVF (CSV.GZ)` → `data/raw` → `Python (validation + PostgreSQL COPY)`
→ `mart.dim_date / dim_geo / dim_type_bien / fact_transaction`
→ `mart.v_powerbi_transactions` → `Power BI`

La table de faits est au grain **mutation + disposition + département + année**,
pas au grain ligne DVF. Voir [méthodologie](docs/methodologie.md).

## Installation sous Windows (PowerShell)

Prérequis : Git, Python 3.11+, Docker Desktop, VS Code (conseillé), Power BI Desktop.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
docker compose up -d db
```

## Test rapide avec 8 lignes d'exemple (sans accès à DVF)

```powershell
python -m dvf_etl.cli --year 2025 --departments 75 --local-file tests/fixtures/dvf_sample.csv
python -m pytest -q
```

Attendu : **8 lignes source**, **7 valides**, **4 transactions Vente**. Le
prix au m² de la mutation 2025-000001 vaut 6 000 €/m² malgré deux lignes DVF.

## Données réelles : commencer petit, puis élargir

```powershell
python -m dvf_etl.cli --year 2025 --departments 75
python -m dvf_etl.cli --year 2025 --departments 75 77 78 91 92 93 94 95
python -m dvf_etl.cli --year 2024 --departments 75 77 78 91 92 93 94 95
```

Le pipeline télécharge les sources dans `data/raw/<année>/<département>.csv.gz`.
On relance un lot sans doubler le nombre de transactions. Pour récupérer une
nouvelle publication : ajouter `--force-download`.

## Voir les résultats dans PostgreSQL

```powershell
docker compose exec db psql -U dvf -d dvf -c "SELECT * FROM mart.v_qualite ORDER BY source_year, source_department;"
```

## Power BI

Connecteur PostgreSQL → serveur `localhost:5433`, base `dvf` ;
utilisateur `dvf`, mot de passe local dans `docker-compose.yml`.
Importer la vue `mart.v_powerbi_transactions` et créer les mesures documentées
dans [mesures DAX](powerbi/mesures_dax.md).

## Git / branches recommandées

- `main` : version stable / présentation portfolio.
- `develop` : intégration après validation.
- `feature/etl-dvf` : téléchargement et nettoyage.
- `feature/data-warehouse` : tables, tests SQL et indicateurs.
- `feature/powerbi-dashboard` : dashboard et documentation.

Toujours créer une branche depuis `develop`, faire de petits commits cohérents,
pousser la branche, ouvrir une Pull Request vers `develop`, vérifier la CI,
puis fusionner. `develop` → `main` pour une livraison. Voir le
[guide Git pas-à-pas](docs/git-workflow.md) et la [feuille de route](docs/roadmap.md).

## Qualité et CI

`.github/workflows/ci.yml` lance Ruff, pytest et un test d'intégration avec
un vrai PostgreSQL sur chaque PR vers `develop` ou `main`. Le workflow
`manual-etl.yml` est optionnel : il nécessite un **PostgreSQL distant accessible**
ainsi qu'un secret GitHub `DVF_DATABASE_URL`. Les runners GitHub ne peuvent pas
accéder directement à `localhost` sur l'ordinateur personnel.

## Source et licence

Source : https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres-geolocalisees
Licence source : Licence Ouverte 2.0. Respecter les conditions de réutilisation
DVF, notamment ne pas permettre la réidentification ou l'indexation d'informations
à caractère personnel.

Les chiffres du CV devront provenir de la table `mart.etl_runs` et de
`mart.fact_transaction` : ne pas confondre lignes brutes et ventes distinctes.
