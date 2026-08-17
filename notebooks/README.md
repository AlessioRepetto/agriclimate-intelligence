# Notebooks

This directory contains the executable workflows used to inspect, transform, validate, integrate, and analyse the project data.

> [!NOTE]
> The notebook collection is still evolving.
>
> The two ETL workflows are implemented. The EDA notebook now extends beyond descriptive analysis into crop-season reconstruction, feature engineering, dataset integration, and climate–yield feature screening. Predictive modeling has not yet been implemented.

## Current contents

| Notebook                             | Current role                                                                            | Main input                                                       | Current output                                                                                             | Status      |
| ------------------------------------ | --------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ----------- |
| `ETL_Climate_Example.ipynb`          | Demonstrates the climate transformation on one source province                          | One compressed provincial climate file from Google Cloud Storage | Validation outputs and one monthly provincial example                                                      | Implemented |
| `ETL_Climate_Data.ipynb`             | Runs the climate transformation across all mapped production areas                      | Provincial climate source files                                  | Consolidated monthly climate dataset                                                                       | Implemented |
| `ETL_Production_Data.ipynb`          | Harmonizes and validates agricultural-production data                                   | Production source from Google Cloud Storage                      | Province–year–crop production panel                                                                        | Implemented |
| `EDA_AgriClimate_Intelligence.ipynb` | Performs exploratory analysis and constructs the analytical dataset for future modeling | Curated climate and production tables                            | Diagnostics, engineered crop-phase features, integrated observations, feature rankings, and visualizations | In progress |

## Relationship between the notebooks

```text
ETL_Climate_Example.ipynb
        │
        │ validates and illustrates
        ▼
src/province_transformation.py
        │
        ▼
ETL_Climate_Data.ipynb ─────────────┐
                                    │
                                    ├──► curated BigQuery tables
                                    │             │
ETL_Production_Data.ipynb ──────────┘             ▼
                                  EDA_AgriClimate_Intelligence.ipynb
                                                   │
                                                   ├──► data understanding
                                                   ├──► crop-season reconstruction
                                                   ├──► phase-based feature engineering
                                                   ├──► climate–production integration
                                                   └──► feature screening
                                                               │
                                                               ▼
                                                       future modeling
```

The two ETL notebooks produce the climate and production datasets independently. Their outputs are subsequently combined inside the EDA workflow after the crop-season climate features have been constructed.

## Recommended reading order

```text
1. ETL_Climate_Example.ipynb
2. ETL_Climate_Data.ipynb
3. ETL_Production_Data.ipynb
4. EDA_AgriClimate_Intelligence.ipynb
```

For code-level understanding:

* read `src/province_transformation.py` together with the climate ETL;
* read `src/eda_utils.py` before the EDA notebook.

## `ETL_Climate_Example.ipynb`

### Purpose

This notebook applies the climate workflow to a single provincial source file so that the transformation can be inspected before executing it across all source areas.

### Current operations

* configure project and cloud paths;
* read one compressed CSV directly from Google Cloud Storage;
* inspect the raw schema and sample observations;
* validate dates, numerical fields, nulls, duplicates, and grid consistency;
* derive daily province-level indicators;
* aggregate them to month;
* inspect intermediate and final outputs.

### Appropriate use

Use this notebook to:

* understand the climate pipeline;
* test source-data changes;
* investigate a problematic province;
* validate changes to feature definitions;
* check a transformation before running the full batch.

Reusable transformation changes should normally be implemented in `src/province_transformation.py`.

## `ETL_Climate_Data.ipynb`

### Purpose

This notebook orchestrates the complete climate ETL.

### Current operations

* define the mapping between target production areas and climate source files;
* read gzip-compressed files directly from Google Cloud Storage;
* combine source territories where required;
* remove duplicate cell–day observations introduced by overlaps;
* call the reusable climate transformation for each target area;
* add province and region labels;
* concatenate monthly outputs;
* validate the consolidated dataset;
* export the curated climate table.

### Territorial mapping

The notebook retains the mapping between:

```text
territorial code
source filename or filenames
final production-area label
region
```

This is required because the climate and production sources do not always use directly compatible territorial definitions.

### Current status

The complete workflow has been implemented for the mapped areas.

Its output should nevertheless remain versioned and reproducible, because changes to thresholds, event definitions, source mappings, or aggregation rules can affect downstream analytical results.

## `ETL_Production_Data.ipynb`

### Purpose

This notebook converts the agricultural-production source into a harmonized panel suitable for integration with the climate data.

### Current operations

* read the source from Google Cloud Storage;
* inspect variables and source structure;
* retain the required crop, year, territorial, area, production, and yield fields;
* analyse absent observations and structural zeroes;
* harmonize territorial definitions;
* aggregate source territories where required;
* calculate yield from total production and cultivated area;
* preserve provenance and quality information;
* reshape the data to long format;
* validate the final key;
* export the curated production table.

### Observation unit

```text
province × year × crop
```

### Main analytical fields

```text
province
year
crop_name
area
production
yield
```

### Quality information

