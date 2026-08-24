# Notebooks

This directory contains the executable workflows used to inspect, transform, validate, analyse, engineer, and model the project data.

> **Status**
>
> The ETL pipelines are implemented, the EDA has reached the modelling hand-off stage, and `ML_Quantile_Modelling.ipynb` has now progressed through **model selection and final 2019-2022 out-of-time evaluation**.
>
> The notebook collection is still evolving as the project moves toward final interpretation and communication.

## Current contents

| Notebook | Current role | Main input | Main output | Status |
| --- | --- | --- | --- | --- |
| `ETL_Climate_Example.ipynb` | Demonstrates and validates the climate transformation on one source province | One compressed provincial climate file from Google Cloud Storage | Intermediate diagnostics and one monthly provincial example | Implemented |
| `ETL_Climate_Data.ipynb` | Runs the climate transformation across all mapped production areas | 107 compressed provincial climate files | Consolidated monthly climate dataset | Implemented |
| `ETL_Production_Data.ipynb` | Harmonizes and validates agricultural-production data | Production source from Google Cloud Storage | Province-year-crop production dataset | Implemented |
| `EDA_AgriClimate_Intelligence.ipynb` | Integrates the curated data, performs the main EDA, reconstructs crop-season information, and prepares the modelling representation | BigQuery curated tables or optional local CSV exports | Diagnostics, visualizations, engineered predictors, modelling dataset | Advanced |
| `ML_Quantile_Modelling.ipynb` | Develops, selects, evaluates, and diagnoses crop-specific quantile models under chronological validation | `data/modelling_data.csv` | Final models, 2019-2022 test results, distributional diagnostics, national representations | Advanced / still evolving |

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
                                                        ├── model development
                                                        ├── model selection
                                                        ├── final test
                                                        └── final diagnostics
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
- removes duplicate cell-day observations introduced by overlap;
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
- area-production-yield coherence;
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

The notebook includes:

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

The EDA is not only descriptive. It provides the methodological bridge between the curated monthly data and the annual supervised-learning problem.

The transformations and observations developed here determine:

- which crops proceed to modelling;
- how the agricultural season is represented;
- which climate periods are aggregated;
- which predictors become available to the models;
- how historical yield information is represented;
- which data-quality issues must remain visible.

### Output boundary

Generated analytical datasets are not committed to the public repository.

The modelling notebook expects the current local modelling export at:

```text
data/modelling_data.csv
```

---

## `ML_Quantile_Modelling.ipynb`

### Purpose

This notebook is the main model-development, model-selection, final-evaluation, and probabilistic-diagnostics workflow for annual crop yield.

Three crops are modelled separately:

```text
Durum wheat
Soft wheat
Grain maize
```

### Modelling objective

The workflow estimates three conditional yield quantiles:

```text
Q1 = 0.25
Q2 = 0.50
Q3 = 0.75
```

Q2, the conditional median, is the primary model-selection objective.

Performance is evaluated with **pinball loss**.

### Current modelling data

