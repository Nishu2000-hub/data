-- Load test for the Issue #301 mock data CSVs.
--
-- Creates the ten tables in a scratch schema, loads every CSV, and re-runs
-- the foreign-key and geographic-consistency checks in SQL. Run from the
-- directory containing the CSV files:
--
--     psql "postgresql://postgres:localtest@localhost:5432/saayam_local" \
--          -v ON_ERROR_STOP=1 -f load_test.sql
--
-- Requires PostGIS: user_locations and volunteer_locations use
-- geography(Point, 4326).

\set ON_ERROR_STOP on

CREATE EXTENSION IF NOT EXISTS postgis;

DROP SCHEMA IF EXISTS mock_load_test CASCADE;
CREATE SCHEMA mock_load_test;
SET search_path TO mock_load_test, public;

-- Enum types used by user_skills and organizations
CREATE TYPE skill_levels  AS ENUM ('BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT');
CREATE TYPE org_type_enum AS ENUM ('non_profit', 'for_profit');
CREATE TYPE org_size_enum AS ENUM ('small', 'medium', 'large');

-- ── Tables, in foreign-key dependency order ────────────────────────

CREATE TABLE countries (
    country_id       SERIAL PRIMARY KEY,
    country_name     VARCHAR(100) NOT NULL,
    phone_code       VARCHAR(5)   NOT NULL,
    country_code     VARCHAR(6)   NOT NULL,
    last_updated_at  TIMESTAMP WITHOUT TIME ZONE,
    is_eu_member     BOOLEAN DEFAULT FALSE
);

CREATE TABLE states (
    state_id         VARCHAR(50) PRIMARY KEY,
    country_id       INT NOT NULL,
    state_name       VARCHAR(100) NOT NULL,
    state_code       VARCHAR(6),
    last_updated_at  TIMESTAMP WITHOUT TIME ZONE,
    FOREIGN KEY (country_id) REFERENCES countries (country_id)
);

CREATE TABLE cities (
    city_id          SERIAL PRIMARY KEY,
    state_id         VARCHAR(50) NOT NULL,
    city_name        VARCHAR(30) NOT NULL,
    lattitude        DECIMAL(9, 6),   -- spelled with two t's in the source DDL
    longitude        DECIMAL(9, 6),
    last_updated_at  TIMESTAMP WITHOUT TIME ZONE,
    FOREIGN KEY (state_id) REFERENCES states (state_id)
);

CREATE TABLE help_categories (
    cat_id           VARCHAR(50) PRIMARY KEY,
    cat_name         VARCHAR(100) NOT NULL,
    cat_desc         VARCHAR(150) NOT NULL,
    last_updated_at  TIMESTAMP WITHOUT TIME ZONE
);

CREATE TABLE users (
    user_id                          VARCHAR(255) PRIMARY KEY,
    state_id                         VARCHAR(30) NULL,
    country_id                       INT NULL,
    user_status_id                   INT NULL,
    full_name                        VARCHAR(255),
    first_name                       VARCHAR(255),
    middle_name                      VARCHAR(255),
    last_name                        VARCHAR(255),
    primary_email_address            VARCHAR(255),
    primary_phone_number             VARCHAR(255),
    addr_ln1                         VARCHAR(255),
    addr_ln2                         VARCHAR(255),
    addr_ln3                         VARCHAR(255),
    city_name                        VARCHAR(255),
    zip_code                         VARCHAR(255),
    last_location                    point,
    last_updated_at                  TIMESTAMP WITHOUT TIME ZONE,
    time_zone                        VARCHAR(255),
    profile_picture_path             VARCHAR(255),
    gender                           VARCHAR(255),
    language_1                       BIGINT,
    language_2                       BIGINT,
    language_3                       BIGINT,
    promotion_wizard_stage           INT,
    promotion_wizard_last_updated_at TIMESTAMP WITHOUT TIME ZONE,
    external_auth_provider           VARCHAR(20),
    dob                              DATE,
    is_eu                            BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (country_id) REFERENCES countries (country_id),
    FOREIGN KEY (state_id)   REFERENCES states (state_id)
);

