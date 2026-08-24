# AgriClimate Intelligence

Data engineering, exploratory analysis, and probabilistic machine-learning modelling for studying agricultural yields and climate conditions in Italy at subnational level.

> **Work in progress**
>
> This repository documents an active Capstone Project developed within the Executive Master in Data Science at Rome Business School.
>
> The climate and agricultural-production pipelines are implemented, the exploratory analysis and crop-season feature engineering are advanced, and the main quantile-modelling workflow has now progressed through **model selection and final out-of-time evaluation**.
>
> The repository is still evolving toward the final interpretation, consolidation, and communication of the project results.

## Project overview

AgriClimate Intelligence investigates how historical agricultural yields vary across Italian territories and how much additional predictive information can be extracted from climate and environmental conditions.

The practical objective is to build a reproducible workflow that can:

1. collect and harmonize historical climate and agricultural-production data;
2. assess temporal, territorial, and structural data quality;
3. reconstruct agronomically meaningful crop seasons;
4. engineer climate and historical yield predictors;
5. estimate crop yield through chronologically validated models;
6. quantify predictive uncertainty through conditional quantiles;
7. compare parsimonious statistical models with nonlinear tabular approaches;
8. select crop-specific specifications without using the final test period;
9. evaluate the frozen models on a genuinely out-of-time benchmark;
10. derive coherent probabilistic diagnostics and aggregate national representations;
11. support later model interpretation and decision-oriented communication.

The project follows an iterative CRISP-DM logic. Findings from EDA and modelling can lead to revisions of feature definitions, validation choices, or analytical assumptions, while the final test period is kept isolated from model-development decisions.

## Current project status

| Area | Current status |
| --- | --- |
| Project scope | Defined and refined through the evidence emerging from the data |
| Raw climate storage | Implemented in Google Cloud Storage |
| Climate ETL | Implemented for the mapped Italian provincial files |
| Production ETL | Implemented, including territorial harmonization and quality flags |
| Curated cloud tables | Available in BigQuery |
| Exploratory data analysis | Advanced |
| Crop-season feature engineering | Implemented for the current modelling dataset |
| Climate-yield bivariate analysis | Implemented |
| Integrated modelling dataset | Built for the current modelling workflow |
| Naive persistence benchmark | Implemented |
| Historical quantile baseline | Implemented |
| Sequential Forward Selection | Implemented and frozen as crop-specific selected sets |
| L1 quantile-regression experiment | Implemented |
| CatBoost comparison | Implemented |
| TabPFN comparison | Implemented |
| Outer temporal validation | Implemented on 2016-2018 |
| Temporal robustness checks | Implemented |
| Final crop-specific model selection | **Completed** |
| Final 2019-2022 test evaluation | **Completed** |
| Quantile post-processing and distribution diagnostics | Implemented |
| Geographic outlier diagnostics | Implemented |
| National aggregation of predictions | Implemented |
| Model interpretation | Partial / ongoing |
| Final project synthesis and communication | **WIP** |

This table describes the state currently visible in the repository and should evolve with the project.

## Current analytical scope

The modelling workflow focuses on three crops:

- **Durum wheat**
- **Soft wheat**
- **Grain maize**

The modelling observation unit is:

```text
province × crop × harvest year
```

The available information includes:

- historical agricultural yield;
- cultivated area and production;
- province and region;
- lagged and rolling historical yield information;
- crop-phase climate and environmental indicators;
- altitude characteristics;
- climate-event frequency and duration measures.

Current-year `area`, `production`, and `yield` are not used as model predictors.

## Data architecture

The project combines Google Cloud resources with locally executed notebooks.

```text
Raw source data
      │
      ├── Climate files in Google Cloud Storage
      └── Agricultural-production source
      │
      ▼
ETL notebooks + reusable Python transformations
      │
      ▼
Curated datasets
      │
      ├── BigQuery curated tables
      └── Optional local CSV exports
      │
      ▼
EDA + crop-season feature engineering
      │
      ▼
Local modelling dataset
      │
      ▼
Temporal model development
      │
      ▼
Outer validation and model selection
      │
      ▼
Frozen model specifications
      │
      ▼
2019-2022 final test
      │
      ▼
Distributional diagnostics and national aggregation
```

