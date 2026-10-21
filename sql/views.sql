CREATE OR REPLACE VIEW mart.v_powerbi_transactions AS
SELECT
    f.source_year,
    f.source_department AS departement,
    f.id_mutation,
    f.numero_disposition,
    d.date_key AS date_vente,
    d.annee,
    d.trimestre,
    d.mois,
    g.code_commune,
    g.nom_commune,
    t.type_bien,
    f.valeur_fonciere,
    f.surface_bati,
    f.prix_m2,
    f.prix_m2_eligible
FROM mart.fact_transaction AS f
JOIN mart.dim_date AS d ON f.date_key = d.date_key
JOIN mart.dim_geo AS g ON f.code_commune = g.code_commune
JOIN mart.dim_type_bien AS t ON f.type_bien_id = t.type_bien_id;

CREATE OR REPLACE VIEW mart.v_qualite AS
SELECT source_year, source_department,
       COUNT(*) AS nombre_ventes,
       COUNT(*) FILTER (WHERE prix_m2_eligible) AS ventes_avec_prix_m2,
       ROUND(100.0 * COUNT(*) FILTER (WHERE prix_m2_eligible)
             / NULLIF(COUNT(*), 0), 2) AS pourcentage_eligibles
FROM mart.fact_transaction
GROUP BY source_year, source_department;
