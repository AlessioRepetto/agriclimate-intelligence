# Notebooks

This directory contains the complete executable analytical workflow for **AgriClimate Intelligence**, from source-data transformation to final crop-yield modelling and interpretation.

The main analysis is complete. The notebooks are organized so that the data-engineering logic, exploratory reasoning, feature engineering and model-development decisions remain inspectable rather than being hidden behind a single pipeline.

## Notebook overview

| Notebook | Purpose | Main output | Status |
| --- | --- | --- | --- |
| `ETL_Climate_Example.ipynb` | Demonstrate and validate the climate transformation on one source territory | One fully inspected monthly provincial climate example | Complete |
| `ETL_Climate_Data.ipynb` | Run the climate ETL across all mapped Italian areas | Consolidated monthly provincial climate dataset | Complete |
| `ETL_Production_Data.ipynb` | Harmonize agricultural area, production and yield data | Curated province × crop × year production dataset | Complete |
| `EDA_AgriClimate_Intelligence.ipynb` | Integrate curated data, analyse yield/climate patterns and engineer crop-season predictors | Analytical findings + modelling dataset | Complete |
| `ML_Quantile_Modelling.ipynb` | Develop, select, test and interpret crop-specific probabilistic models | Final models, 2019–2022 test results, SHAP and territorial diagnostics | Complete |

## Workflow

```text
ETL_Climate_Example.ipynb
        │
        │ validates
        ▼
src/province_transformation.py
        │
        ▼
ETL_Climate_Data.ipynb ────────────┐
                                   │
                                   ├──► curated cloud datasets
                                   │             │
ETL_Production_Data.ipynb ─────────┘             ▼
                                   EDA_AgriClimate_Intelligence.ipynb
                                                  │
                                                  │ crop calendar
                                                  │ phase features
                                                  │ historical features
                                                  ▼
                                      ML_Quantile_Modelling.ipynb
                                                  │
                                                  ├── temporal development CV
                                                  ├── outer validation
                                                  ├── frozen model selection
                                                  ├── 2019–2022 final test
                                                  ├── SHAP interpretation
                                                  └── territorial diagnostics
```

## Recommended reading order

For the full workflow:

```text
1. ETL_Climate_Example.ipynb
2. ETL_Climate_Data.ipynb
3. ETL_Production_Data.ipynb
4. EDA_AgriClimate_Intelligence.ipynb
5. ML_Quantile_Modelling.ipynb
```

For a portfolio-oriented review, starting directly from the EDA and modelling notebooks is usually sufficient.

---

## `ETL_Climate_Example.ipynb`

### Purpose

This notebook exposes the full climate transformation on a single provincial source file before the same logic is executed in batch.

It is primarily a **validation and transparency notebook**.

### Main operations

The workflow:

- configures project and cloud paths;
- reads one compressed daily climate file from Google Cloud Storage;
- checks raw structure and types;
- validates dates and numerical values;
- inspects missing observations and duplicate cell–day keys;
- verifies grid consistency through time;
- checks temperature ordering and repairs inconsistent minimum/average/maximum values where possible;
- derives daily provincial indicators from the underlying grid cells;
- aggregates the resulting information to month;
- inspects both intermediate and final outputs.

### Why it exists

The production ETL delegates reusable transformations to `src/province_transformation.py`.

This notebook makes that logic inspectable on one manageable case and is the preferred place to diagnose source-format or transformation issues before rerunning the national batch.

---

## `ETL_Climate_Data.ipynb`

### Purpose

This notebook orchestrates the complete climate-data transformation across the mapped Italian production areas.

### Main operations

It:

- maps production territories to the appropriate source climate files;
- reads compressed climate data from Google Cloud Storage;
- combines multiple historical source areas where administrative boundaries require it;
- removes duplicate cell–day observations caused by territorial overlap;
- applies the reusable transformation in `src/province_transformation.py`;
- assigns final province and region labels;
- concatenates the monthly outputs;
- validates the complete dataset;
- exports the curated climate table.

