# Notebooks

This directory contains the executable workflows used to inspect, transform, validate, and analyse the project data.

The notebooks currently cover the **Data Understanding** and **Data Preparation** phases of CRISP-DM. The project-level exploratory notebook begins the transition toward modeling, but the final integrated dataset and predictive models are not yet included.

## Contents

| Notebook | Purpose | Main input | Main output | Status |
|---|---|---|---|---|
| `ETL_Climate_Example.ipynb` | Demonstrates and inspects the climate transformation on one province | One compressed provincial climate file from Google Cloud Storage | One monthly provincial example dataset and intermediate validation outputs | Implemented |
| `ETL_Climate_Data.ipynb` | Runs the climate ETL across all mapped Italian provincial files | 107 compressed climate files from Google Cloud Storage | `data/climate_full_dataset.csv` | Implemented; under consolidation |
| `ETL_Production_Data.ipynb` | Cleans, harmonizes, validates, and reshapes agricultural-production data | Production source from Google Cloud Storage | `data/production_data.csv` | Implemented; under consolidation |
| `EDA_AgriClimate_Intelligence.ipynb` | Performs exploratory analysis on the prepared project datasets | Prepared climate and production datasets | Tables, figures, diagnostics, and analytical observations | In progress |

## Recommended reading and execution order

```text
1. ETL_Climate_Example.ipynb
2. ETL_Climate_Data.ipynb
3. ETL_Production_Data.ipynb
4. EDA_AgriClimate_Intelligence.ipynb
```

The first notebook explains the climate transformation incrementally and is the best entry point for reviewing or changing its logic.

The two full ETL notebooks are independent at the current stage. Their outputs will later be joined to create the modeling dataset.

## `ETL_Climate_Example.ipynb`

### Purpose

This notebook applies the climate transformation workflow to a single provincial file so that every major step can be inspected before batch execution.

### Main operations

- configure project, data, and cloud paths;
- authenticate through Google Cloud Application Default Credentials;
- read one compressed CSV directly from Cloud Storage;
- inspect the source schema and sample values;
- validate dates, numeric columns, missing values, duplicates, and cell consistency;
- calculate daily and monthly climate indicators;
- inspect intermediate dataframes;
- export a test result.

### When to use it

Use this notebook when:

- learning how the climate pipeline works;
- testing a new source-file version;
- debugging a transformation problem;
- adding or changing a climate feature;
- validating a province before modifying the full batch process.

Changes that are intended for the production workflow should normally be implemented in `src/province_transformation.py`, not only inside the notebook.

## `ETL_Climate_Data.ipynb`

### Purpose

This notebook orchestrates the complete national climate transformation.

### Main operations

- define the mapping between climate source files and final production territories;
- read compressed source files from Cloud Storage;
- concatenate multiple files where one final territory requires several source territories;
- remove duplicate cell–day observations introduced by overlapping source files;
- call `transform_province_dataframe()` for each final territory;
- append territorial identifiers;
- concatenate all monthly provincial datasets;
- validate the consolidated result;
- save the generated dataset locally.

### Current output

```text
data/climate_full_dataset.csv
```

### Important configuration

The notebook currently contains a territorial mapping that links:

```text
territorial code
source climate filename or filenames
final province name
region
```

This mapping is part of the project methodology because climate-source boundaries do not always match the territorial definitions used by the production data.

It should eventually be moved to a centralized configuration file.

## `ETL_Production_Data.ipynb`

### Purpose

This notebook transforms the agricultural source into a harmonized province–year–crop panel suitable for later integration with the climate data.

### Main operations

- read the production source directly from Cloud Storage;
- inspect the source structure and variables;
- select the area, production, yield, crop, year, and territorial fields required by the project;
- analyse missing observations and structural zeroes;
- harmonize territories;
- aggregate source regions where required;
- calculate yield from aggregated production and area;
- retain provenance and quality information;
- reshape the data into long format;
- validate the final key and quality columns;
- save the generated dataset locally.

### Current output

```text
data/production_data.csv
```

### Final observation unit

```text
province × year × crop
```

### Core analytical fields

```text
province
year
crop_name
area
production
yield
```

### Quality and provenance fields

The final dataset also includes `q_*` columns describing aspects such as:

- territorial coverage;
- number of source regions used;
- missing component regions;
- structural zeroes;
- source or calculation status;
- area–production–yield coherence;
- reconstructed territories.

These fields should be retained through modeling-dataset construction so that observations can be filtered, stratified, or analysed by quality class.

## `EDA_AgriClimate_Intelligence.ipynb`

### Purpose

This notebook contains project-level exploratory analysis.

### Current role

It supports:

- verification of dataset dimensions and coverage;
- distribution analysis;
- missing-value and zero-value diagnostics;
- temporal analysis;
- territorial comparison;
- review of quality indicators;
- identification of transformations and filters required before modeling.

### Development status

The notebook is still in progress. It should not yet be treated as the final EDA report or as evidence that the climate and production data have already been fully integrated.

Future versions are expected to include:

- cross-dataset alignment checks;
- crop-specific season construction;
- target-distribution analysis;
- leakage checks;
- correlation and redundancy analysis;
- baseline comparisons;
- visual summaries for the final report.

## Cloud access

The notebooks use Google Cloud Application Default Credentials.

Authenticate locally with:

```bash
gcloud auth application-default login
```

The account must have read access to the project bucket.

The current cloud organization follows this general pattern:

```text
raw/
├── climate/
│   └── v1/
└── production/
    └── v1/
```

Do not place credentials, service-account keys, or other secrets in notebook cells.

## Local paths

Notebook code resolves the repository root and writes generated outputs to a local project-level data directory.

Expected structure during execution:

```text
agriclimate-intelligence/
├── data/
├── notebooks/
└── src/
```

The `data/` directory is not part of the current public repository and may need to be created automatically or manually depending on the notebook version.

## Imports from `src`

Reusable logic should be imported from the `src/` directory.

The repository is not yet packaged as an installable Python project, so some notebooks may currently add `src/` to `sys.path` or depend on the execution directory.

This behavior should be standardized in a future revision.

## Notebook conventions

When editing notebooks:

- keep data access separate from transformation logic;
- move reusable transformations into `src/`;
- use markdown cells to explain methodological decisions;
- avoid storing credentials or personal local paths;
- do not commit large generated outputs;
- clear unnecessary temporary cells;
- retain important validation outputs when they document pipeline correctness;
- ensure that cells can be run in a clear top-to-bottom order;
- update this README when adding, renaming, or changing a notebook's role.
