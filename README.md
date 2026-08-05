# AgriClimate Intelligence

Data engineering, exploratory analysis, and machine-learning development for studying the relationship between climate conditions and agricultural yields in Italy at subnational level.

> [!IMPORTANT]
> **This repository documents an active work in progress.**
>
> The climate and agricultural-production ETL pipelines are available, and the exploratory analysis has reached an advanced but not final stage. The integrated crop-season dataset, bivariate analysis, predictive modeling, evaluation, and final decision-support outputs are still under development.
>
> The repository should therefore be read as the evolving technical workspace of the project, not as a completed analytical product.

## Project overview

AgriClimate Intelligence is a Capstone Project developed within the Executive Master in Data Science at Rome Business School.

The practical aim is to build a reproducible workflow that can progressively:

1. collect and harmonize historical climate and agricultural-production data;
2. evaluate their territorial and temporal coverage;
3. describe patterns, anomalies, missing observations, and data-quality limitations;
4. construct province–crop–season observations suitable for modeling;
5. estimate agricultural yield using climate, environmental, temporal, and territorial information;
6. interpret the principal factors associated with yield variability;
7. evaluate the robustness and practical limits of the resulting models;
8. communicate the results through reproducible notebooks, visualizations, and decision-oriented outputs.

The current work is focused primarily on the historical relationship between climate conditions and agricultural yield. Probabilistic forecasting, revenue scenarios, and broader decision-support applications remain possible extensions rather than completed components.

## Current project status

The repository currently sits between the **Data Understanding** and **Data Preparation** phases of CRISP-DM.

| Area | Current status |
|---|---|
| Project scope | Defined at a general level and still being refined according to the evidence emerging from the data |
| Raw data storage | Implemented in Google Cloud Storage |
| Climate ETL | Implemented for the mapped Italian provincial files |
| Production ETL | Implemented, including territorial harmonization and quality flags |
| Curated cloud tables | Available in BigQuery and used by the EDA notebook |
| Exploratory data analysis | Advanced, but still in progress |
| Yield trend analysis | Present |
| Yield autocorrelation analysis | Present through PACF-based summaries |
| Crop-season reconstruction | Not yet implemented |
| Climate–yield bivariate analysis | Not yet implemented |
| Integrated modeling dataset | Not yet finalized |
| Baseline models | Not yet implemented |
| Machine-learning models | Not yet implemented |
| Model evaluation and interpretation | Not yet implemented |
| Final report or decision-support output | Not yet implemented |

This table describes the state visible in the repository at the time of writing. It should be updated as new phases are added.

## Methodological framework

The project follows the iterative **CRISP-DM** framework.

### 1. Business Understanding

Define the analytical problem, practical scope, constraints, and criteria by which the work should be evaluated.

### 2. Data Understanding

Inspect the available sources, variables, spatial and temporal granularity, data quality, completeness, and informative value.

### 3. Data Preparation

Validate, clean, aggregate, and align climate and production data; define crop seasons; engineer features; and construct the modeling target.

### 4. Modeling

Establish transparent baselines and compare suitable supervised models for agricultural-yield estimation. Optional unsupervised territorial analysis may be considered only if supported by the data and project needs.

### 5. Evaluation

Assess predictive performance, temporal and territorial robustness, error patterns, interpretability, and agronomic plausibility.

### 6. Deployment and Communication

Translate the work into reproducible pipelines, notebooks, visualizations, documented findings, and possible decision-support outputs.

These phases are not treated as strictly linear. Findings from the EDA or modeling stages may require revisiting earlier assumptions, source selection, feature definitions, or territorial filters.

## Current analytical scope

The repository currently works with:

- historical climate and environmental observations;
- historical agricultural area, production, and yield data;
- Italian provinces or harmonized subnational production areas;
- monthly provincial climate indicators;
- annual province–crop production observations;
- multiple crops within a common analytical structure.