### Resulting climate representation

The final monthly provincial data preserve information about:

- temperature levels and local extremes;
- spatial temperature variability;
- precipitation totals and intensity;
- wetness and dryness;
- wind;
- vapour pressure;
- evapotranspiration;
- radiation;
- event frequency;
- territorial share affected by events;
- longest event sequences;
- altitude.

The curated climate history covers **1980–2025**.

---

## `ETL_Production_Data.ipynb`

### Purpose

This notebook transforms the agricultural source into a consistent structure that can be combined with climate information.

### Observation unit

```text
province × crop × harvest year
```

### Main operations

The workflow:

- reads the production source;
- retains cultivated area, production and yield information;
- distinguishes missing observations from structural zeroes;
- harmonizes territorial definitions;
- reconstructs or aggregates selected historical areas where required;
- recalculates yield from area and total production when appropriate;
- preserves provenance and quality information;
- reshapes the source into long format;
- validates the final observation key;
- exports the curated production table.

### Quality fields

Dedicated `q_*` fields retain information about:

- territorial coverage;
- source completeness;
- structural zeroes;
- reconstructed territories;
- calculation status;
- area–production–yield coherence.

This allows later notebooks to distinguish source-data limitations from genuine agricultural patterns.

---

## `EDA_AgriClimate_Intelligence.ipynb`

### Purpose

This notebook performs the project's main **Data Understanding and feature-engineering** work.

Its role is not limited to visualization. It defines how the raw climate and production histories become a valid supervised-learning problem.

### Main analytical areas

The notebook covers:

- data structure and internal consistency;
- temporal and territorial completeness;
- production-data quality flags;
- univariate production and climate distributions;
- yield variation through time;
- macro-regional differences;
- robust long-term yield trends;
- partial autocorrelation;
- altitude;
- crop calendars and agricultural phases;
- climate behaviour across crop phases;
- bivariate climate–yield relationships;
- crop-specific feature rankings;
- geographical comparison of relevant climate indicators;
- preparation of the final modelling table.

### Crop-season engineering

Annual harvest yield is not matched mechanically to calendar-year climate.

Climate variables are reorganized around the relevant crop cycle and aggregated into agronomically meaningful phases such as:

```text
planting / early vegetative
vegetative / reproductive
ripening / harvest
```

This allows the same physical variable to play different predictive roles depending on when it occurs in the crop cycle.

### Main modelling hand-off

The EDA produces the feature representation used by the modelling notebook.

The current modelling table contains:

```text
7,576 supervised observations
4 historical yield predictors
192 crop-phase climate predictors
```

Current-year area, production and yield are not used as predictors.

### Important analytical finding

Several strong pooled climate–yield relationships also have a marked spatial footprint.

This is particularly important for durum wheat, where yield, evapotranspiration, radiation, wind and frost exposure all show strong macro-regional structure. The modelling stage later demonstrates that much of this persistent spatial information is already summarized effectively by historical provincial and regional yield.

---

## `ML_Quantile_Modelling.ipynb`

### Purpose

This notebook contains the complete crop-specific model-development and evaluation workflow.

It models:

```text
Durum wheat
Soft wheat
Grain maize
```

The target is probabilistic rather than purely point-based:

```text
Q1 = 0.25
Q2 = 0.50
Q3 = 0.75
```

Q2 is the primary model-selection objective and all three quantiles are evaluated with pinball loss.

## Temporal design

All validation respects time order.

### Inner development folds

```text
train through 2006 → validate on 2007–2009
train through 2009 → validate on 2010–2012
train through 2012 → validate on 2013–2015
```

### Outer model-selection validation

```text
2016–2018
```

### Final test

```text
2019–2022
```

The final test does not influence feature selection, early stopping, hyperparameters, model-family comparison or final model choice.

## Modelling sequence

### 1. Naive persistence benchmark

Previous-year yield establishes a minimum level of forecasting skill.

