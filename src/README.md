# Source Code

This directory contains the reusable Python utilities used by the AgriClimate Intelligence notebooks.

```text
src/
├── __init__.py
├── eda_utils.py
├── modelling_utils.py
└── province_transformation.py
```

The notebooks retain experiment order, narrative and domain interpretation, while functions that are reusable or would otherwise obscure the analysis are kept here.

## Module overview

| Module | Responsibility | Used by |
| --- | --- | --- |
| `province_transformation.py` | Validate and transform daily gridded climate observations into monthly provincial indicators | Climate ETL notebooks |
| `eda_utils.py` | Shared exploratory-analysis helpers and project plotting style | EDA + modelling |
| `modelling_utils.py` | Quantile modelling, temporal validation, SFS, CatBoost, post-processing, aggregation and SHAP support | Modelling notebook |

`__init__.py` marks `src` as a Python package. The notebooks import reusable utilities through this package, although the repository is not currently distributed as an installable Python package.

---

# `province_transformation.py`

## Purpose

This module implements the reusable climate-data transformation used by the ETL workflow.

It converts daily gridded observations for one source territory into a monthly provincial representation.

## Expected source variables

The transformation works with fields corresponding to:

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

## Validation

The module checks:

- required columns;
- empty inputs;
- duplicate column names;
- missing values;
- date conversion;
- numeric conversion;
- duplicate `IDCELL`–`DAY` keys;
- stability of cell geography;
- consistency of the grid through time;
- invalid negative values where variables must be non-negative;
- logical ordering of minimum, average and maximum temperature.

Where possible, inconsistent temperature values are repaired by reordering the three temperature measurements before final validation.

## Climate-event thresholds

The transformation combines relative historical thresholds and absolute agronomic/meteorological definitions.

Derived events include examples such as:

- unusually high maximum temperature;
- unusually low minimum temperature;
- heavy positive precipitation;
- high wind;
- frost;
- high and very high heat;
- wet cells;
- heavy rainfall.

Threshold definitions are part of the project methodology and should not be changed casually, because they affect all downstream climate features.

## Spatial aggregation

Daily provincial indicators preserve the spatial nature of the gridded source rather than collapsing each day immediately to one average.

Depending on the variable, the transformation can retain:

- territorial mean;
- local maximum or minimum;
- spatial standard deviation;
- proportion of cells affected;
- whether a sufficient share of the territory experienced an event.

This distinguishes localized extremes from events affecting a meaningful part of a province.

## Temporal aggregation

The workflow combines:

```text
cell × day observations
        │
        ├── direct monthly statistics
        │
        └── daily provincial event states
                │
                ▼
           monthly indicators
```

The final features cover:

- temperature;
- precipitation;
- wind;
- vapour pressure;
- evapotranspiration;
- radiation;
- spatial variability;
- event frequency;
- affected territorial share;
- consecutive-event duration;
- altitude.

## Altitude

Altitude is calculated from unique grid cells rather than repeated daily rows.

Current static features include:

```text
ALTITUDE_MEAN
ALTITUDE_STD
ALTITUDE_MIN
ALTITUDE_MAX
ALTITUDE_RANGE
```

## Usage

The transformation is demonstrated in:

```text
notebooks/ETL_Climate_Example.ipynb
```

and executed across the full source mapping in:

```text
notebooks/ETL_Climate_Data.ipynb
```

---

# `eda_utils.py`

## Purpose

This module centralizes reusable exploratory-analysis helpers and the visual identity shared across the project.

## Plot style

The project palette and semantic aliases are defined here, including:

```text
GOLD
TEAL
TEAL_LIGHT
DARK
GRAY_MED
GRAY_LIGHT
```

`set_plot_style()` applies shared conventions such as:

- white background;
- minimal spines;
- left-aligned titles;
- consistent font sizing;
- frameless legends.

Modelling visualizations import these definitions rather than maintaining a second color system.

## Main utilities

The module includes helpers for:

- required-column checks;
- dataframe diagnostics;
- missing-value summaries;
- zero-value summaries;
- frequency tables;
- readable feature labels;
- continuous-variable exploration;
- discrete-variable exploration;
- categorical distributions;
- numeric–numeric relationships;
- numeric–categorical relationships;
- categorical composition;
- temporal plots;
- stacked time-series composition;
- seasonality heatmaps;
- reusable axes for notebook layouts.

The goal is to keep repeated plotting and descriptive logic out of the EDA notebook while preserving transparent notebook-level analysis.

---

# `modelling_utils.py`

## Purpose

This module contains reusable functions supporting the complete quantile-modelling workflow.

Current public utilities are:

```text
pinball
make_linear_pipeline
rolling_history_median
temporal_cv_indices
temporal_cv_scores
evaluate_feature_set
fit_sfs
selected_feature_table
native_feature_names
make_regularized_linear_pipeline
q2_l1_cv_scores
select_l1_alpha
evaluate_regularized_feature_set
make_catboost_q2_model
fit_catboost_q2
correction_function
add_quantile_limits
aggregate_national_predictions
plot_national_quantile_forecast
NamedColumnsWrapper
```

## Core quantile modelling

### `pinball()`

Convenience wrapper around `mean_pinball_loss`.

