# Source Code

This directory contains reusable Python code shared across the ETL, EDA, and modelling notebooks.

The source layer now separates three main responsibilities:

```text
src/
├── __init__.py
├── eda_utils.py
├── modelling_utils.py
└── province_transformation.py
```

## Module overview

| Module | Main responsibility | Main consumers |
| --- | --- | --- |
| `province_transformation.py` | Validate and transform raw daily gridded climate data into monthly provincial indicators | Climate ETL notebooks |
| `eda_utils.py` | Shared descriptive-analysis utilities and project plotting style | EDA notebook and modelling plots |
| `modelling_utils.py` | Reusable quantile-modelling, temporal-validation, feature-selection, CatBoost, post-processing, and aggregation utilities | `ML_Quantile_Modelling.ipynb` |

`__init__.py` marks the directory as a Python package namespace, although the project is not currently distributed as an installable package.

---

## `province_transformation.py`

### Purpose

This module contains the main reusable climate transformation.

Its central workflow converts daily gridded observations for one source territory into monthly provincial climate indicators.

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

### Validation logic

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

Where possible, inconsistent temperature ordering is corrected by reordering the three temperature values before the final validation.

### Historical thresholds

The transformation derives month-specific historical thresholds from the available reference-period observations.

Current relative event definitions include thresholds for:

- high maximum temperature;
- low minimum temperature;
- heavy positive precipitation;
- high wind speed.

These are complemented by absolute event definitions such as:

- frost;
- high heat;
- very high heat;
- wet cells;
- heavy precipitation.

Threshold definitions are methodological choices. Changes to them can alter the complete curated climate dataset and should therefore be documented explicitly.

### Spatial logic

The transformation does not reduce each province directly to one raw mean.

For each day it derives indicators describing:

- average conditions across cells;
- local maximum or minimum;
- spatial standard deviation;
- proportion of cells affected;
- whether an event exceeds the minimum territorial-coverage rule.

This distinguishes localized extremes from events affecting a meaningful share of the province.

### Temporal logic

The workflow combines two levels:

```text
cell–day observations
├── direct monthly aggregation
└── daily provincial state
      └── monthly aggregation
```

The final output contains indicators related to:

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
- static altitude characteristics.

### Altitude features

Altitude is calculated from unique grid cells rather than repeated daily rows.

Current fields include:

```text
ALTITUDE_MEAN
ALTITUDE_STD
ALTITUDE_MIN
ALTITUDE_MAX
ALTITUDE_RANGE
```

### Current use

The module is:

- demonstrated incrementally in `notebooks/ETL_Climate_Example.ipynb`;
- executed across all mapped target areas by `notebooks/ETL_Climate_Data.ipynb`.

Reusable changes to climate transformation logic should be implemented here rather than duplicated across notebooks.

---

## `eda_utils.py`

### Purpose

This module provides reusable utilities for consistent exploratory analysis and visualization.

It covers descriptive univariate, bivariate, multivariate, and temporal exploration without embedding project-specific modelling decisions.

### Shared visual identity

The project plotting identity is defined centrally in this module.

The palette includes:

- gold;
- teal;
- dark gray;
- medium and light neutral grays;
- supporting darker and lighter variants.

Semantic aliases such as:

```text
GOLD
TEAL
DARK
GRAY_MED
GRAY_LIGHT
```

allow downstream plotting code to express visual intent without repeatedly using raw hexadecimal values.

The module also defines shared sequential and diverging colormaps.

`set_plot_style()` applies the project-wide chart conventions, including:

- minimal white background;
- hidden top and right spines;
- left-oriented bold titles;
- consistent font sizes;
- frameless legends.

### Current capabilities

The utilities include support for:

- required-column validation;
- dataframe diagnostics;
- missing-value summaries;
- zero-value summaries;
- frequency tables;
- readable variable labels;
- variable-type recognition;
- univariate analysis of continuous variables;
- univariate analysis of discrete variables;
- categorical distributions;
- numeric–numeric relationships;
- numeric–categorical comparisons;
- category-conditioned numeric relationships;
- temporal exploration;
- reusable axes so plots can be composed in notebook layouts.

The functions are intended for interactive notebook use and generally combine visual output with short descriptive summaries.

### Design principle

Project colors and plotting conventions should be maintained here rather than redefined independently in each notebook or in `modelling_utils.py`.

This keeps EDA and modelling visualizations consistent.

---

## `modelling_utils.py`

### Purpose

This module contains reusable logic extracted from the quantile-modelling notebook.

It supports the current crop-specific model-development workflow while keeping the notebook focused on experiment order, model comparison, and interpretation.

