# Validation du pipeline ETL - Paris 2025

## Source
Donnees DVF geolocalisees, departement 75, annee 2025.

## Resultats du chargement
- Lignes source : 84440
- Lignes valides : 84440
- Transactions consolidees : 40323
- Transactions eligibles au prix/m2 : 29651
- Prix median au m2 : 9680.85 EUR
- Groupes de transactions dupliques : 0

## Tests
- 6 tests Pytest reussis en 0.87 seconde.

## Methodologie
Le pipeline extrait le CSV DVF, valide les lignes,
charge les donnees dans PostgreSQL avec COPY et
consolide les ventes au grain mutation/disposition.

Le prix median au m2 est calcule uniquement sur
les transactions eligibles selon les regles du projet.

## Limites
Le nombre de lignes valides ne garantit pas une
qualite parfaite de toutes les variables.
Les indicateurs necessitent des controles supplementaires.

## Prochaines etapes
- Valider la separation entre dvf et dvf_test.
- Charger les sept autres departements.
- Construire le dashboard Power BI.