The `q_*` fields retain information concerning, among other aspects:

* territorial coverage;
* source regions used;
* missing source regions;
* structural zeroes;
* source or calculation status;
* area–production–yield coherence;
* reconstructed territorial units.

These fields remain relevant when deciding which observations can enter the final modeling dataset.

## `EDA_AgriClimate_Intelligence.ipynb`

### Purpose

This notebook performs the main exploratory analysis and progressively transforms the curated climate and production datasets into observations suitable for predictive modeling.

It currently combines **Data Understanding** and **Data Preparation** responsibilities.

### Current data access

The default execution path reads the curated BigQuery tables:

```text
agriclimate-intelligence.curated.climate_full_dataset_v1
agriclimate-intelligence.curated.production_full_dataset_v1
```

Optional local CSV files can be used when available.

### 1. Data structure and quality

The first part of the notebook covers:

* initial inspection of both curated datasets;
* structural and type checks;
* internal-consistency checks;
* temporal and territorial coverage;
* absent province–crop–year combinations;
* production-data quality indicators;
* univariate analysis of production and climate variables.

The objective is to understand what information is available and which limitations must be retained during subsequent modeling.

### 2. Agricultural yield analysis

The notebook examines:

* yield distributions by crop;
* temporal yield patterns;
* differences between territories and broader geographical areas;
* long-term province–crop trends;
* partial autocorrelation within independent yield series.

Long-term trends are estimated using **Theil–Sen slopes**, which reduce sensitivity to isolated anomalous years.

The **PACF** analysis evaluates whether previous yield values may contain additional predictive information without concatenating independent provincial series.

### 3. Crop-season reconstruction

Monthly climate observations are aligned with the agricultural year associated with each yield target.

The notebook:

* defines crop-specific agricultural calendars;
* expands the calendars over the available production years;
* checks that the required climate months are available;
* associates each climate month with a crop-development phase.

This moves the analysis from generic calendar-year climate statistics toward agriculturally meaningful time windows.

### 4. Climate feature engineering

Monthly climate indicators are aggregated over the crop-development phases.

Depending on the underlying variable, the resulting features retain information such as:

* average environmental conditions;
* accumulated quantities;
* extreme-event frequency;
* consecutive-event duration;
* spatial variability;
* territorial event coverage.

Stable territorial information such as altitude is also retained where relevant.

### 5. Climate and production integration

The engineered climate features are combined with annual production observations at the analytical level:

```text
province × crop × harvest year
```

The integrated dataframe includes the yield target together with climate, territorial, temporal, and selected historical production information.

Lagged production variables are constructed before the final modeling stage so that their potential predictive contribution can be evaluated while preserving the temporal structure of the problem.

### 6. Bivariate analysis with yield

The notebook performs crop-specific exploratory screening of the engineered variables.

This currently includes:

* correlation-based ranking of candidate features;
* visual inspection of the strongest relationships;
* comparison across crops;
* temporal trends of selected variables;
* comparisons across geographical macro-areas;
* distributions across territories;
* identification of provisional crop-specific feature sets.

The rankings are used as exploratory guidance rather than as an automatic feature-selection rule.

A high correlation does not by itself demonstrate that a variable should enter the final model, while weaker marginal relationships may still contain useful information in a multivariate setting.

### 7. Environmental patterns across crop phases

For selected environmental variables, the notebook compares the different crop-development phases through:

* distribution plots across province–year observations;
* yearly median trends;
* crop-specific comparisons.

This helps identify whether environmental conditions and their variability differ systematically across agronomic phases before the modeling stage.

### Current boundary

The EDA now provides the analytical foundation required for modeling, but the feature set is not yet final.

The remaining preparation work mainly concerns:

* consolidating crop-specific candidate features;
* controlling redundancy among correlated climate indicators;
* confirming admissible production observations;
* deciding which lagged variables to retain;
* checking potential data leakage;
* freezing the final modeling dataset.

The notebook does **not** yet contain:

* formal train/validation/test splitting;
* predictive baselines;
* machine-learning training;
* hyperparameter tuning;
* final model comparison;
* SHAP or other model-level interpretation;
* final predictive-performance results.

## Cloud authentication

The notebooks use Google Cloud Application Default Credentials.

```bash
gcloud auth application-default login
```

The authenticated account must have permission to read the required Google Cloud Storage objects and BigQuery tables.

Never place credentials or service-account keys inside notebook cells.

## Local project layout

When local alternatives are used, the expected structure is:

```text
agriclimate-intelligence/
├── data/
├── notebooks/
└── src/
```

The `data/` directory is not versioned in the public repository.

## Notebook conventions

When editing notebooks:

* maintain a clear top-to-bottom execution order;
* separate data access from analytical transformations;
* keep reusable logic in `src/` where appropriate;
* explain methodological choices in markdown;
* distinguish observed findings from decisions that are still provisional;
* do not describe planned work as already implemented;
* avoid user-specific local paths;
* never commit credentials;
* avoid unnecessary large outputs;
* update this README when the analytical workflow changes materially.
