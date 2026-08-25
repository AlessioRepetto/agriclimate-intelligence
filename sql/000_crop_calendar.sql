-- Agronomic crop calendar (JRC EU28, Italy), transcribed from half-month
-- resolution to monthly. Persisting it as a table rather than a notebook
-- dictionary makes the agronomic assumption an auditable, versioned asset:
-- a change to a phase boundary becomes a reviewable diff and can be traced
-- back from any model trained on a given dataset version.
--
-- year_offset = -1  ->  month belongs to the year before harvest
-- year_offset =  0  ->  month belongs to the harvest year itself

CREATE OR REPLACE TABLE `agriclimate-intelligence.utilities.crop_calendar`
OPTIONS (
  description = "Crop development phases by relative month. Soft and durum wheat share the same JRC calendar."
)
AS

WITH wheat_phases AS (
  SELECT * FROM UNNEST([
    STRUCT('planting_early_vegetative' AS phase, -1 AS year_offset,  9 AS month),
    STRUCT('planting_early_vegetative',          -1,                10),
    STRUCT('planting_early_vegetative',          -1,                11),
    STRUCT('vegetative_reproductive',            -1,                12),
    STRUCT('vegetative_reproductive',             0,                 1),
    STRUCT('vegetative_reproductive',             0,                 2),
    STRUCT('vegetative_reproductive',             0,                 3),
    STRUCT('vegetative_reproductive',             0,                 4),
    STRUCT('vegetative_reproductive',             0,                 5),
    STRUCT('ripening_harvest',                    0,                 6),
    STRUCT('ripening_harvest',                    0,                 7)
  ])
),

maize_phases AS (
  SELECT * FROM UNNEST([
    STRUCT('planting_early_vegetative' AS phase, 0 AS year_offset,  4 AS month),
    STRUCT('vegetative_reproductive',            0,                 5),
    STRUCT('vegetative_reproductive',            0,                 6),
    STRUCT('vegetative_reproductive',            0,                 7),
    STRUCT('vegetative_reproductive',            0,                 8),
    STRUCT('ripening_harvest',                   0,                 9),
    STRUCT('ripening_harvest',                   0,                10),
    STRUCT('ripening_harvest',                   0,                11)
  ])
)

SELECT crop_name, phase, year_offset, month
FROM UNNEST(['Durum wheat', 'Soft wheat']) AS crop_name
CROSS JOIN wheat_phases

UNION ALL

SELECT 'Grain maize', phase, year_offset, month
FROM maize_phases
;

-- A crop-month must belong to one phase only, otherwise a climate month
-- would be counted twice when phase features are constructed.
ASSERT (
  SELECT COUNT(*) = 0
  FROM (
    SELECT crop_name, year_offset, month
    FROM `agriclimate-intelligence.utilities.crop_calendar`
    GROUP BY 1, 2, 3
    HAVING COUNT(*) > 1
  )
) AS "crop_calendar: a relative month is assigned to more than one phase";