The final modeling scope may be narrower than the full curated datasets. Crop selection, admissible observations, quality filters, and seasonal windows will be decided through the ongoing analysis rather than assumed in advance.

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
│   └── README.md
├── src/
│   ├── __init__.py
│   ├── eda_utils.py
│   └── province_transformation.py
├── .gitignore
└── README.md
```

Raw datasets and generated analytical datasets are not versioned in the public repository.

See:

- [`notebooks/README.md`](notebooks/README.md) for the role and status of each notebook;
- [`src/README.md`](src/README.md) for the reusable Python modules;
- [`.github/README.md`](.github/README.md) for repository-governance notes.

## Data architecture

The project currently uses Google Cloud together with locally executed notebooks.

```text
Google Cloud Storage
        │
        │ raw compressed source data
        ▼
ETL notebooks and reusable Python transformations
        │
        ▼
Curated datasets
        │
        ├── optional local CSV exports
        └── BigQuery curated tables
                 │
                 ▼
        Exploratory analysis and future modeling
```

The Google Cloud project is:

```text
Project name: AgriClimate Intelligence
Project ID: agriclimate-intelligence
```

The EDA notebook currently uses the following BigQuery resources by default:

```text
agriclimate-intelligence.curated.climate_full_dataset_v1
agriclimate-intelligence.curated.production_full_dataset_v1
```

Local CSV copies can be used as an alternative when available.

No credentials, service-account files, private configuration, or restricted source data should be committed to the repository.

## Data currently processed

### Climate data

The raw climate files contain daily gridded observations, with multiple cells for each source province.

The fields processed by the current transformation include:

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

The climate pipeline converts these observations into monthly provincial indicators while retaining information about:

- average conditions;
- local extremes;
- spatial variability;
- territorial share affected by an event;
- event frequency;
- consecutive-event duration;
- precipitation, evapotranspiration, and radiation totals;
- static altitude characteristics.

The resulting curated climate dataset currently contains 74 columns and covers monthly observations from 1980 to 2025.

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

The output is a long-format province–year–crop panel. It retains dedicated `q_*` fields so that missing source components, structural zeroes, calculated territories, and other quality conditions are not hidden during later analysis.

## Implemented workflows

### Climate ETL

The climate workflow currently:

- reads 107 compressed provincial source files from Google Cloud Storage;
- validates schema, dates, numeric values, missing values, duplicate keys, and grid consistency;
- handles source territories that must be combined to match production areas;
- corrects inconsistent ordering of minimum, average, and maximum temperatures where possible;
- calculates historical monthly reference thresholds;
- identifies fixed-threshold and percentile-based climate events;
- derives daily provincial indicators from cell-level observations;
- aggregates climate information to province and month;
- exports a consolidated curated climate dataset.

### Production ETL

The production workflow currently:

- reads the production source from Google Cloud Storage;
- inspects the source structure and relevant variables;
- distinguishes missing observations from structural zeroes;
- harmonizes changing or incompatible territorial definitions;
- reconstructs selected production areas where required;
- calculates yield from aggregated production and area;
- creates provenance and quality indicators;
- validates the final province–year–crop key;
- exports a curated production panel.

### Exploratory data analysis

The EDA notebook currently:

- reads the two curated datasets from BigQuery by default;
- supports optional local CSV input;
- checks data structure and internal consistency;
- reviews temporal and territorial coverage;
- analyses missing and absent observations;
- performs univariate exploration of production and climate fields;
- examines agricultural-yield distributions;
- analyses yield trends within province–crop series;
- uses Theil–Sen trend estimates to obtain robust long-term slopes;
- summarises partial autocorrelation across multiple province–crop series;
- identifies the preparation steps still required before climate–yield modeling.

The EDA is not complete. Crop-season feature construction and bivariate analysis between engineered climate features and the yield target are explicitly left for subsequent development.

## Current EDA boundary

The current EDA is designed to answer questions such as:

- Are the curated tables structurally coherent?
- Which province–crop–year combinations are present or absent?
- How complete are the production series?
- Which quality conditions affect the target observations?
- How is yield distributed across crops and territories?
- Which series show increasing, decreasing, or weak trends?
- Is there evidence that past yield values may provide useful lagged information?

It does not yet answer the final modeling questions:

- Which seasonal climate variables are associated with yield?
- Which climate windows should be retained?
- Which features remain useful after controlling for trend and territory?
- What validation design is most appropriate?
- Which model performs best?
- How uncertain are its predictions?
- Can the fitted relationships support scenario analysis?

## Next development stages

### 1. Complete the EDA

- finish the review of relevant climate features;
- consolidate findings on data completeness and admissible observations;
- document exclusions and quality filters;
- evaluate redundancy and scale differences among variables.

### 2. Build crop-season features

For a yield target in harvest year `X`, climate observations will initially be aligned to an agricultural window approximately spanning:

```text
September of year X-1 → August of year X
```

The precise feature windows may be refined by crop and by the evidence emerging from the data.

Potential features include:

- seasonal averages and totals;
- values by crop-development phase;
- extreme-event counts;
- longest extreme-event sequences;
- spatial-variability indicators;
- evapotranspiration and radiation measures;
- lagged yield information where justified;
- trend and time indicators;
- stable territorial characteristics.

### 3. Construct the integrated modeling dataset

The expected observation unit is:

```text
province × crop × harvest year
```

The dataset will combine:

- yield target;
- crop identifier;
- territory;
- season identifier;
- engineered climate variables;
- possible lagged target variables;
- production-data quality indicators.

### 4. Establish baselines and validation

Before complex modeling, the project will define:

- historical or persistence baselines;
- simple statistical baselines;
- temporal validation;
- possible territorial generalization checks;
- suitable error metrics;
- comparison rules that avoid leakage.

### 5. Develop and evaluate models

Candidate tabular models will be selected after the final dataset is available. The project may compare pooled and crop-specific alternatives and use interpretability methods such as feature importance and SHAP.

Probabilistic or quantile predictions will be considered only if supported by the available observations and validation results.

## Running the current repository

### Main dependencies

The notebooks currently use packages including:

```text
pandas
numpy
scipy
statsmodels
matplotlib
seaborn
google-cloud-bigquery
google-cloud-storage
gcsfs
jupyter
```

The exact imports vary by notebook.

A formal dependency file has not yet been added. The repository is therefore not yet fully reproducible from a clean environment without manual inspection of notebook imports.

### Authentication

Authenticate locally with Google Cloud Application Default Credentials:

```bash
gcloud auth application-default login
```

The authenticated account must have access to the required Cloud Storage objects and BigQuery tables.

### Suggested reading order

To understand the current project:

```text
1. notebooks/ETL_Climate_Example.ipynb
2. src/province_transformation.py
3. notebooks/ETL_Climate_Data.ipynb
4. notebooks/ETL_Production_Data.ipynb
5. src/eda_utils.py
6. notebooks/EDA_AgriClimate_Intelligence.ipynb
```

The two ETL workflows are logically independent. The EDA consumes their curated outputs.

## Reproducibility and known limitations

The repository is being actively reorganized and documented. Current limitations include:

- no formal dependency or environment file;
- no automated test suite;
- no continuous-integration workflow;
- some configuration remains inside notebooks;
- the project is not packaged as an installable Python package;
- raw data are not distributed through this repository;
- Google Cloud access is required for the default execution path;
- no integrated modeling dataset is yet published;
- no final model or performance result is yet available;
- future model relationships should not automatically be interpreted as causal.

## Collaboration

The `main` branch is protected. Contributors should work on a dedicated branch and open a pull request for review.

Example:

```bash
git checkout -b feature/descriptive-name
git add .
git commit -m "Describe the change"
git push -u origin feature/descriptive-name
```

Methodological changes should state clearly:

- what definition or transformation changed;
- why it changed;
- which outputs are affected;
- whether downstream tables or notebooks must be regenerated.

## Academic context

This repository supports the Capstone Project:

**Data Driven Analysis for Climate Smart Agriculture: Strategy, Operational Resilience, and Agricultural Yield Analysis in a Changing Climate**

The project is associated with the Executive Master in Data Science at Rome Business School.

## License

No open-source license is currently included. Public visibility alone does not grant explicit reuse, redistribution, or modification rights.