The first learned historical model improves mean temporal-CV Q2 pinball loss over persistence for all three crops.
This comparison refers to the development-period temporal folds. After model selection is frozen, the naive benchmark is evaluated again on the independent 2019–2022 test period to quantify the incremental median predictive skill of the final models.

### 2. Historical linear quantile model

`Linear H` uses:

```text
yield_lag_1
yield_lag_1_missing
5-year provincial rolling yield median
5-year regional rolling yield median
```

The rolling summaries use only observations from previous calendar years.

### 3. Sequential Forward Selection

SFS allows historical and climate predictors to compete in the same candidate pool.

It is run separately by crop using **linear quantile regression** as the wrapper estimator, chronological CV and Q2 pinball loss. The resulting subsets are therefore model-specific to the linear estimator.

Repeating the complete wrapper search independently for CatBoost and especially for the hosted TabPFN model would require substantially greater computational and API resources. The linear-SFS subsets are consequently reused as predefined compact feature representations for the nonlinear models, while the `Full` feature set is also evaluated to test whether those models benefit from information excluded by the linear wrapper.

The retained sets contain:

| Crop | Total | Historical | Climate |
| --- | ---: | ---: | ---: |
| Durum wheat | 12 | 3 | 9 |
| Soft wheat | 18 | 3 | 15 |
| Grain maize | 25 | 4 | 21 |

The completed search is stored explicitly in the notebook rather than rerun on every execution.

### 4. Temporal stability

Historical and SFS linear specifications are compared fold by fold to determine whether average gains are stable through time.

### 5. L1 regularization

A deliberately narrow sensitivity experiment tests whether coefficient shrinkage improves the SFS linear specifications.

### 6. CatBoost

CatBoost provides a conventional nonlinear tabular comparison.

Early stopping uses only the most recent years inside the training window. The external validation period is never used for stopping decisions.

### 7. Outer validation

The strongest conventional specifications are evaluated on 2016–2018.

### 8. TabPFN

TabPFN introduces a tabular foundation model comparison using:

- historical features;
- SFS-selected features;
- the full candidate feature set.

Native numerical missing values are preserved where the model supports them.

### 9. Model-selection tie-breakers

When outer-validation candidates are sufficiently close, selection is not based mechanically on the smallest single score.

The notebook uses:

- temporal robustness across all pre-test folds;
- Q1/Q2/Q3 predictive behaviour;
- calibration information where relevant.

### 10. Frozen final models

The final choices are:

| Crop | Model |
| --- | --- |
| Durum wheat | `Linear H` |
| Grain maize | `TabPFN SFS` |
| Soft wheat | `TabPFN Full` |

These choices are frozen before test access.

### 11. Final refit and 2019–2022 test

The selected models are refitted on all admissible **1995–2018** observations and evaluated once on **2019–2022**.

Final pinball losses are:

| Crop | Model | Test Q1 | Test Q2 | Test Q3 |
| --- | --- | ---: | ---: | ---: |
| Durum wheat | `Linear H` | 0.1756 | **0.2106** | 0.1898 |
| Grain maize | `TabPFN SFS` | 0.3348 | **0.3759** | 0.2965 |
| Soft wheat | `TabPFN Full` | 0.1978 | **0.2393** | 0.2026 |

The values above are calculated from the raw model predictions and are the official final-test results.

### 12. Final models vs naive persistence

The frozen final models are also compared with the naive persistence benchmark on the independent 2019–2022 test period.

For Q2 pinball loss, the relative improvements over persistence are:

| Crop | Final model | Improvement over naive |
| --- | --- | ---: |
| Durum wheat | `Linear H` | **0.2%** |
| Grain maize | `TabPFN SFS` | **14.8%** |
| Soft wheat | `TabPFN Full` | **1.0%** |

All three final models outperform persistence, but the magnitude of the gain differs substantially.

Grain maize provides the clearest evidence of incremental median predictive skill beyond previous-year yield. Soft wheat improves only modestly over persistence, while the durum-wheat model is essentially tied with the naive benchmark on Q2.