After rows without an observed target are removed, the workflow uses:

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
train through 2006 → validate on 2007-2009
train through 2009 → validate on 2010-2012
train through 2012 → validate on 2013-2015
```

These expanding folds are used for feature selection, regularization checks, temporal stability analysis, and model screening.

#### Outer validation

```text
2016-2018
```

This is the last period allowed to influence the final model choice.

#### Final test

```text
2019-2022
```

The final test is used only after model selection has been frozen.

It does not contribute to:

- feature selection;
- early stopping;
- hyperparameter decisions;
- model-family comparison;
- crop-specific model selection.

### Current experiment sequence

The notebook now contains:

1. **Naive persistence benchmark**
   - predicts yield from the previous observed year;
   - evaluated on Q2 only;
   - establishes a minimum forecasting-skill hurdle.

2. **Historical linear quantile baseline**
   - four historical predictors;
   - Q1, Q2, and Q3 models;
   - chronological temporal CV.

3. **Sequential Forward Selection**
   - performed separately by crop;
   - Q2 temporal-CV objective;
   - historical and crop-phase climate predictors compete in the same pool;
   - the original expensive search is not rerun;
   - the exact selected feature sets are stored explicitly.

4. **Temporal stability analysis**
   - compares historical and SFS linear specifications fold by fold;
   - checks whether average improvements remain consistent over time.

5. **L1-regularized linear quantile regression**
   - tests whether coefficient shrinkage improves the selected linear specifications.

6. **CatBoost**
   - conventional nonlinear tabular comparison;
   - Q2-focused;
   - early stopping uses only recent years inside the current training window;
   - the selected number of trees is then refitted on the complete training block.

7. **Outer validation**
   - compares the strongest developed specifications on 2016-2018.

8. **Tabular foundation models / TabPFN**
   - introduces the modelling paradigm theoretically;
   - compares historical, SFS, and broader feature representations;
   - preserves native missing values where supported.

9. **Model-selection tie-breakers**
   - applies temporal robustness when outer-validation candidates are sufficiently close;
   - examines quantile behaviour where temporal robustness does not fully separate the finalists.

10. **Final crop-specific selection**
    - freezes one specification for each crop before test access.

11. **Final model refit**
    - combines 1995-2015 development data with the 2016-2018 outer-validation block;
    - refits each already frozen specification using all admissible pre-test observations.

12. **Final 2019-2022 evaluation**
    - evaluates each final model exactly once;
    - reports raw-prediction Q1, Q2, and Q3 pinball losses.

13. **Distributional post-processing**
    - enforces non-negative, ordered quantiles for downstream interpretation;
    - derives conditional IQR and Tukey-style limits.

14. **Final distributional diagnostics**
    - empirical quantile coverage;
    - Q1-Q3 coverage;
    - conditional dispersion;
    - low and high outlier counts.

15. **Validation-to-test comparison**
    - compares final Q2 loss with the preceding outer-validation evidence;
    - reports temporal generalization without reopening model selection.

16. **Geographic outlier analysis**
    - summarizes final-test outliers by region.

17. **Final linear-model interpretation**
    - verifies scaled/unscaled equivalence for unregularized `Linear H`;
    - fits the final durum-wheat equations directly in original feature units;
    - reports coefficients for Q1, Q2, and Q3.

18. **National aggregation**
    - converts province-level yield estimates into implied production;
    - aggregates production and cultivated area;
    - reconstructs area-weighted national yield quantile series;
    - visualizes observed yield, median forecast, IQR, and conditional limits.

### Naive benchmark

The first learned model must outperform a simple persistence rule before more complex modelling is considered useful.

`Linear H` improves mean temporal-CV Q2 pinball loss over the naive benchmark by approximately:

- **10.0% for durum wheat**;
- **11.2% for soft wheat**;
- **7.8% for grain maize**.

The naive model is therefore not retained as a final candidate.

### SFS feature sets

The stored SFS selections contain:

| Crop | Total selected | Historical | Climate |
| --- | ---: | ---: | ---: |
| Durum wheat | 12 | 3 | 9 |
| Soft wheat | 18 | 3 | 15 |
| Grain maize | 25 | 4 | 21 |

The selected sets are specific to the linear Q2 selection procedure. Excluded features are not assumed to be uninformative for nonlinear models.

### Final model selection

The final specifications are:

```text
Durum wheat → Linear H
Grain maize → TabPFN SFS
Soft wheat  → TabPFN Full
```

The 2019-2022 observations were not used to make these choices.

For close outer-validation results, the notebook uses additional pre-test evidence instead of automatically selecting the smallest single validation loss.

For grain maize, the comparison between `TabPFN SFS` and `TabPFN Full` proceeds to temporal robustness.

For soft wheat, the close `TabPFN H` versus `TabPFN Full` comparison proceeds first to temporal robustness and then to quantile behaviour. `TabPFN Full` is ultimately selected because its Q1, Q2, and Q3 pinball losses provide the stronger overall predictive evidence.

### Final training and test

Once the model choices are frozen:

```text
final training = 1995-2018
final test     = 2019-2022
```

Final pre-test training sizes are:

| Crop | Final training rows | Final test rows |
| --- | ---: | ---: |
| Durum wheat | 2,058 | 373 |
| Grain maize | 2,294 | 366 |
| Soft wheat | 2,124 | 361 |

### Final predictive performance

| Crop | Final model | Test Q1 | Test Q2 | Test Q3 |
| --- | --- | ---: | ---: | ---: |
| Durum wheat | `Linear H` | 0.1756 | **0.2106** | 0.1898 |
| Grain maize | `TabPFN SFS` | 0.3348 | **0.3759** | 0.2965 |
| Soft wheat | `TabPFN Full` | 0.1978 | **0.2393** | 0.2026 |

These losses are calculated from the raw predictions and remain the official final-test performance metrics.

### Quantile post-processing

For downstream distributional interpretation, predicted quantiles are converted into a logically coherent order:

```text
0 <= Q1* <= Q2* <= Q3*
```

The corrected quartiles are then used to derive:

```text
predicted IQR = Q3* - Q1*
lower limit   = max(0, Q1* - 1.5 × IQR)
upper limit   = Q3* + 1.5 × IQR
```

This post-processing does not change the raw final-test pinball losses.

### Final distributional diagnostics

The notebook reports:

- empirical Q1, Q2, and Q3 coverage;
- Q1-Q3 interval coverage;
- median predicted IQR;
- low and high conditional outliers.

The raw final-test predictions contain only a small number of quantile-ordering violations, all associated with the independently fitted durum-wheat linear quantiles. The downstream corrected representation resolves them.

### Geographic diagnostics

Province-year observations outside the conditional Tukey-style limits are summarized by region.

This diagnostic is descriptive. It does not compare or reselect models.

### Final linear interpretation

For durum wheat, the selected model is an unregularized linear quantile regression.

A pre-test equivalence check confirms that scaling changes only the parameterization, not the predictions. The final model is therefore fitted without standardization so that coefficients can be interpreted directly in the original feature units.

### National aggregation

The primary modelling output remains the province-level prediction.

National yield is reconstructed by:

1. multiplying each province-level predicted yield by cultivated area;
2. summing implied production across provinces;
3. dividing aggregate production by aggregate cultivated area.

The resulting Q1, Q2, and Q3 series are area-weighted aggregates of province-level forecasts rather than quantiles of a separately fitted national model.

### Current boundary

The notebook has now passed the principal model-selection and final-performance stages.

Remaining project work is more naturally concentrated on:

- deeper interpretation of the nonlinear final models;
- synthesis of the modelling evidence;
- integration with the wider Capstone conclusions and communication layer.

The final test results must not be used retrospectively to change the selected model specifications.

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
- distinguish model-development evidence from final-test evidence;
- never use the final test to revise a frozen model choice;
- avoid user-specific absolute paths;
- never commit credentials or API tokens;
- avoid committing unnecessary large outputs;
- update this README when the role or status of a notebook changes.
