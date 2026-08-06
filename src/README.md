# Source Code

This directory contains reusable Python code shared by the project notebooks.

> [!NOTE]
> The source-code layer is still small and is expected to grow as the project moves from ETL and EDA toward integrated data preparation and modeling.

## Current contents

```text
src/
├── __init__.py
├── eda_utils.py
└── province_transformation.py
```

## `province_transformation.py`

### Purpose

This module contains the main reusable climate transformation.

Its central entry point converts daily gridded observations for one source territory into monthly provincial climate indicators.

### Expected input

The current transformation expects fields corresponding to:

```text
IDCELL
LATITUDE
LONGITUDE
ALTITUDE
DAY
TEMPERATURE_MAX
TEMPERATURE_MIN
TEMPERATURE_AVG
WINDSPEED
VAPOURPRESSURE
PRECIPITATION
ET0
RADIATION
```

### Current validation logic

The module checks:

- input object and dataframe emptiness;
- required columns;
- duplicate column names;
- missing observations;
- valid date conversion;
- numeric conversion;
- duplicate `IDCELL`–`DAY` keys;
- stability of geographical attributes for each cell;
- consistency of the grid through time;
- invalid negative values in non-negative variables;
- logical ordering of minimum, average, and maximum temperatures.

Where possible, inconsistent temperature ordering is corrected by reordering the three values before the final check.

### Historical thresholds

The transformation derives month-specific historical thresholds from the available reference-period observations.

Current event definitions include relative thresholds for:

- high maximum temperature;
- low minimum temperature;
- heavy positive precipitation;
- high wind speed.

These are complemented by absolute thresholds for events such as frost, high heat, very high heat, wet cells, and heavy precipitation.

Threshold values and the reference period are methodological choices. Any change can affect the entire curated climate dataset and must therefore be documented.

### Spatial logic

The transformation does not reduce each province to a single raw mean.

For each day it derives indicators describing:

- average conditions across cells;
- local maximum or minimum;
- spatial standard deviation;
- proportion of cells affected;
- whether an event exceeds the minimum territorial-coverage rule.

This allows localized extremes to be distinguished from events affecting a meaningful share of the province.

### Temporal logic

The workflow combines two levels:

```text
cell–day observations
├── direct monthly aggregation
└── daily provincial state
      └── monthly aggregation
```

The final output includes indicators related to:

- temperature averages and local extremes;
- spatial temperature variability;
- precipitation intensity and totals;
- wet-day frequency;
- local precipitation maxima;
- wind conditions;
- vapour pressure;
- reference evapotranspiration;
- solar radiation;
- event frequency;
- territorial shares affected;
- longest consecutive event sequences;
- static altitude properties.

### Altitude features

Altitude is derived from unique grid cells, not from repeated daily rows.

Current fields include:

```text
ALTITUDE_MEAN
ALTITUDE_STD
ALTITUDE_MIN
ALTITUDE_MAX
ALTITUDE_RANGE
```

### Current use

The function is:

- demonstrated incrementally in `notebooks/ETL_Climate_Example.ipynb`;
- executed across all mapped target areas by `notebooks/ETL_Climate_Data.ipynb`.

## `eda_utils.py`

### Purpose

This module provides reusable utilities for consistent exploratory analysis and visualization.

### Current capabilities

The utilities include support for:

- required-column validation;
- dataframe diagnostics;
- missing-value summaries;
- zero-value summaries;
- frequency tables;
- readable variable labels;
- plot-style configuration;
- variable-type recognition;
- univariate analysis of continuous variables;
- univariate analysis of discrete variables;
- univariate analysis of categorical variables;
- reusable bivariate visualization helpers.

The EDA notebook imports these utilities and supplements them with notebook-specific logic for trends, PACF, coverage, and production-series analysis.

### Boundaries

Reusable plotting and diagnostic functions belong in this module.

Dataset-specific conclusions, analytical narrative, crop-selection decisions, and project-stage interpretations should remain in notebooks or dedicated documentation.

## `__init__.py`

This file marks the directory as a Python package namespace.

The project is not currently configured as an installable package. Notebook imports therefore still depend on adding `src/` to the Python path or executing from the expected project layout.

## Development guidelines

Code added to `src/` should:

- implement reusable or independently testable logic;
- avoid dependence on notebook-global variables;
- use descriptive function names;
- include docstrings for public functions;
- use type hints where they improve clarity;
- validate assumptions at function boundaries;
- raise informative errors;
- avoid hard-coded user-specific paths;
- keep cloud configuration separate from transformation logic;
- preserve generated column names unless a documented dataset version is introduced.

## Testing status

No automated test suite is currently present.

Priority areas include:

```text
required-column validation
temperature reordering
duplicate cell–day detection
geographical consistency
historical-threshold calculation
affected-area calculations
daily-to-monthly aggregation
consecutive-event sequences
precipitation totals
ET0 and radiation totals
altitude features
EDA utility dispatch and plotting behavior
```

## Expected future modules

As the project progresses, reusable logic may be separated into modules for:

```text
territorial configuration
production transformation
crop-season construction
feature engineering
dataset integration
temporal validation
model baselines
model training
evaluation
interpretability
```

These are expected responsibilities, not files currently present in the repository.

## Change management

A material change to a threshold, aggregation rule, or feature definition can alter all downstream records.

For such changes:

1. document the previous and new definition;
2. identify affected output columns;
3. regenerate the curated climate dataset;
4. rerun data-quality checks and EDA;
5. update relevant README sections;
6. consider incrementing the curated-table or transformation version.
