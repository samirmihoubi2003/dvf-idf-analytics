# Plan d'évolution du portfolio

## Jalon A — Premier pipeline local
- [ ] Installer Python, Git, Docker Desktop et Power BI Desktop
- [ ] Lancer PostgreSQL en Docker
- [ ] Charger le petit fichier exemple et contrôler les 4 ventes
- [ ] Charger les ventes 2025 de Paris
- [ ] Noter les chiffres réels chargés dans `mart.etl_runs`

## Jalon B — Data Warehouse complet
- [ ] Ajouter les 8 départements
- [ ] Ajouter l'année 2024
- [ ] Examiner le taux de ventes exclues et éligibles prix/m²
- [ ] Documenter les limites de la source et les évolutions de millésimes

## Jalon C — Git / CI
- [ ] Dépôt GitHub public (aucun secret)
- [ ] Branches `main` et `develop`
- [ ] PR d'une amélioration réelle
- [ ] CI verte incluant un PostgreSQL jetable pour tests
- [ ] Ajouter éventuellement un PostgreSQL externe avant ETL GitHub Actions

## Jalon D — Power BI
- [ ] Importer la vue dans Power BI Desktop
- [ ] Créer les 8 mesures DAX
- [ ] Construire 2 pages : marché et qualité
- [ ] Tester filtres année / département / type
- [ ] Exporter uniquement des captures/agrégats anonymes sur GitHub

## Jalon E — Valorisation CV
- [ ] Décrire N lignes ingérées et M ventes distinctes : chiffres calculés
- [ ] Ajouter une capture d'écran du dashboard
- [ ] Ajouter un schéma de l'architecture et les enseignements métier
- [ ] Présenter commits, PR et tests dans le README