### `make_linear_pipeline()`

Builds the development-stage unregularized linear quantile model:

```text
StandardScaler
      ↓
QuantileRegressor(alpha=0)
```

Scaling remains inside the pipeline so that it is refitted independently inside every temporal fold.

## Historical features

### `rolling_history_median()`

Calculates a rolling historical median using only yields observed in previous calendar years.

It can be applied at different levels, for example:

```text
crop × province
crop × region
```

This prevents future target observations from entering historical predictors.

## Chronological validation

### `temporal_cv_indices()`

Converts year-defined chronological folds into positional train/validation indices for scikit-learn tools.

### `temporal_cv_scores()`

Fits and evaluates each requested quantile independently inside each chronological fold.

### `evaluate_feature_set()`

Produces full-development train losses and mean temporal-CV losses for one feature representation.

The core invariant is:

```text
validation year > every training year
```

## Sequential Forward Selection

### `fit_sfs()`

Runs forward `SequentialFeatureSelector` using:

- Q2 pinball loss;
- the explicit chronological folds;
- the standard linear quantile pipeline.

The selected set is specific to the linear SFS experiment and is not assumed to define the optimal representation for all nonlinear models.

### `selected_feature_table()`

Builds a compact summary of selected variables, distinguishing:

```text
historical
climate
```

and extracting the crop-phase suffix from engineered climate feature names.

## Native missing values

### `native_feature_names()`

Maps zero-filled historical feature names to their native missing-value equivalents for model families that support numerical `NaN` values directly.

This prevents the imputation strategy required by linear regression from being imposed unnecessarily on CatBoost or TabPFN.

## L1 quantile regression

The module provides helpers to:

- build regularized quantile pipelines;
- evaluate candidate `alpha` values on chronological folds;
- choose the strongest effectively tied regularization value;
- evaluate the selected regularized specification.

This is used as a sensitivity check rather than as a separate unrestricted modelling strategy.

## CatBoost

### `make_catboost_q2_model()`

Creates the common Q2 CatBoost specification with deterministic project settings.

### `fit_catboost_q2()`

Implements leakage-safe early stopping:

1. the most recent years inside the current training window are used to determine tree count;
2. the external validation period remains untouched;
3. a fresh model is refitted on the complete training window using the selected number of trees.

## Quantile post-processing

### `correction_function()`

Enforces the expected order between two consecutive quantiles.

### `add_quantile_limits()`

Constructs the final coherent distribution:

```text
0 ≤ Q1* ≤ Q2* ≤ Q3*
```

and derives:

```text
predicted IQR
lower Tukey-style limit
upper Tukey-style limit
```

This post-processing is used only for probabilistic interpretation and diagnostics. Official final-test pinball losses remain based on the raw model outputs.

## Area-weighted aggregation

### `aggregate_national_predictions()`

Transforms province-level yield estimates into implied production:

```text
predicted yield × cultivated area
```

and reconstructs aggregate yield from:

```text
total predicted production / total cultivated area
```

This procedure is applied consistently to observed yield, Q1, Q2, Q3 and the conditional limits.

Although originally introduced for national aggregation, the same logic is also reused for selected macro-regional areas in the final modelling analysis.

## Forecast visualization

### `plot_national_quantile_forecast()`

Draws an aggregate observed-versus-predicted yield chart containing:

- observed yield;
- predicted median;
- Q1–Q3 interquartile band;
- lower and upper Tukey-style limits;
- flagged low or high outliers.

The function accepts an `area_label`, so it is used for both:

```text
National
selected territorial aggregates
```

The resulting title follows:

```text
{crop} - {area_label}: observed yield and quantile forecast
```

and the legend is kept in the upper-right corner.

## TabPFN / SHAP support

### `NamedColumnsWrapper`

The final TabPFN interpretation uses `shapiq`, which internally passes NumPy arrays to the model, whereas the fitted TabPFN client expects the named DataFrame columns used during training.

`NamedColumnsWrapper` rebuilds that DataFrame before prediction while transparently forwarding other model attributes.

This adapter allows the final TabPFN models to be interpreted with the SHAP/shapiq workflow without changing their trained feature schema.

---

## Import pattern

The notebooks are designed to run from the `notebooks/` directory and add the project root to the Python path so that `src` is imported as a package.

```python
from pathlib import Path
import sys

CURRENT_DIR = Path.cwd().resolve()
PROJECT_ROOT = CURRENT_DIR.parent

DATA_DIR = PROJECT_ROOT / "data"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
```

Utilities are then imported through the `src` package:

```python
from src.eda_utils import *
from src.modelling_utils import *
```

Modules can also be imported explicitly where appropriate, for example:

```python
from src.province_transformation import transform_province_dataframe
```

## Development conventions

When extending the source layer:

- move genuinely reusable logic out of notebooks;
- keep experiment order and interpretative narrative in the notebooks;
- preserve chronological validation and leakage controls;
- never use final-test results to modify a frozen model specification;
- maintain plotting style centrally in `eda_utils.py`;
- prefer small functions with explicit inputs and outputs;
- use deterministic seeds where applicable;
- avoid credentials, tokens and user-specific absolute paths;
- document methodological changes that alter downstream results.
