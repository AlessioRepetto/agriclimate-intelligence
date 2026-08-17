# AgriClimate Intelligence

Data engineering, exploratory analysis, feature engineering, and machine-learning development for studying the relationship between climate conditions and agricultural yields in Italy at subnational level.

> [!IMPORTANT]
> **This repository documents an active work in progress.**
>
> The climate and agricultural-production ETL pipelines are implemented, and the exploratory analysis now includes crop-season reconstruction, phase-based climate feature engineering, and climate–yield bivariate analysis.
>
> The analytical dataset and feature-selection process are still being refined. Predictive modeling, model evaluation, interpretation, and final decision-support outputs have not yet been completed.

## Project overview

AgriClimate Intelligence is a Capstone Project developed within the Executive Master in Data Science at Rome Business School.

The project aims to build a reproducible workflow that can progressively:

1. collect and harmonize historical climate and agricultural-production data;
2. evaluate territorial and temporal coverage and data quality;
3. reconstruct agriculturally meaningful crop seasons;
4. engineer climate and environmental features over crop-development phases;
5. investigate their relationship with agricultural yield;
6. construct modeling-ready province–crop–year observations;
7. estimate agricultural yield using suitable machine-learning models;
8. interpret the main factors associated with yield variability;
9. evaluate predictive robustness and practical limitations.

The current work focuses on historical relationships between climate conditions and agricultural yield. Forecasting, scenario analysis, and broader decision-support applications remain possible later extensions.

## Current project status

The project is currently in the **Data Preparation** stage of CRISP-DM, following an extensive Data Understanding phase. The first modeling stage has not yet started.

| Area                                    | Current status                                   |
| --------------------------------------- | ------------------------------------------------ |
| Project scope                           | Defined and refined through the ongoing analysis |
| Raw data storage                        | Implemented in Google Cloud Storage              |
| Climate ETL                             | Implemented                                      |
| Production ETL                          | Implemented                                      |
| Curated cloud tables                    | Available in BigQuery                            |
| Data-quality and completeness analysis  | Implemented                                      |
| Yield trend analysis                    | Implemented                                      |
| Yield autocorrelation analysis          | Implemented through PACF summaries               |
| Crop-season reconstruction              | Implemented                                      |
| Phase-based climate feature engineering | Implemented                                      |
| Climate–yield bivariate analysis        | Implemented                                      |
| Crop-specific feature screening         | In progress                                      |
| Integrated analytical dataset           | Implemented and still being refined              |
| Final training dataset                  | Not yet frozen                                   |
| Baseline models                         | Not yet implemented                              |
| Machine-learning models                 | Not yet implemented                              |
| Model evaluation and interpretation     | Not yet implemented                              |
| Final report / decision-support output  | Not yet implemented                              |

The repository should therefore be read as the evolving technical workspace of the project rather than as a completed analytical product.

## Methodological framework

The project follows the iterative **CRISP-DM** framework.

### 1. Business Understanding

Define the analytical problem, practical scope, constraints, and criteria by which the work should be evaluated.

### 2. Data Understanding

Inspect available sources, variables, spatial and temporal granularity, completeness, data quality, and informative value.

### 3. Data Preparation

Validate and harmonize the source data, align climate observations with crop seasons, engineer features, integrate climate and production information, and prepare the modeling target.

### 4. Modeling

Establish transparent baselines and compare suitable supervised models for agricultural-yield estimation.

### 5. Evaluation

Assess predictive performance, temporal and territorial robustness, error patterns, interpretability, and agronomic plausibility.

### 6. Deployment and Communication

Translate the work into reproducible pipelines, documented analyses, visualizations, and possible decision-support outputs.

The phases are not strictly linear. Findings from the EDA, feature engineering, or future modeling stages may require revisiting previous assumptions and transformations.

## Current analytical scope

The repository currently works with:

* historical climate and environmental observations;
* historical agricultural area, production, and yield data;
* Italian provinces or harmonized subnational production areas;
* monthly provincial climate indicators;
* annual province–crop production observations;
* crop-specific agricultural calendars;
* climate features aggregated over crop-development phases;
* production variables and lagged production information;
* multiple crops analysed within a common workflow.