The Google Cloud project is:

```text
Project name: AgriClimate Intelligence
Project ID: agriclimate-intelligence
```

The main curated BigQuery resources used by the analytical workflow are:

```text
agriclimate-intelligence.curated.climate_full_dataset_v1
agriclimate-intelligence.curated.production_full_dataset_v1
```

Raw datasets, generated analytical datasets, credentials, and private configuration are not versioned in the public repository.

## Data currently processed

### Climate data

The raw climate files contain daily gridded observations with multiple cells for each source province.

The transformation works with variables including:

- grid-cell identifier;
- latitude and longitude;
- altitude;
- date;
- minimum, average, and maximum temperature;
- wind speed;
- vapour pressure;
- precipitation;
- reference evapotranspiration;
- solar radiation.

The climate pipeline derives monthly provincial indicators that retain information about:

- average conditions;
- local extremes;
- spatial variability;
- territorial share affected by an event;
- event frequency;
- consecutive-event duration;
- precipitation totals and intensity;
- evapotranspiration and radiation;
- static altitude characteristics.

The curated climate history spans **1980-2025**.

### Agricultural production data

The production workflow processes historical information on:

- cultivated area;
- total production;
- agricultural yield;
- crop;
- year;
- source territory;
- territorial coverage;
- reconstruction and quality status.

The current modelling horizon uses agricultural observations through **2022**.

Dedicated quality fields preserve information about missing source components, structural zeroes, reconstructed territories, and other data-quality conditions.

## Exploratory analysis

`notebooks/EDA_AgriClimate_Intelligence.ipynb` is the main analytical notebook preceding model development.

Its current role includes:

- structural and consistency checks on the curated data;
- temporal and territorial completeness analysis;
- production and climate univariate exploration;
- yield distribution analysis;
- yield trends across territories and macro-areas;
- robust trend estimation;
- partial-autocorrelation summaries;
- altitude analysis;
- crop-season and crop-phase climate reconstruction;
- bivariate analysis between yield and engineered predictors;
- comparison of environmental patterns across crops and phases;
- preparation of the modelling dataset.

The EDA should be read as the analytical justification for the modelling representation rather than as an isolated descriptive report.

## Quantile modelling

`notebooks/ML_Quantile_Modelling.ipynb` is the main modelling notebook.

The objective is to estimate conditional yield quantiles:

- **Q1** = 0.25 quantile;
- **Q2** = 0.50 quantile / conditional median;
- **Q3** = 0.75 quantile.

Q2 is the primary model-selection target. Q1 and Q3 are retained to evaluate the broader conditional yield distribution.

Performance is evaluated with **pinball loss**.

### Modelling dataset

After removing observations without an observed target, the workflow uses:

```text
7,576 observations
4 historical predictors
192 crop-phase climate predictors
196 SFS candidate predictors
```

### Temporal design

All model development is chronological.

The development period ends in **2015** and uses three expanding validation folds:

```text
train through 2006 → validate on 2007-2009
train through 2009 → validate on 2010-2012
train through 2012 → validate on 2013-2015
```

The later **2016-2018** block is used as outer validation and is the last period allowed to inform model selection.

The final benchmark is:

```text
2019-2022 → final out-of-time test
```

The 2019-2022 observations were not used for feature selection, model-family comparison, tuning, early stopping, or the final choice among competing specifications.

### Modelling sequence

The current notebook develops the problem progressively through:

1. a naive persistence benchmark based on the previous year's yield;
2. a historical linear quantile baseline;
3. Sequential Forward Selection over historical and climate predictors;
4. fold-level temporal-stability analysis;
5. L1-regularized linear quantile regression;
6. CatBoost as a conventional nonlinear tabular model;
7. outer validation on 2016-2018;
8. TabPFN as a tabular foundation model;
9. temporal robustness and quantile-behaviour tie-breakers;
10. final crop-specific model selection;
11. refitting of the frozen specifications on all admissible 1995-2018 data;
12. one-time evaluation on the untouched 2019-2022 final test;
13. quantile correction and distributional diagnostics;
14. geographic analysis of final-test outliers;
15. direct interpretation of the final linear model;
16. area-weighted national aggregation and visualization.