The module imports the plotting style and semantic color aliases directly from `eda_utils.py`, so there is only one visual source of truth.

### Main exported utilities

The current public functions include:

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
```

### Core quantile modelling

The module provides:

- pinball-loss evaluation;
- standardized `QuantileRegressor` pipelines;
- fold-by-fold temporal evaluation;
- aggregate train and temporal-CV scoring.

The unregularized linear specification uses:

```text
StandardScaler
    ↓
QuantileRegressor
```

Scaling stays inside the pipeline so that it is refitted independently inside each chronological fold.

### Historical yield features

`rolling_history_median()` derives historical medians using only yield values from previous calendar years.

It can operate at different grouping levels, for example:

```text
crop × province
crop × region
```

This avoids using future target observations when constructing historical predictors.

### Temporal validation

`temporal_cv_indices()` converts year-based chronological folds into the positional-index format required by scikit-learn tools.

`temporal_cv_scores()` evaluates each requested quantile separately within the defined chronological folds.

The central assumption is that every validation block must occur strictly after the observations used to fit its model.

### Sequential Forward Selection

`fit_sfs()` runs forward `SequentialFeatureSelector` using:

- Q2 pinball loss as the scoring objective;
- the explicit chronological folds;
- the same linear quantile pipeline used for later evaluation.

The resulting feature subset is model-specific and should not be interpreted as the only informative set for nonlinear estimators.

`selected_feature_table()` provides a compact readable summary of the selected predictors and distinguishes historical from climate variables.

### Native missing-value feature mapping

`native_feature_names()` converts zero-filled linear-model feature names back to their native missing-value versions when a downstream model can consume numerical `NaN` values directly.

This allows CatBoost and TabPFN experiments to preserve missingness information instead of inheriting the imputation required by the linear pipeline.

### L1-regularized quantile regression

The module contains utilities to:

- build standardized L1 quantile-regression pipelines;
- calculate Q2 fold-level losses for candidate `alpha` values;
- choose a regularization strength within a tolerance of the best validation result;
- evaluate the selected regularized specification on train and temporal CV.

### CatBoost Q2

The CatBoost helpers implement the current conservative Q2 workflow.

`make_catboost_q2_model()` creates the base quantile model with:

```text
loss_function = Quantile:alpha=0.5
random_seed = 0
verbose = False
allow_writing_files = False
```

`fit_catboost_q2()`:

1. uses the most recent years inside the training window as an internal early-stopping block;
2. determines the best tree count;
3. refits a fresh model on the complete training window using that tree count.

This prevents the external validation period from influencing early stopping while still allowing all available training observations to contribute to the final fit.

### Quantile post-processing

`correction_function()` and `add_quantile_limits()` enforce the expected ordering:

```text
Q1 <= Q2 <= Q3
```

and derive:

- corrected conditional quantiles;
- predicted interquartile range;
- Tukey-style lower and upper limits.

These utilities are intended for later probabilistic interpretation and anomaly-style diagnostics rather than for changing the underlying model-selection score.

### National aggregation

`aggregate_national_predictions()` converts province-level predicted yields into implied production, aggregates production and cultivated area nationally, and only then reconstructs national yield.

This is preferable to directly averaging provincial yields because provinces have different cultivated areas.

The function also derives national observed and predicted yield series and flags observations outside the predicted Tukey-style limits.

### National forecast visualization

`plot_national_quantile_forecast()` draws, for one crop:

- observed national yield;
- predicted median;
- interquartile band;
- lower and upper outlier limits;
- flagged low and high observations.

The function reuses the project plotting style from `eda_utils.py`.

---

## Import pattern used by the notebooks

The notebooks are expected to run from the `notebooks/` directory and make `src/` available explicitly.

```python
from pathlib import Path
import sys

CURRENT_DIR = Path.cwd().resolve()
PROJECT_ROOT = CURRENT_DIR.parent

SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))
```

The shared utilities can then be imported with:

```python
from eda_utils import *
from modelling_utils import *
```

The project currently favors transparent notebook execution over packaging the repository as an installable library.

## Development conventions

When extending `src/`:

- move logic here when it is reusable or distracts from notebook readability;
- keep experiment-specific control flow in the notebook;
- avoid duplicating plotting colors or style definitions outside `eda_utils.py`;
- keep temporal-validation logic explicit and leakage-safe;
- prefer small functions with clear inputs and outputs;
- document methodological changes that can alter downstream results;
- preserve reproducibility through deterministic seeds where applicable;
- avoid embedding credentials, API tokens, local absolute paths, or private configuration.