The final modeling scope may be narrower than the full curated datasets. Feature selection and admissible observations are still being refined through the exploratory analysis.

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
│   ├── province_transformation.py
│   └── README.md
├── .gitignore
└── README.md
```

Raw datasets and generated analytical datasets are not versioned in the public repository.

See:

* [`notebooks/README.md`](notebooks/README.md) for the role and current status of each notebook;
* [`src/README.md`](src/README.md) for the reusable Python modules.

## Data architecture

The project currently combines Google Cloud storage and analytical services with locally executed notebooks.

```text
Google Cloud Storage
        │
        │ raw source data
        ▼
ETL notebooks + reusable transformations
        │
        ▼
Curated datasets
        │
        ▼
BigQuery
        │
        ▼
Exploratory analysis
        │
        ▼
Crop-season reconstruction
        │
        ▼
Phase-based feature engineering
        │
        ▼
Integrated analytical dataset
        │
        ▼
Feature screening
        │
        ▼
Future modeling and evaluation
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

The raw climate files contain daily gridded observations, with multiple grid cells for each source province.

The climate pipeline processes variables including:

* temperature;
* precipitation;
* wind speed;
* vapour pressure;
* reference evapotranspiration;
* solar radiation;
* altitude.

Daily cell-level observations are transformed into monthly provincial indicators describing:

* average conditions;
* local extremes;
* spatial variability;
* territorial shares affected by events;
* event frequency;
* consecutive-event duration;
* precipitation, evapotranspiration, and radiation totals;
* static altitude characteristics.

The curated climate dataset covers monthly observations from 1980 to 2025.

### Agricultural production data

The production workflow processes historical information on:

* cultivated area;
* total production;
* agricultural yield;
* crop;
* year;
* source territory;
* territorial coverage;
* reconstruction and quality status.

The resulting dataset is a long-format province–year–crop panel.

Dedicated `q_*` fields retain information about missing source components, structural zeroes, reconstructed territories, territorial coverage, and other quality conditions.

## Implemented workflows

### Climate ETL

The climate workflow:

* reads the provincial source files from Google Cloud Storage;
* validates schema, dates, numeric values, missing values, duplicate keys, and grid consistency;
* handles source territories that must be combined to match production areas;
* corrects inconsistent temperature ordering where possible;
* calculates historical monthly reference thresholds;
* identifies fixed-threshold and percentile-based climate events;
* derives daily provincial indicators;
* aggregates the results to province and month;
* exports a consolidated curated climate dataset.

### Production ETL

The production workflow:

* reads the agricultural-production source from Google Cloud Storage;
* inspects source structure and relevant variables;
* distinguishes absent observations from structural zeroes;
* harmonizes changing or incompatible territorial definitions;
* reconstructs selected production areas where necessary;
* calculates yield from aggregated production and area;
* creates provenance and quality indicators;
* validates the final province–year–crop key;
* exports a curated production panel.

### Exploratory analysis and data preparation

The EDA notebook currently covers:

* structural and consistency checks;
* temporal and territorial coverage;
* absent and incomplete production observations;
* quality indicators;
* univariate analysis of production and climate variables;
* agricultural-yield distributions;
* temporal yield patterns across territories;
* robust long-term trend estimation using Theil–Sen slopes;
* partial autocorrelation analysis across independent province–crop series;
* relationships between cultivated area and yield;
* construction of agricultural crop calendars;
* alignment of climate observations with harvest years;
* aggregation of monthly climate variables over crop-development phases;
* integration of climate, production, territorial, and lagged information;
* crop-specific ranking of climate–yield associations;
* screening of candidate features;
* temporal and territorial inspection of selected variables;
* comparison of environmental conditions across crop phases.

The notebook remains exploratory: feature screening is intended to guide the modeling stage rather than to define a final causal interpretation of climate–yield relationships.

## Current analytical boundary

The repository can now address questions such as:

