-- Phase-level aggregation rule for every dynamic climate variable, inferred
-- from the naming convention rather than from a static list.
--
-- Reading the schema from INFORMATION_SCHEMA makes this view automatically
-- detect new climate variables and validates that each one has a defined
-- aggregation policy. The modelling query in 030_modeling_dataset.sql uses
-- the frozen set of aggregation expressions corresponding to the schema
-- used for the final project dataset and must be reviewed if the schema
-- changes.

CREATE OR REPLACE VIEW `agriclimate-intelligence.utilities.climate_aggregation_rules`
OPTIONS (
  description = "Aggregation rule per dynamic climate variable, with a flag for rules that are a methodological default rather than implied by the quantity."
)
AS

WITH dynamic_columns AS (
  SELECT column_name
  FROM `agriclimate-intelligence.curated`.INFORMATION_SCHEMA.COLUMNS
  WHERE table_name = 'climate_full_dataset_v1'
    AND column_name NOT IN (
      -- identifiers
      'YEAR_MONTH', 'OBSERVED_DAYS', 'PROVINCE', 'REGION',
      -- static territorial characteristics
      'N_CELLS', 'ALTITUDE_MIN', 'ALTITUDE_MAX',
      'ALTITUDE_RANGE', 'ALTITUDE_MEAN', 'ALTITUDE_STD'
    )
)

SELECT
  column_name,

  CASE
    -- Retain the coldest monthly minimum within the phase.
    WHEN column_name = 'TEMPERATURE_MIN_MONTH'
      THEN 'MIN'

    -- Retain the largest monthly extreme, affected fraction or spell length.
    WHEN STARTS_WITH(column_name, 'MAX_CONSECUTIVE_')
      OR REGEXP_CONTAINS(column_name,
           r'(_MAX_MONTH|_LOCAL_DAILY_MAX|_LOCAL_MAX|_AREA_DAILY_MAX|_FRACTION_MAX)$')
      THEN 'MAX'

    -- Accumulate monthly totals and event-day counts over the phase.
    WHEN REGEXP_CONTAINS(column_name, r'^(DAYS_|WET_DAYS_|DRY_DAYS_)')
      OR ENDS_WITH(column_name, '_TOTAL_MONTH')
      THEN 'SUM'

    -- Average variables that represent typical monthly conditions.
    WHEN column_name = 'TEMPERATURE_DAILY_STD'
      OR REGEXP_CONTAINS(column_name,
           r'(_AVG_MONTH|_DAILY_AVG|_SPATIAL_STD_AVG|_FRACTION_AVG|_AREA_WHEN_PRESENT)$')
      THEN 'AVG'
  END AS aggregation_rule,

  -- For this group more than one aggregation could be defensible. The choice
  -- stays explicit so it can be revisited without archaeology on the notebook.
  (
    column_name = 'TEMPERATURE_DAILY_STD'
    OR REGEXP_CONTAINS(column_name, r'(_FRACTION_AVG|_AREA_WHEN_PRESENT)$')
  ) AS is_provisional_rule

FROM dynamic_columns
;

-- A new or renamed variable must never receive a silent default rule.
ASSERT (
  SELECT COUNT(*) = 0
  FROM `agriclimate-intelligence.utilities.climate_aggregation_rules`
  WHERE aggregation_rule IS NULL
) AS "climate_aggregation_rules: at least one climate variable matches no naming pattern";
