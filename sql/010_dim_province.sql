-- Static territorial characteristics, one row per production area.
-- These columns are repeated across every province-month in the climate
-- table; isolating them prevents a province from being weighted by the
-- number of months it appears in, and gives the altitude class and macro
-- region a single definition shared by EDA, modelling and any BI layer.

CREATE OR REPLACE VIEW `agriclimate-intelligence.utilities.dim_province`
OPTIONS (
  description = "One row per production area: region, territorial characteristics, morphological altitude class and macro-region."
)
AS

SELECT DISTINCT
  PROVINCE,
  REGION,
  N_CELLS,
  ALTITUDE_MIN,
  ALTITUDE_MAX,
  ALTITUDE_RANGE,
  ALTITUDE_MEAN,
  ALTITUDE_STD,

  -- ALTITUDE_MEAN describes the whole provincial territory and not the
  -- cultivated land, so the class is a morphological descriptor and the
  -- internal dispersion is retained as a second dimension.
  CASE
    WHEN ALTITUDE_MEAN < 300 AND ALTITUDE_STD <  150 THEN 'lowland'
    WHEN ALTITUDE_MEAN < 300                         THEN 'lowland mixed'
    WHEN ALTITUDE_MEAN < 700                         THEN 'hill'
    ELSE 'mountain'
  END AS ALTITUDE_CLASS,

  -- Groups the 20 Italian administrative regions into 6 broader
  -- geographical areas, matching REGION_TO_MACRO in the EDA notebook.
  -- Sicilia and Sardegna are kept as their own macro-region rather than
  -- folded into "South", since both are treated separately downstream.
  CASE REGION
    WHEN 'Piemonte'              THEN 'North West'
    WHEN 'Valle d\'Aosta'         THEN 'North West'
    WHEN 'Liguria'                THEN 'North West'
    WHEN 'Lombardia'              THEN 'North West'

    WHEN 'Trentino-Alto Adige'    THEN 'North East'
    WHEN 'Veneto'                 THEN 'North East'
    WHEN 'Friuli-Venezia Giulia'  THEN 'North East'
    WHEN 'Emilia-Romagna'         THEN 'North East'

    WHEN 'Toscana'                THEN 'Center'
    WHEN 'Umbria'                 THEN 'Center'
    WHEN 'Marche'                 THEN 'Center'
    WHEN 'Lazio'                  THEN 'Center'

    WHEN 'Abruzzo'                THEN 'South'
    WHEN 'Molise'                 THEN 'South'
    WHEN 'Campania'               THEN 'South'
    WHEN 'Puglia'                 THEN 'South'
    WHEN 'Basilicata'             THEN 'South'
    WHEN 'Calabria'               THEN 'South'

    WHEN 'Sicilia'                THEN 'Sicilia'
    WHEN 'Sardegna'               THEN 'Sardegna'

    -- A region absent from this mapping must never fall through to a
    -- silent NULL: it needs an explicit decision, not a gap discovered
    -- downstream in a groupby. Mirrors the ValueError in
    -- phase_aggregation_rule() for an unmapped climate column.
    ELSE ERROR(FORMAT("No macro-region mapping defined for REGION = %s", REGION))
  END AS MACRO_REGION

FROM `agriclimate-intelligence.curated.climate_full_dataset_v1`
;