* Are the curated datasets structurally coherent?
* Which province–crop–year observations are available?
* Which quality conditions affect the production data?
* How does yield vary between crops, years, and territories?
* Which province–crop series show long-term trends?
* Do previous yield values contain potentially useful information?
* How should monthly climate observations be aligned with crop seasons?
* How do environmental conditions vary across crop-development phases?
* Which engineered climate variables show the strongest exploratory relationships with yield?
* Do these relationships differ between crops or territories?

The following questions remain open:

* Which candidate features should enter the final training dataset?
* How much information is redundant across climate indicators?
* Which historical production variables can be retained without leakage?
* What validation design best represents the intended prediction problem?
* Which baseline and machine-learning models perform best?
* How stable are results over time and across territories?
* Which model relationships remain robust after accounting for trend and geography?
* How should predictive uncertainty be represented?

## Next development stages

### 1. Finalize feature selection and modeling data

The next preparation step is to consolidate the exploratory feature screening into a stable modeling dataset.

This includes:

* confirming crop-specific candidate variables;
* controlling redundancy between related climate indicators;
* defining admissible production observations;
* confirming lagged variables;
* removing information that would introduce leakage;
* documenting the final feature set.

### 2. Define validation and baselines

Before comparing complex models, the project will establish:

* temporal training and validation splits;
* appropriate baseline predictions;
* suitable regression metrics;
* rules for comparing pooled and crop-specific models;
* possible checks of territorial generalization.

### 3. Train predictive models

Candidate tabular models will be evaluated after the modeling dataset is frozen.

The initial objective is supervised yield estimation rather than causal inference.

### 4. Evaluate and interpret

Model evaluation will consider:

* predictive accuracy;
* error distributions;
* performance stability over time;
* performance across crops and territories;
* feature importance;
* SHAP-based interpretation where appropriate;
* agronomic plausibility of the relationships identified.

### 5. Communicate results

The final stages will consolidate:

* methodology;
* model comparisons;
* limitations;
* interpretability findings;
* visualizations;
* possible decision-support implications.

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

A formal dependency or environment file has not yet been added.

### Authentication

Authenticate locally using Google Cloud Application Default Credentials:

```bash
gcloud auth application-default login
```

The authenticated account must have permission to access the required Google Cloud Storage objects and BigQuery tables.

### Suggested reading order

```text
1. notebooks/ETL_Climate_Example.ipynb
2. src/province_transformation.py
3. notebooks/ETL_Climate_Data.ipynb
4. notebooks/ETL_Production_Data.ipynb
5. src/eda_utils.py
6. notebooks/EDA_AgriClimate_Intelligence.ipynb
```

The two ETL workflows are logically independent. Their curated outputs are combined during the analytical and data-preparation stages of the EDA.

## Reproducibility and known limitations

The repository remains under active development.

Current limitations include:

* no formal dependency or environment file;
* no automated test suite;
* no continuous-integration workflow;
* some configuration remains inside notebooks;
* the project is not packaged as an installable Python package;
* raw datasets are not distributed through the repository;
* Google Cloud access is required for the default execution path;
* the final modeling dataset has not yet been frozen;
* no predictive model or validated performance result is yet available;
* exploratory associations should not be interpreted automatically as causal relationships.

## Collaboration

The `main` branch is protected. Contributors should work on a dedicated branch and open a pull request for review.

Example:

```bash
git checkout -b feature/descriptive-name
git add .
git commit -m "Describe the change"
git push -u origin feature/descriptive-name
```

Methodological changes should clearly state:

* what definition or transformation changed;
* why it changed;
* which outputs are affected;
* whether downstream datasets or notebooks must be regenerated.

## Academic context

This repository supports the Capstone Project:

**Data Driven Analysis for Climate Smart Agriculture: Strategy, Operational Resilience, and Agricultural Yield Analysis in a Changing Climate**

The project is associated with the Executive Master in Data Science at Rome Business School.

## License

No open-source license is currently included. Public visibility alone does not grant explicit reuse, redistribution, or modification rights.
