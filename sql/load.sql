-- Exécuté dans une transaction par fichier, avec une table temporaire staging_file.
-- Grain cible : 1 mutation + 1 disposition + 1 département + 1 année.
-- Une valeur foncière répétée sur plusieurs lignes n'est comptée qu'une fois.
CREATE TEMP TABLE agg_file ON COMMIT DROP AS
SELECT
    source_year,
    source_department,
    id_mutation,
    numero_disposition,
    MIN(date_mutation) AS date_mutation,
    MIN(nature_mutation) AS nature_mutation,
    MIN(valeur_fonciere) AS valeur_fonciere,
    MIN(code_commune) AS code_commune,
    MIN(nom_commune) AS nom_commune,
    COUNT(*) FILTER (
        WHERE type_local IN ('Appartement', 'Maison')
          AND surface_reelle_bati > 0
    ) AS nb_lignes_baties,
    COUNT(*) FILTER (
        WHERE type_local IS NOT NULL
          AND type_local NOT IN ('Appartement', 'Maison', 'Dépendance')
    ) AS nb_autres_locaux,
    MAX(type_local) FILTER (
        WHERE type_local IN ('Appartement', 'Maison')
          AND surface_reelle_bati > 0
    ) AS type_local,
    MAX(surface_reelle_bati) FILTER (
        WHERE type_local IN ('Appartement', 'Maison')
          AND surface_reelle_bati > 0
    ) AS surface_bati
FROM staging_file
GROUP BY source_year, source_department, id_mutation, numero_disposition
HAVING COUNT(DISTINCT date_mutation) = 1
   AND COUNT(DISTINCT nature_mutation) = 1
   AND MIN(nature_mutation) = 'Vente'
   AND COUNT(DISTINCT valeur_fonciere) = 1
   AND MIN(valeur_fonciere) > 0
   AND COUNT(DISTINCT code_commune) = 1;

INSERT INTO mart.dim_date(date_key, annee, trimestre, mois)
SELECT DISTINCT date_mutation,
       EXTRACT(YEAR FROM date_mutation)::int,
       EXTRACT(QUARTER FROM date_mutation)::int,
       EXTRACT(MONTH FROM date_mutation)::int
FROM agg_file
ON CONFLICT (date_key) DO NOTHING;

INSERT INTO mart.dim_geo(code_commune, nom_commune, code_departement)
SELECT code_commune, MIN(nom_commune), MIN(source_department)
FROM agg_file
GROUP BY code_commune
ON CONFLICT (code_commune) DO UPDATE SET
    nom_commune = EXCLUDED.nom_commune,
    code_departement = EXCLUDED.code_departement;

-- Le rechargement d'un même couple département/année remplace ses données.
DELETE FROM mart.fact_transaction
WHERE source_year = %s AND source_department = %s;

INSERT INTO mart.fact_transaction (
    source_year, source_department, id_mutation, numero_disposition,
    date_key, code_commune, type_bien_id, valeur_fonciere,
    surface_bati, prix_m2, prix_m2_eligible
)
SELECT
    source_year,
    source_department,
    id_mutation,
    numero_disposition,
    date_mutation,
    code_commune,
    CASE
        WHEN nb_lignes_baties = 1 AND nb_autres_locaux = 0 AND type_local = 'Appartement' THEN 1
        WHEN nb_lignes_baties = 1 AND nb_autres_locaux = 0 AND type_local = 'Maison' THEN 2
        ELSE 3
    END,
    valeur_fonciere,
    CASE WHEN nb_lignes_baties = 1 AND nb_autres_locaux = 0
         THEN surface_bati ELSE NULL END,
    CASE WHEN nb_lignes_baties = 1 AND nb_autres_locaux = 0
         THEN ROUND(valeur_fonciere / NULLIF(surface_bati, 0), 2)
         ELSE NULL END,
    nb_lignes_baties = 1 AND nb_autres_locaux = 0
FROM agg_file;