CREATE TABLE volunteer_details (
    user_id              VARCHAR(255) PRIMARY KEY,
    terms_and_conditions BOOLEAN,
    terms_accepted_at    TIMESTAMP WITHOUT TIME ZONE,
    govt_id_path1        TEXT,
    govt_id_path2        TEXT,
    path1_updated_at     TIMESTAMP WITHOUT TIME ZONE,
    path2_updated_at     TIMESTAMP WITHOUT TIME ZONE,
    availability_days    JSONB,
    availability_times   JSONB,
    created_at           TIMESTAMP WITHOUT TIME ZONE,
    last_updated_at      TIMESTAMP WITHOUT TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE user_skills (
    user_id          VARCHAR(255),
    cat_id           VARCHAR(50) NOT NULL,
    skill_level      skill_levels,
    created_at       TIMESTAMP WITHOUT TIME ZONE,
    last_updated_at  TIMESTAMP WITHOUT TIME ZONE,
    PRIMARY KEY (user_id, cat_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (cat_id)  REFERENCES help_categories (cat_id)
);

CREATE TABLE organizations (
    org_id           VARCHAR(255) PRIMARY KEY,
    org_name         VARCHAR(125) NOT NULL,
    street           VARCHAR(255),
    city_name        VARCHAR(100),
    state_id         VARCHAR(50),
    zip_code         VARCHAR(10),
    mission          TEXT,
    web_url          VARCHAR(255) CHECK (web_url IS NULL OR web_url LIKE 'http%'),
    phone            VARCHAR(20),
    email            VARCHAR(255) CHECK (email IS NULL OR email LIKE '%@%'),
    org_type         org_type_enum,
    org_size         org_size_enum,
    org_rating       INTEGER CHECK (org_rating >= 1 AND org_rating <= 5),
    is_collaborator  BOOLEAN,
    is_contributor   BOOLEAN,
    created_at       TIMESTAMP WITHOUT TIME ZONE,
    last_updated_at  TIMESTAMP WITHOUT TIME ZONE,
    FOREIGN KEY (state_id) REFERENCES states (state_id)
);

CREATE TABLE user_locations (
    user_id          VARCHAR(255) PRIMARY KEY,
    prev_loc         geography(Point, 4326),
    curr_loc         geography(Point, 4326),
    last_updated_at  TIMESTAMP WITHOUT TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

CREATE TABLE volunteer_locations (
    user_id          VARCHAR(255) PRIMARY KEY,
    prev_loc         geography(Point, 4326),
    curr_loc         geography(Point, 4326),
    last_updated_at  TIMESTAMP WITHOUT TIME ZONE,
    -- references volunteer_details, NOT users
    FOREIGN KEY (user_id) REFERENCES volunteer_details (user_id) ON DELETE CASCADE
);

-- ── Load the CSVs ──────────────────────────────────────────────────
-- Loaded in dependency order. Any orphan foreign key, bad datatype or
-- violated CHECK constraint aborts the script because ON_ERROR_STOP is set.

\copy countries           FROM 'countries.csv'           WITH (FORMAT csv, HEADER true, NULL '')
\copy states              FROM 'states.csv'              WITH (FORMAT csv, HEADER true, NULL '')
\copy cities              FROM 'cities.csv'              WITH (FORMAT csv, HEADER true, NULL '')
\copy help_categories     FROM 'help_categories.csv'     WITH (FORMAT csv, HEADER true, NULL '')
\copy users               FROM 'users.csv'               WITH (FORMAT csv, HEADER true, NULL '')
\copy volunteer_details   FROM 'volunteer_details.csv'   WITH (FORMAT csv, HEADER true, NULL '')
\copy user_skills         FROM 'user_skills.csv'         WITH (FORMAT csv, HEADER true, NULL '')
\copy organizations       FROM 'organizations.csv'       WITH (FORMAT csv, HEADER true, NULL '')
\copy user_locations      FROM 'user_locations.csv'      WITH (FORMAT csv, HEADER true, NULL '')
\copy volunteer_locations FROM 'volunteer_locations.csv' WITH (FORMAT csv, HEADER true, NULL '')

-- ── Row counts ─────────────────────────────────────────────────────

\echo ''
\echo 'Rows loaded'
\echo '-----------'

SELECT 'countries'           AS table_name, count(*) FROM countries
UNION ALL SELECT 'states',              count(*) FROM states
UNION ALL SELECT 'cities',              count(*) FROM cities
UNION ALL SELECT 'help_categories',     count(*) FROM help_categories
UNION ALL SELECT 'users',               count(*) FROM users
UNION ALL SELECT 'volunteer_details',   count(*) FROM volunteer_details
UNION ALL SELECT 'user_skills',         count(*) FROM user_skills
UNION ALL SELECT 'organizations',       count(*) FROM organizations
UNION ALL SELECT 'user_locations',      count(*) FROM user_locations
UNION ALL SELECT 'volunteer_locations', count(*) FROM volunteer_locations;

-- ── Post-load checks ───────────────────────────────────────────────
-- The foreign keys above already reject orphans at load time. These
-- confirm the parts the schema cannot enforce on its own.

\echo ''
\echo 'Post-load checks (expect 0 rows from each)'
\echo '------------------------------------------'

\echo 'users whose city does not belong to their state:'
SELECT u.user_id, u.state_id, u.city_name
FROM users u
LEFT JOIN cities c
       ON c.state_id = u.state_id AND c.city_name = u.city_name
WHERE c.city_id IS NULL;

\echo 'organizations whose city does not belong to their state:'
SELECT o.org_id, o.state_id, o.city_name
FROM organizations o
LEFT JOIN cities c
       ON c.state_id = o.state_id AND c.city_name = o.city_name
WHERE c.city_id IS NULL;

\echo 'rows where created_at is later than last_updated_at:'
SELECT 'volunteer_details' AS src, user_id::text AS id
FROM volunteer_details WHERE created_at > last_updated_at
UNION ALL
SELECT 'user_skills', user_id || '/' || cat_id
FROM user_skills WHERE created_at > last_updated_at
UNION ALL
SELECT 'organizations', org_id
FROM organizations WHERE created_at > last_updated_at;

\echo 'volunteer_locations whose user has no volunteer_details row:'
SELECT vl.user_id
FROM volunteer_locations vl
LEFT JOIN volunteer_details vd ON vd.user_id = vl.user_id
WHERE vd.user_id IS NULL;

\echo 'location points further than 100km from their city centroid:'
SELECT ul.user_id,
       round(ST_Distance(ul.curr_loc,
             ST_SetSRID(ST_MakePoint(c.longitude, c.lattitude), 4326)::geography
       )::numeric / 1000, 1) AS km_from_city
FROM user_locations ul
JOIN users  u ON u.user_id = ul.user_id
JOIN cities c ON c.state_id = u.state_id AND c.city_name = u.city_name
WHERE ST_Distance(ul.curr_loc,
        ST_SetSRID(ST_MakePoint(c.longitude, c.lattitude), 4326)::geography
      ) > 100000;

\echo ''
\echo 'Load test complete. Every table above loaded without error.'

-- Leave the schema in place for inspection.
-- Drop it with:  DROP SCHEMA mock_load_test CASCADE;
