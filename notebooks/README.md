# Notebooks

This directory contains the executable workflows used to inspect, transform, validate, analyse, engineer, and model the project data.

> **Status**
>
> The notebook collection is still evolving. The two ETL pipelines are implemented, the EDA has reached the modelling hand-off stage, and `ML_Quantile_Modelling.ipynb` is now the main work-in-progress notebook.
>
> The modelling workflow has **not yet evaluated the 2019–2022 final test period**.

## Current contents

| Notebook | Current role | Main input | Main output | Status |
| --- | --- | --- | --- | --- |
| `ETL_Climate_Example.ipynb` | Demonstrates and validates the climate transformation on one source province | One compressed provincial climate file from Google Cloud Storage | Intermediate diagnostics and one monthly provincial example | Implemented |
| `ETL_Climate_Data.ipynb` | Runs the climate transformation across all mapped production areas | 107 compressed provincial climate files | Consolidated monthly climate dataset | Implemented |
| `ETL_Production_Data.ipynb` | Harmonizes and validates agricultural-production data | Production source from Google Cloud Storage | Province–year–crop production dataset | Implemented |
| `EDA_AgriClimate_Intelligence.ipynb` | Integrates the curated data, performs the main EDA, reconstructs crop-season information, and prepares the modelling representation | BigQuery curated tables or optional local CSV exports | Diagnostics, visualizations, engineered predictors, analytical findings, modelling dataset | Advanced |
| `ML_Quantile_Modelling.ipynb` | Develops and compares crop-specific quantile models under chronological validation | `data/modelling_data.csv` | Model comparisons, outer-validation results, temporal robustness diagnostics | **WIP** |

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
                                    ├──► curated climate + production data
                                    │                  │
ETL_Production_Data.ipynb ──────────┘                  ▼
                                      EDA_AgriClimate_Intelligence.ipynb
                                                        │
                                                        │ crop-season features
                                                        │ + modelling table
                                                        ▼
                                           ML_Quantile_Modelling.ipynb
                                                        │
                                                        ▼
                                         final model selection still open
