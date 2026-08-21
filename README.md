# AgriClimate Intelligence

Data engineering, exploratory analysis, and machine-learning development for studying the relationship between climate conditions and agricultural yields in Italy at subnational level.

> **Work in progress**
>
> This repository documents an active Capstone Project. The climate and agricultural-production pipelines are implemented, the exploratory analysis has reached the modelling hand-off stage, and a dedicated quantile-modelling workflow is now under development.
>
> Model selection is **not yet final**. In particular, the 2019–2022 out-of-time test period remains intentionally untouched until the crop-specific model-selection rule has been fixed.

## Project overview

AgriClimate Intelligence is a Capstone Project developed within the Executive Master in Data Science at Rome Business School.

The project investigates how historical agricultural yields vary across Italian territories and how much additional predictive information can be extracted from climate and environmental conditions.

The practical objective is to build a reproducible workflow that can:

1. collect and harmonize historical climate and agricultural-production data;
2. assess temporal, territorial, and structural data quality;
3. reconstruct agronomically meaningful crop seasons;
4. engineer climate and historical yield predictors;
5. estimate crop yield through temporally validated predictive models;
6. quantify predictive uncertainty through conditional quantiles;
7. compare parsimonious statistical models with nonlinear tabular approaches;
8. evaluate temporal robustness before touching the final test period;
9. support later interpretation and decision-oriented communication.

The project follows an iterative CRISP-DM logic: findings from EDA and modelling can lead to revisions of feature definitions, validation choices, or modelling assumptions.

## Current project status

| Area | Current status |
| --- | --- |
| Project scope | Defined and refined through the evidence emerging from the data |
| Raw climate storage | Implemented in Google Cloud Storage |
| Climate ETL | Implemented for the mapped Italian provincial files |
| Production ETL | Implemented, including territorial harmonization and quality flags |
| Curated cloud tables | Available in BigQuery |
| Exploratory data analysis | Advanced and currently used as the analytical hand-off to modelling |
| Crop-season feature engineering | Implemented for the current modelling dataset |
| Climate–yield bivariate analysis | Implemented in the EDA workflow |
| Integrated modelling dataset | Built locally for the current modelling experiments |
| Historical quantile baseline | Implemented |
| Sequential feature selection | Implemented and retained as fixed selected feature sets |
| L1 quantile-regression experiment | Implemented |
| CatBoost comparison | Implemented for the current Q2 experiments |
| TabPFN comparison | Implemented for the current candidate configurations |
| Outer temporal validation | Implemented on 2016–2018 |
| Temporal robustness checks | Implemented for the strongest competing specifications |
| Final crop-specific model selection | **Open / WIP** |
| Final 2019–2022 test evaluation | **Not yet performed** |
| Final interpretation and communication | Not yet completed |

This table describes the state visible in the repository at the time of writing and should evolve with the project.

## Current analytical scope

The current modelling work focuses on three crops:

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
- monthly climate and environmental indicators;
- crop-season and crop-phase aggregations;
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
EDA and crop-season feature engineering
      │
      ▼
Local modelling dataset
      │
      ▼
Temporal model development and validation
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

The curated climate history spans **1980–2025**.

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

The production pipeline preserves dedicated quality fields so that missing source components, structural zeroes, reconstructed territories, and other quality conditions are not silently lost during downstream analysis.

## Exploratory analysis

`notebooks/EDA_AgriClimate_Intelligence.ipynb` is the main analytical notebook before modelling.

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
- preparation of the modelling dataset used by the machine-learning notebook.

The EDA should be read as the analytical justification for the modelling choices rather than as a separate final report.

## Quantile modelling

`notebooks/ML_Quantile_Modelling.ipynb` is the current main modelling notebook.

The objective is not only to estimate a central yield prediction, but to model conditional yield quantiles:

- **Q1** = 0.25 quantile;
- **Q2** = 0.50 quantile / conditional median;
- **Q3** = 0.75 quantile.

Q2 is the primary model-selection target, while Q1 and Q3 are retained where useful to assess the broader conditional distribution.

### Temporal design

All model development is chronological.

The development period ends in **2015** and uses three expanding validation folds:

```text
train through 2006 → validate on 2007–2009
train through 2009 → validate on 2010–2012
train through 2012 → validate on 2013–2015
```

A later block is then used as outer validation:

```text
2016–2018 → model-selection validation
```

The final benchmark is:

```text
2019–2022 → untouched final test
```

The 2019–2022 period is intentionally excluded from training, feature selection, hyperparameter decisions, and current model selection.

### Current modelling sequence

The notebook currently compares:

1. a scaled historical linear quantile baseline;
2. linear quantile regression with Sequential Forward Selection;
3. L1-regularized linear quantile regression;
4. CatBoost as a conventional nonlinear tabular model;
5. TabPFN as a tabular foundation model;
6. temporal robustness checks on the strongest competing specifications.

The current modelling table contains **7,576 usable target observations**. The candidate feature pool contains **4 historical predictors** and **192 crop-phase climate predictors**.

The SFS search is computationally expensive and is therefore not rerun on every notebook execution. The selected crop-specific feature sets are stored explicitly and reused in the subsequent experiments.

### Current modelling boundary

The notebook deliberately ends before final test evaluation.

At the current stage:

- the evidence for durum wheat is already concentrated around a parsimonious historical linear specification;
- grain maize still requires a final rule for choosing between the strongest linear and TabPFN alternatives;
- soft wheat still presents a trade-off between average temporal robustness and stronger performance in the most recent validation period.

These are **intermediate model-selection findings**, not final test conclusions.

The final selection rule must be fixed before the 2019–2022 benchmark is evaluated.

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

- `notebooks/README.md` for the purpose, inputs, outputs, and status of each notebook;
- `src/README.md` for the reusable Python modules.

## Reusable source code

The `src/` directory currently separates three main responsibilities:

### `province_transformation.py`

Reusable climate-data validation and transformation from daily gridded observations to monthly provincial indicators.

### `eda_utils.py`

Shared descriptive-analysis and plotting utilities, including the central project visual identity used across EDA and modelling charts.

### `modelling_utils.py`

Reusable functions for:

- quantile-regression pipelines;
- temporal cross-validation;
- rolling historical medians;
- Sequential Forward Selection;
- L1 quantile regression;
- CatBoost Q2 fitting;
- quantile post-processing;
- national-level aggregation;
- national quantile-forecast visualization.

`modelling_utils.py` deliberately reuses the palette and plotting style defined in `eda_utils.py` rather than maintaining a second visual configuration.

## Running the project

### Expected local layout

Some workflows use local generated files that are intentionally excluded from Git.

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

The modelling notebook uses the TabPFN client for the current foundation-model experiments.

The access token should be stored locally in environment configuration and **must never be committed to Git**.

## Suggested reading order

For a complete view of the current project:

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

The ETL workflows produce the curated inputs. The EDA integrates and interprets them, engineers the crop-season representation, and prepares the modelling table. The modelling notebook then performs chronological model development and model selection.

## Reproducibility and known limitations

The repository is still evolving. Current limitations include:

- no formal dependency or environment file;
- no automated test suite;
- no continuous-integration workflow;
- some configuration remains inside notebooks;
- the project is not packaged as an installable Python package;
- raw and generated analytical datasets are not distributed through the repository;
- Google Cloud access is required for the default ETL/EDA cloud path;
- TabPFN experiments require separate authenticated API access;
- the final crop-specific model choices are not yet frozen;
- the 2019–2022 final test has not yet been evaluated;
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

Its primary purpose is to document the technical workflow, methodological decisions, intermediate evidence, and final modelling process in a reproducible and transparent way.