This comparison evaluates **median predictive skill only**. Unlike the persistence benchmark, the selected models also estimate Q1 and Q3 and therefore provide conditional uncertainty information.

### 13. Distributional diagnostics

The predicted quartiles are subsequently made non-negative and monotonically ordered for downstream interpretation:

```text
0 ≤ Q1* ≤ Q2* ≤ Q3*
```

The corrected distribution is used to derive:

- conditional interquartile range;
- Tukey-style lower and upper limits;
- empirical quantile coverage;
- Q1–Q3 interval coverage;
- low and high conditional outliers.

The Q1–Q3 empirical coverage is close to the nominal 50% for all three crops.

### 14. Year-specific and geographical diagnostics

The final test is also examined by year and by region.

This is diagnostic only: it does not reopen model selection.

### 15. Linear-model interpretation

The final durum-wheat model is refitted without standardization after a numerical equivalence check confirms that scaling does not alter predictions for the unregularized linear specification.

This makes the Q1/Q2/Q3 equations directly interpretable in the original feature units.

### 16. TabPFN interpretation with SHAP

The final soft-wheat and maize TabPFN models are interpreted after model selection using SHAP values estimated through the TabPFN/shapiq workflow.

The analysis shows:

- a concentrated historical + targeted climate structure for grain maize;
- a strong historical backbone plus distributed environmental information for soft wheat.

These attribution patterns describe how the fitted models construct their predictions and should not be interpreted directly as incremental predictive skill. On the final test, the richer TabPFN representation produces a substantial Q2 gain over persistence for grain maize, but only a modest gain for soft wheat.

### 17. National and territorial aggregation

Province-level yield predictions remain the primary model output.

For aggregation, yield is first converted into implied production using cultivated area. Production is then summed and aggregate yield reconstructed from:

```text
total predicted production / total cultivated area
```

This avoids treating provinces with very different cultivated areas as equally important.

The final notebook provides both national plots and selected macro-regional views.

## Final synthesis

Across the three crops, the modelling evidence supports a common structure:

> **Recent history and persistent geography establish the expected productivity of a territory; current-season climate modifies that baseline when it contains additional predictive information.**

The form and predictive value of the additional information differ substantially by crop:

- **Durum wheat:** historical productivity dominates, and the final linear model is essentially tied with previous-year persistence for median prediction on the final test. Climate relationships observed in the EDA appear largely entangled with persistent geographical structure.
- **Grain maize:** a compact combination of historical and seasonal predictors produces the clearest incremental forecasting gain, reducing final-test Q2 pinball loss by approximately **14.8%** relative to persistence.
- **Soft wheat:** the fitted TabPFN model uses a broader multivariate environmental representation, but this additional complexity translates into only about **1.0%** improvement in final-test Q2 loss over persistence.

The interpretation is predictive rather than causal.

---

## Data access

The curated datasets are available through Google Cloud Storage and BigQuery.

The modelling notebook supports loading the modelling dataset from BigQuery, while the equivalent local CSV structure is retained as a reproducible local-data option where applicable.

Large source and generated datasets are not stored directly in the Git repository.

## Authentication

### Google Cloud

```bash
gcloud auth application-default login
```

### TabPFN

The TabPFN access token must be supplied through local environment configuration, for example a `.env` file excluded from Git.

Never commit credentials or API tokens.

For reproducibility, the `tabpfn-client` package version is pinned in the project requirements. Because inference is served remotely, the notebook also records the API checkpoint used for the reported experiments:

`tabpfn-v3-regressor-v3_default.ckpt`

## Notebook conventions

When modifying the notebooks:

- preserve top-to-bottom execution;
- keep chronological validation explicit;
- keep final-test evidence separate from model-selection evidence;
- keep reusable project utilities in `src/` and import them through the `src` package;
- distinguish predictive interpretation from causal claims;
- keep credentials and generated private data outside Git;
- document any methodological change that would alter reported results.