The naive persistence benchmark is used only as a minimum forecasting-skill hurdle. The historical linear model improves Q2 temporal-CV loss over this benchmark for all three crops.

## Final model selection

Model selection is now frozen.

The selected specifications are:

| Crop | Final model | Feature representation |
| --- | --- | --- |
| Durum wheat | `Linear H` | Four historical predictors |
| Grain maize | `TabPFN SFS` | Previously selected SFS feature set |
| Soft wheat | `TabPFN Full` | Complete candidate feature set |

The final choices were resolved before the 2019-2022 benchmark was evaluated.

For close outer-validation comparisons, the notebook uses additional pre-test evidence such as temporal robustness and quantile behaviour rather than automatically choosing the numerically best single validation score.

## Final out-of-time test

After model selection, the 2016-2018 validation observations are incorporated into the final training data.

The frozen models are then fitted on **1995-2018** and evaluated once on **2019-2022**.

Final pinball losses are:

| Crop | Model | Test Q1 | Test Q2 | Test Q3 |
| --- | --- | ---: | ---: | ---: |
| Durum wheat | `Linear H` | 0.1756 | **0.2106** | 0.1898 |
| Grain maize | `TabPFN SFS` | 0.3348 | **0.3759** | 0.2965 |
| Soft wheat | `TabPFN Full` | 0.1978 | **0.2393** | 0.2026 |

These values are calculated from the **raw model predictions** and represent the official final predictive assessment.

The subsequent quantile corrections are used only to construct coherent probabilistic outputs and do not alter these final scores.

## Distributional diagnostics

The final-test workflow also evaluates the predictions as conditional distributions rather than only as point estimates.

The notebook:

- checks raw Q1-Q2-Q3 ordering;
- enforces non-negative and monotonically ordered quantiles for downstream interpretation;
- derives the predicted interquartile range;
- constructs Tukey-style conditional lower and upper limits;
- evaluates empirical Q1, Q2, and Q3 coverage;
- evaluates Q1-Q3 interval coverage;
- counts low and high final-test outliers;
- examines their geographic distribution.

Only a small number of raw quantile-ordering violations occur, all in the final durum-wheat linear predictions; they are corrected for the downstream distributional representation.

## Validation-to-test generalization

The notebook also compares the final Q2 loss with the corresponding pre-test outer-validation result.

The observed changes are:

- **Durum wheat:** modestly higher final-test loss;
- **Grain maize:** lower final-test loss;
- **Soft wheat:** moderately higher final-test loss.

These comparisons are treated as temporal-generalization evidence and do not reopen model selection.

## Model interpretation

The final durum-wheat model is an unregularized linear quantile regression.

A dedicated check confirms that scaling and non-scaling formulations are numerically equivalent for this specification. The final implementation therefore omits `StandardScaler`, allowing coefficients and intercepts to be read directly in the original feature units.

Interpretation of the more complex TabPFN models remains a natural next stage of the project.

## National aggregation

The primary modelling output remains the **province-level prediction**.

For national summaries, provincial yields are not averaged directly. Each predicted yield is first converted to implied production using cultivated area, production is aggregated across provinces, and national yield is then reconstructed as:

```text
total predicted production / total cultivated area
```

This procedure is applied to Q1, Q2, Q3, and the conditional outlier limits.

The resulting national quantile series are therefore **area-weighted aggregates of province-level quantile forecasts**, not quantiles estimated from a separate national predictive distribution.

National plots compare:

- observed yield;
- predicted median;
- Q1-Q3 band;
- Tukey-style conditional limits.

## Repository structure

```text
agriclimate-intelligence/
├── .github/
│   └── CODEOWNERS
├── notebooks/
│   ├── EDA_AgriClimate_Intelligence.ipynb
│   ├── ETL_Climate_Data.ipynb
│   ├── ETL_Climate_Example.ipynb
│   ├── ETL_Production_Data.ipynb
│   ├── ML_Quantile_Modelling.ipynb
│   └── README.md
├── src/
│   ├── __init__.py
│   ├── eda_utils.py
│   ├── modelling_utils.py
│   ├── province_transformation.py
│   └── README.md
├── .gitignore
└── README.md
```