```

## Recommended reading order

```text
1. ETL_Climate_Example.ipynb
2. ETL_Climate_Data.ipynb
3. ETL_Production_Data.ipynb
4. EDA_AgriClimate_Intelligence.ipynb
5. ML_Quantile_Modelling.ipynb
```

For code-level understanding:

- read `src/province_transformation.py` after the climate example;
- read `src/eda_utils.py` before the EDA;
- read `src/modelling_utils.py` before the modelling notebook.

---

## `ETL_Climate_Example.ipynb`

### Purpose

This notebook applies the climate workflow to a single provincial file so that the complete transformation can be inspected before running it across all source areas.

### Current operations

The notebook:

- configures project and cloud paths;
- reads one compressed CSV from Google Cloud Storage;
- inspects the raw schema and sample observations;
- validates dates, numerical fields, nulls, duplicate keys, and grid consistency;
- checks and corrects inconsistent temperature ordering where possible;
- derives daily province-level indicators;
- aggregates them to month;
- inspects intermediate and final outputs.

### Appropriate use

Use this notebook to:

- understand the climate pipeline;
- test source-data changes;
- investigate a problematic province;
- validate changes to feature definitions;
- check a transformation before running the national batch.

Reusable transformation logic should be implemented in `src/province_transformation.py`, not only in notebook cells.

---

## `ETL_Climate_Data.ipynb`

### Purpose

This notebook orchestrates the complete climate ETL across the mapped Italian production areas.

### Current operations

The workflow:

- defines the mapping between target production areas and climate source files;
- reads gzip-compressed files from Cloud Storage;
- concatenates multiple source territories where required;
- removes duplicate cell–day observations introduced by overlap;
- applies the reusable provincial transformation;
- adds province and region labels;
- concatenates all monthly outputs;
- validates and exports the consolidated dataset.

### Territorial mapping

The workflow maintains a mapping between:

```text
territorial code
source filename or filenames
final production-area label
region
```

This is necessary because the climate and production sources do not always use identical historical administrative boundaries.

### Status

The notebook has been executed across all mapped areas and represents the current complete climate batch workflow.

---

## `ETL_Production_Data.ipynb`

### Purpose

This notebook converts the agricultural source into a harmonized structure that can be integrated with climate information.

### Current operations

The workflow:

- reads the production source from Google Cloud Storage;
- inspects variables and source structure;
- retains the required crop, year, territory, area, production, and yield information;
- distinguishes missing observations from structural zeroes;
- harmonizes territorial definitions;
- reconstructs or aggregates selected areas when required;
- recalculates yield from total production and cultivated area where appropriate;
- preserves provenance and quality information;
- reshapes the data to long format;
- validates the final observation key;
- exports the curated production dataset.

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

Dedicated `q_*` fields retain information about:

- territorial coverage;
- source completeness;
- structural zeroes;
- calculation or reconstruction status;
- area–production–yield coherence;
- reconstructed territorial units.

These fields are kept so that data-quality assumptions remain visible during later analysis.

---

## `EDA_AgriClimate_Intelligence.ipynb`

### Purpose

This notebook is the main Data Understanding and feature-engineering workflow.

It connects the curated climate and production datasets, examines their analytical limitations, reconstructs climate information around the agricultural cycle, and prepares the representation used by the modelling notebook.

### Data access

The default cloud path uses:

```text
agriclimate-intelligence.curated.climate_full_dataset_v1
agriclimate-intelligence.curated.production_full_dataset_v1
```

Optional local CSV copies can also be used when available.

### Current analytical coverage

The notebook currently includes:

- initial structure and type checks;
- internal-consistency checks;
- temporal and territorial coverage;
- missing and absent production observations;
- review of quality flags;
- univariate exploration of production and climate variables;
- yield distributions;
- temporal yield patterns;
- macro-regional comparisons;
- robust long-term trend estimation;
- partial-autocorrelation summaries;
- altitude analysis;
- crop-calendar and crop-phase reconstruction;
- phase-level environmental summaries;
- bivariate analysis between yield and engineered predictors;
- crop-specific correlation rankings;
- selected follow-up visualizations;
- preparation of the modelling dataset.

### Role in the project

The EDA is not only descriptive. It also provides the methodological bridge between the curated monthly data and the annual supervised-learning problem.

The transformations and observations developed here determine:

- which crops proceed to modelling;
- how the agricultural season is represented;
- which climate periods are aggregated;
- which predictors are plausible candidates;
- how historical yield information should be treated;
- which data-quality issues must remain visible.

The notebook should therefore be read before the modelling workflow.

### Output boundary

Generated analytical datasets are not committed to the public repository.

The modelling notebook expects the current local modelling export at:

```text
data/modelling_data.csv
```

---

## `ML_Quantile_Modelling.ipynb`

### Purpose

This notebook is the current model-development and model-selection workflow for annual crop yield.

Three crops are modelled separately:

```text
Durum wheat
Soft wheat
Grain maize
```

The notebook is explicitly **work in progress** and currently ends before final test evaluation.

### Modelling objective

The workflow uses quantile regression to estimate three conditional yield quantiles:

```text
Q1 = 0.25
Q2 = 0.50
Q3 = 0.75
```

Q2, the conditional median, is the primary model-selection objective.

Performance is evaluated with pinball loss.

### Current modelling data

After rows without an observed target are removed, the modelling workflow uses:

```text
7,576 observations
4 historical predictors
192 crop-phase climate predictors
196 SFS candidate predictors
```

Current-year `area`, `production`, and `yield` are not used as predictors.

### Temporal validation design

The chronological split is fixed before model comparison.

#### Development folds

```text
train through 2006 → validate on 2007–2009
train through 2009 → validate on 2010–2012
train through 2012 → validate on 2013–2015
```

#### Outer validation

```text
2016–2018
```

This block is used for the later model-selection comparison.

#### Final test

```text
2019–2022
```

The final test remains untouched and is not used for:

- training;
- feature selection;
- early stopping;
- tuning;
- model-family selection;
- current model-choice decisions.

### Current experiment sequence

The notebook currently contains:

1. **Historical linear quantile baseline**
   - four historical yield predictors;
   - common scaling and quantile-regression pipeline.

2. **Sequential Forward Selection**
   - performed separately by crop;
   - Q2 temporal-CV objective;
   - historical and phase-level climate predictors compete in the same candidate pool;
   - the expensive original search is not rerun;
   - selected feature sets are stored explicitly for reproducibility.

3. **Temporal stability analysis**
   - compares historical and SFS linear specifications fold by fold.

4. **L1-regularized linear quantile regression**
   - tests whether additional coefficient shrinkage improves the selected linear models.

5. **CatBoost**
   - conventional nonlinear tabular comparison;
   - Q2-focused;
   - early stopping is determined using recent years inside the training window and the model is then refitted on the full training period.

6. **Outer validation**
   - compares the strongest developed specifications on 2016–2018.

7. **Tabular foundation models / TabPFN**
   - introduces the modelling paradigm theoretically;
   - compares TabPFN variants with historical, selected, and broader feature representations;
   - preserves native missing values where the model supports them.

8. **Temporal robustness checks**
   - backtests the strongest TabPFN alternatives against the strongest conventional references on earlier chronological folds.

### Current model-selection boundary

The notebook currently ends with:

```text
Model selection - TO BE CONTINUED
```

The main unresolved issue is not whether further models can be fitted, but which selection rule should be frozen before accessing the final benchmark.

Current evidence suggests:

- **Durum wheat:** strongest evidence is concentrated around the parsimonious historical linear model.
- **Grain maize:** TabPFN is competitive with or stronger than the best linear alternative, but the choice depends on whether average temporal robustness or the strongest recent validation result is prioritized.
- **Soft wheat:** the ranking remains mixed; the historical linear model is stronger on average across the available temporal windows, while TabPFN Full is stronger in part of the later validation evidence.

These are validation-stage findings only.

The **2019–2022 final test must remain untouched until this decision is fixed**.

### TabPFN access

The notebook uses `tabpfn_client`.

Authentication information should be read from a local `.env` file or equivalent environment configuration.

Never commit API tokens or credentials to the repository.

---

## Cloud authentication

The cloud-based notebooks use Google Cloud Application Default Credentials.

```bash
gcloud auth application-default login
```

The authenticated account must have access to the required Cloud Storage objects and BigQuery tables.

Never place service-account keys or credentials directly in notebook cells.

## Local project layout

When locally generated datasets are used, the expected structure is:

```text
agriclimate-intelligence/
├── data/
│   └── modelling_data.csv
├── notebooks/
└── src/
```

The `data/` directory is intentionally not part of the public versioned workflow.

## Notebook conventions

When editing notebooks:

- maintain a clear top-to-bottom execution order;
- keep chronological validation explicit;
- separate data access from reusable analytical logic;
- move reusable functions to `src/`;
- explain methodological choices in markdown;
- distinguish observed evidence from decisions not yet taken;
- do not describe planned work as already completed;
- avoid user-specific absolute paths;
- never commit credentials or API tokens;
- avoid committing unnecessary large outputs;
- keep the final test isolated until model selection is frozen;
- update this README when the role or status of a notebook changes.
