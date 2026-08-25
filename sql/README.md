# BigQuery SQL workflow

This directory contains the BigQuery Standard SQL scripts used to build the analytical table consumed by the machine-learning workflow.

The scripts were developed as part of the project pipeline and executed directly in BigQuery. Some of the repetitive phase-level SQL expressions were generated programmatically during development to reduce manual errors, but the versioned `.sql` files are the final warehouse artefacts used by the project.

## Execution order

Run the scripts in numerical order:

| Script | Purpose |
| --- | --- |
| `000_crop_calendar.sql` | Defines the crop calendar and maps crop months to agronomic phases and harvest years. |
| `010_dim_province.sql` | Builds the province-level territorial dimension used by the analytical workflow. |
| `020_climate_aggregation_rules.sql` | Exposes and validates the aggregation policy associated with the climate-variable naming convention. |
| `030_modeling_dataset.sql` | Materializes the final province × crop × harvest-year modelling table, including phase-level climate features and historical yield predictors. |

## Main inputs

The workflow expects the curated BigQuery resources produced by the upstream ETL:

```text
agriclimate-intelligence.curated.climate_full_dataset_v1
agriclimate-intelligence.curated.production_full_dataset_v1
```

The scripts also create or use supporting resources under the project `utilities` dataset and materialize the final modelling table under the `ml` dataset.

## Main output

The modelling workflow consumes:

```text
agriclimate-intelligence.ml.modeling_dataset_v1
```

Its observation unit is:

```text
province × crop × harvest year
```

For observations with an available target, the final dataset contains the historical production predictors together with the crop-phase climate representation used during model development.

## Climate aggregation policy

The monthly climate schema contains variables that require different temporal aggregation rules when converted into agronomic phases. The project infers those rules from the variable naming convention rather than maintaining an independent manual list for every feature.

`020_climate_aggregation_rules.sql` makes this policy explicit and checks that the current climate schema is covered by a defined aggregation rule.

The final expressions contained in `030_modeling_dataset.sql` correspond to the climate schema and aggregation policy used for the completed project dataset. They should therefore be reviewed if the upstream climate schema or naming convention changes.

## Historical yield features

The modelling table includes lagged and rolling historical-yield information.

The previous-year yield is obtained by matching the expected previous calendar year rather than by simply taking the preceding available row. This preserves genuine missing years instead of silently jumping over them.

Current-year production, cultivated area and realised yield are not used as model predictors.

## Running the scripts elsewhere

The files contain the Google Cloud project and dataset identifiers used for this project. To reproduce the workflow in another BigQuery environment, replace those identifiers with the corresponding project and dataset names and ensure that the expected upstream schemas are available.

The SQL files do not contain credentials. Authentication and access permissions are managed through Google Cloud.

## Relationship with the notebooks

The SQL layer is the hand-off between the curated cloud data and the machine-learning workflow:

```text
Curated BigQuery tables
        │
        ▼
BigQuery SQL in this directory
        │
        ▼
ml.modeling_dataset_v1
        │
        ├── direct BigQuery load
        └── optional local CSV export
                │
                ▼
ML_Quantile_Modelling.ipynb
```

For the wider analytical workflow, see the repository-level [`README.md`](../README.md) and [`../notebooks/README.md`](../notebooks/README.md).