See:

- `notebooks/README.md` for the purpose, inputs, outputs, and current status of each notebook;
- `src/README.md` for the reusable Python modules.

## Reusable source code

### `province_transformation.py`

Reusable climate-data validation and transformation from daily gridded observations to monthly provincial indicators.

### `eda_utils.py`

Shared descriptive-analysis and plotting utilities, including the central project visual identity used across EDA and modelling charts.

### `modelling_utils.py`

Reusable functions for:

- quantile-regression pipelines;
- chronological cross-validation;
- rolling historical medians;
- Sequential Forward Selection;
- L1 quantile regression;
- CatBoost Q2 fitting;
- quantile post-processing;
- national-level aggregation;
- national quantile-forecast visualization.

`modelling_utils.py` reuses the palette and plotting style defined in `eda_utils.py` rather than maintaining a second visual configuration.

## Running the project

### Expected local layout

Some workflows use locally generated files that are intentionally excluded from Git.

```text
agriclimate-intelligence/
├── data/
│   └── modelling_data.csv
├── notebooks/
└── src/
```

### Main dependencies

The exact imports vary by notebook, but the current workflows use packages including:

```text
pandas
numpy
scipy
statsmodels
matplotlib
seaborn
scikit-learn
catboost
python-dotenv
tabpfn-client
google-cloud-bigquery
google-cloud-storage
gcsfs
jupyter
```

A formal dependency file has not yet been added, so the repository is not yet fully reproducible from a clean environment without inspecting notebook imports.

### Google Cloud authentication

For notebooks that read from Google Cloud, authenticate locally with Application Default Credentials:

```bash
gcloud auth application-default login
```

The authenticated account must have permission to read the required Cloud Storage objects and BigQuery tables.

### TabPFN authentication

The modelling notebook uses the TabPFN client.

The access token should be stored locally in environment configuration and **must never be committed to Git**.

## Suggested reading order

```text
1. notebooks/ETL_Climate_Example.ipynb
2. src/province_transformation.py
3. notebooks/ETL_Climate_Data.ipynb
4. notebooks/ETL_Production_Data.ipynb
5. src/eda_utils.py
6. notebooks/EDA_AgriClimate_Intelligence.ipynb
7. src/modelling_utils.py
8. notebooks/ML_Quantile_Modelling.ipynb
```

The ETL workflows produce the curated inputs. The EDA integrates and interprets them, engineers the crop-season representation, and prepares the modelling table. The modelling notebook then performs chronological model development, model selection, final out-of-time evaluation, and distributional diagnostics.

## Reproducibility and current limitations

The repository is still evolving. Current limitations include:

- no formal dependency or environment file;
- no automated test suite;
- no continuous-integration workflow;
- some configuration remains inside notebooks;
- the project is not packaged as an installable Python package;
- raw and generated analytical datasets are not distributed through the repository;
- Google Cloud access is required for the default ETL/EDA cloud path;
- TabPFN experiments require separate authenticated API access;
- interpretation of the nonlinear final models is not yet fully developed;
- final project synthesis and communication are still in progress;
- predictive relationships should not automatically be interpreted as causal.

## Collaboration

The `main` branch is protected. Changes should be developed on a dedicated branch and merged through a pull request.

Example:

```bash
git checkout -b feature/descriptive-name
git add .
git commit -m "Describe the change"
git push -u origin feature/descriptive-name
```

Methodological changes should state clearly:

- what definition, feature, model, or transformation changed;
- why it changed;
- which outputs are affected;
- whether downstream datasets or notebooks must be regenerated.

## Academic context

This repository supports the Capstone Project developed within the **Executive Master in Data Science at Rome Business School**.

Its primary purpose is to document the technical workflow, methodological decisions, intermediate evidence, final predictive evaluation, and subsequent interpretation in a reproducible and transparent way.
