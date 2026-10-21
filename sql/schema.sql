CREATE SCHEMA IF NOT EXISTS mart;

CREATE TABLE IF NOT EXISTS mart.dim_date (
    date_key DATE PRIMARY KEY,
    annee INTEGER NOT NULL,
    trimestre INTEGER NOT NULL CHECK (trimestre BETWEEN 1 AND 4),
    mois INTEGER NOT NULL CHECK (mois BETWEEN 1 AND 12)
);

CREATE TABLE IF NOT EXISTS mart.dim_geo (
    code_commune TEXT PRIMARY KEY,
    nom_commune TEXT NOT NULL,
    code_departement TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mart.dim_type_bien (
    type_bien_id SMALLINT PRIMARY KEY,
    type_bien TEXT NOT NULL UNIQUE
);

INSERT INTO mart.dim_type_bien(type_bien_id, type_bien) VALUES
    (1, 'Appartement'),
    (2, 'Maison'),
    (3, 'Autre / multiple')
ON CONFLICT (type_bien_id) DO NOTHING;

CREATE TABLE IF NOT EXISTS mart.fact_transaction (
    source_year INTEGER NOT NULL,
    source_department TEXT NOT NULL,
    id_mutation TEXT NOT NULL,
    numero_disposition TEXT NOT NULL,
    date_key DATE NOT NULL REFERENCES mart.dim_date(date_key),
    code_commune TEXT NOT NULL REFERENCES mart.dim_geo(code_commune),
    type_bien_id SMALLINT NOT NULL REFERENCES mart.dim_type_bien(type_bien_id),
    valeur_fonciere NUMERIC(18, 2) NOT NULL CHECK (valeur_fonciere > 0),
    surface_bati NUMERIC(14, 2),
    prix_m2 NUMERIC(18, 2),
    prix_m2_eligible BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (source_year, source_department, id_mutation, numero_disposition)
);
CREATE INDEX IF NOT EXISTS idx_fact_date ON mart.fact_transaction(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_geo ON mart.fact_transaction(code_commune);
CREATE INDEX IF NOT EXISTS idx_geo_departement ON mart.dim_geo(code_departement);

CREATE TABLE IF NOT EXISTS mart.etl_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    source_year INTEGER NOT NULL,
    source_department TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    lignes_source BIGINT NOT NULL,
    lignes_valides BIGINT NOT NULL,
    transactions_chargees BIGINT NOT NULL
);
