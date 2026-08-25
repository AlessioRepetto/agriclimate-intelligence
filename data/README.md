# Local data

This directory is reserved for local datasets and intermediate exports used by the project notebooks.

The full data files are intentionally **not versioned in GitHub** because of their size. The repository instead versions the code and SQL transformations used to produce the analytical datasets.

## Data sources and canonical storage

The project data pipeline is built on Google Cloud:

- raw climate files are stored in Google Cloud Storage;
- curated climate and agricultural-production datasets are stored in BigQuery;
- the province × crop × harvest-year modelling table is materialized in BigQuery through the SQL workflow under [`../sql/`](../sql/).

The canonical modelling resource is:

```text
agriclimate-intelligence.ml.modeling_dataset_v1
```

## Local CSV files

Some notebooks can also work with local CSV exports of the same analytical data. These files are useful for local development, repeated experimentation, or execution without issuing a new BigQuery query.

The local files are therefore a **development/cache layer**, not a separate data pipeline or source of truth.

Typical usage is:

```text
BigQuery analytical table
        │
        ├── direct query from notebook
        │
        └── optional local CSV export
```

Any CSV, Parquet, pickle, archive, or other dataset placed under `data/` is excluded from version control by the repository `.gitignore`.

## Reproducing the modelling data

To reproduce the modelling dataset from the cloud-side curated tables:

1. prepare the curated climate and agricultural-production tables;
2. execute the BigQuery scripts documented in [`../sql/README.md`](../sql/README.md);
3. load `agriclimate-intelligence.ml.modeling_dataset_v1` directly from the modelling notebook, or export an equivalent local copy under this directory if preferred.

Cloud access requires valid Google Cloud credentials and permissions for the relevant project resources.

## Why the data are not included

The omission of the full datasets is intentional. The repository is designed to document the **data-engineering, analytical and modelling workflow**, while avoiding the duplication of large generated data assets inside Git history.
