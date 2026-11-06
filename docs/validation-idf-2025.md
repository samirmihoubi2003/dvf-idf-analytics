# Validation ETL - Immobilier Ile-de-France 2025

## Technologies
Python, PostgreSQL 17, Docker, SQL, Pytest, GitHub Actions.

## Source des donnees
Demandes de Valeurs Foncieres (DVF) geolocalisees.
Annee : 2025.
Departements : 75, 77, 78, 91, 92, 93, 94, 95.

## Resultats globaux
- Transactions consolidees : 164173
- Departements analyses : 8
- Transactions eligibles au prix/m2 : 123809
- Prix median au m2 : 4687.50 EUR
- Anomalies prix/m2 parmi les eligibles : 0
- Transactions a valeur symbolique <= 1 EUR : 660
- Transactions symboliques eligibles : 0

## Qualite des donnees
- Regroupement des transactions multi-lignes.
- Validation des dates et des valeurs numeriques.
- Exclusion des valeurs symboliques du calcul du prix/m2.
- Conservation des transactions symboliques dans la base.
- Chargement reproductible par annee et departement.

## Tests
- 7 tests Pytest reussis en 0.55 seconde.
- Ruff : All checks passed.
- Base de test separee : dvf_test.

## Limites
- Le prix/m2 est calcule uniquement sur les transactions eligibles.
- Les ventes complexes peuvent etre exclues du calcul.
- Le prix median depend des regles de selection.
- L'ecart de 46 transactions avec l'ancien calcul reste a analyser.

## Prochaines etapes
- Finaliser le workflow GitHub.
- Construire le dashboard Power BI.
- Ajouter les KPI et les mesures DAX.
