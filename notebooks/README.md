# Notebooks

This directory contains the executable workflows used to inspect, transform, validate, and analyse the project data.

> [!NOTE]
> The notebook collection is still evolving.
>
> The ETL workflows are implemented, while the exploratory notebook is advanced but incomplete. No modeling notebook is currently present in the repository.

## Current contents

| Notebook | Current role | Main input | Current output | Status |
|---|---|---|---|---|
| `ETL_Climate_Example.ipynb` | Demonstrates the climate transformation on one source province | One compressed provincial climate file from Google Cloud Storage | Intermediate validation outputs and one monthly provincial example | Implemented |
| `ETL_Climate_Data.ipynb` | Runs the climate transformation across all mapped production areas | 107 compressed provincial climate files | Consolidated monthly climate dataset | Implemented |
| `ETL_Production_Data.ipynb` | Harmonizes and validates agricultural-production data | Production source from Google Cloud Storage | Province–year–crop production panel | Implemented |
| `EDA_AgriClimate_Intelligence.ipynb` | Explores the two curated datasets and prepares the next data-preparation stage | BigQuery curated tables, or optional local CSV exports | Diagnostics, tables, visualizations, trend estimates, PACF summaries, and methodological observations | In progress |

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
                                                   ▼
                             future crop-season preparation and modeling
```

The ETL notebooks currently produce the two curated datasets separately. The EDA reads both, but a final climate–production modeling table has not yet been constructed.

## Recommended reading order

```text
1. ETL_Climate_Example.ipynb
2. ETL_Climate_Data.ipynb
3. ETL_Production_Data.ipynb
4. EDA_AgriClimate_Intelligence.ipynb
```

For code-level understanding, read `src/province_transformation.py` after the climate example and `src/eda_utils.py` before the EDA notebook.

## `ETL_Climate_Example.ipynb`

### Purpose

This notebook applies the climate workflow to a single provincial file so that the transformation can be inspected before running it across all source areas.

### Current operations

- configure project and cloud paths;
- read one compressed CSV directly from Google Cloud Storage;
- inspect the raw schema and sample observations;
- validate dates, numerical fields, nulls, duplicates, and grid consistency;
- derive daily province-level indicators;
- aggregate them to month;
- inspect intermediate and final outputs.

### Appropriate use

Use this notebook to:

- understand the climate pipeline;
- test source-data changes;
- investigate a problematic province;
- validate changes to feature definitions;
- check a transformation before running the national batch.

Reusable changes should be implemented in `src/province_transformation.py`, not only in notebook cells.

## `ETL_Climate_Data.ipynb`

### Purpose

This notebook orchestrates the complete climate ETL.

### Current operations

- define the mapping between target production areas and climate source files;
- read gzip-compressed files directly from Cloud Storage;
- concatenate multiple source territories where required;
- remove duplicate cell–day observations introduced by overlap;
- call `transform_province_dataframe()` for each target area;
- add province and region labels;
- concatenate all monthly results;
- validate and export the consolidated dataset.

### Territorial mapping

The notebook contains a mapping with:

```text
territorial code
source filename or filenames
final production-area label
region
```

This is necessary because climate and production sources do not always use the same historical administrative boundaries.

The mapping is currently embedded in the notebook and may later be moved to a dedicated configuration file.

### Current status

The notebook has been executed across all mapped areas. It should nevertheless be considered part of an evolving pipeline because transformation definitions, paths, and versioning may still change.

## `ETL_Production_Data.ipynb`

### Purpose

This notebook converts the agricultural source into a harmonized panel suitable for integration with the climate data.

### Current operations

- read the source from Google Cloud Storage;
- inspect variables and source structure;
- retain the required crop, year, territorial, area, production, and yield fields;
- analyse absent observations and structural zeroes;
- harmonize territorial definitions;
- aggregate source regions where required;
- calculate yield from total production and total area;
- preserve source and quality information;
- reshape the data to long format;
- validate the final key;
- export the curated production table.

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

### Quality fields

The `q_*` fields describe aspects such as:

- territorial coverage;
- number of source regions used;
- missing source regions;
- structural zeroes;
- source or calculation status;
- area–production–yield coherence;
- calculated territorial units.

These fields should remain available when the modeling dataset is created.

## `EDA_AgriClimate_Intelligence.ipynb`

### Purpose

This notebook explores the curated climate and production datasets and identifies the transformations required before modeling.

### Current data access

The default execution path reads:

```text
agriclimate-intelligence.curated.climate_full_dataset_v1
agriclimate-intelligence.curated.production_full_dataset_v1
```

from BigQuery.

Optional local files can be used instead:

```text
data/climate_full_dataset.csv
data/production_full_dataset.csv
```

### Current analytical coverage

The notebook currently includes:

- initial inspection of both curated tables;
- structural and type checks;
- internal-consistency checks;
- temporal and territorial coverage;
- analysis of absent production observations;
- review of quality flags;
- univariate analysis of production variables;
- selected exploration of climate features;
- yield distributions;
- temporal behavior of yield;
- robust trend estimation within province–crop series;
- summaries of partial autocorrelation across the available series.

The Theil–Sen analysis is used to estimate long-term slopes with reduced sensitivity to isolated extreme years.

The PACF section studies whether previous values of yield may contribute information beyond the trend, without concatenating independent provincial series.

### What the notebook does not yet contain

The notebook explicitly leaves the following for subsequent development:

- crop-season reconstruction;
- aggregation of monthly climate indicators over the agronomic season;
- feature construction by growth phase;
- bivariate analysis between engineered climate features and yield;
- feature selection;
- construction of the final modeling table;
- baseline models;
- machine-learning training and evaluation.

### Current interpretation

The notebook should be read as a working analytical document. Its outputs support decisions about the next preparation steps, but they are not yet the final results of the project.

## Cloud authentication

The notebooks use Google Cloud Application Default Credentials.

```bash
gcloud auth application-default login
```

The authenticated account must have permission to read the relevant Cloud Storage objects and BigQuery tables.

Never place credentials or service-account keys in notebook cells.

## Local project layout

When local CSV alternatives are used, the expected structure is:

```text
agriclimate-intelligence/
├── data/
├── notebooks/
└── src/
```

The `data/` directory is not versioned in the public repository.

## Notebook conventions

When editing notebooks:

- maintain a clear top-to-bottom execution order;
- separate data access from analytical transformations;
- move reusable logic to `src/`;
- explain methodological choices in markdown;
- distinguish observations from decisions not yet taken;
- do not describe planned work as already implemented;
- avoid local user-specific paths;
- never commit credentials;
- avoid committing unnecessary large outputs;
- update this README when the role or status of a notebook changes.

## Expected future workflows

The following logical stages are not yet represented by dedicated notebooks:

```text
crop-season feature construction
integrated modeling-dataset preparation
baseline modeling
model training and validation
interpretability and error analysis
final results and communication
```

The exact file names and division of responsibilities remain open and should follow the practical evolution of the project.
