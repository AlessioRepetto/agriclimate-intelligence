# Data

This directory contains the main analytical datasets used by the project notebooks.

The datasets are included in the repository as **static CSV snapshots** so that the exploratory analysis and modelling workflow can be reproduced locally without requiring access to the project's Google Cloud resources.

The project also implements a cloud-based data pipeline using Google Cloud Storage and BigQuery. The local CSV files and the cloud resources therefore provide different access and storage layers for data originating from the same upstream sources.

## Data sources and attribution

The primary agricultural and agro-meteorological data used in this project were obtained from the **European Commission Joint Research Centre (JRC) AGRI4CAST Resources Portal**:

[AGRI4CAST Resources Portal](https://agri4cast.jrc.ec.europa.eu/dataportal)

In particular, the project uses:

* **agricultural production data** obtained from the AGRI4CAST Resources Portal, providing the historical crop production information underlying `production_full_dataset.csv`;
* **JRC MARS gridded agro-meteorological data**, providing the daily meteorological observations used to construct the project's climate and environmental features.

The meteorological source corresponds to the JRC dataset **Gridded Agro-Meteorological Data in Europe**, which provides daily meteorological variables spatially interpolated over the JRC MARS 25 × 25 km grid.

Official dataset reference:

> Toreti, A. (2026). *Gridded Agro-Meteorological Data in Europe*. European Commission, Joint Research Centre (JRC).
> DOI: [10.2905/JRC.SX02E7G](https://doi.org/10.2905/JRC.SX02E7G)

The datasets contained in this repository are **processed analytical derivatives** of these source resources. Attribution to the original data provider therefore remains with the European Commission Joint Research Centre and the AGRI4CAST project.

## Included datasets

The directory contains three versioned datasets:

* `production_full_dataset.csv` — curated agricultural production dataset derived from AGRI4CAST production data, used in the exploratory analysis;
* `climate_full_dataset.csv` — curated climate and environmental dataset derived from JRC MARS gridded agro-meteorological data, after the spatial and temporal processing implemented in this project;
* `modelling_data.csv` — final province × crop × harvest-year analytical dataset integrating agricultural production, climate, environmental and historical features for the modelling notebook.

The first two datasets preserve the richer domain-specific information used during the exploratory phase, while `modelling_data.csv` represents the integrated modelling-ready table produced after the data preparation workflow.

## Cloud data pipeline

The project also implements the data workflow on Google Cloud:

* the original JRC MARS gridded agro-meteorological files downloaded from AGRI4CAST are stored in Google Cloud Storage;
* curated climate and agricultural-production datasets are stored in BigQuery;
* the province × crop × harvest-year modelling table is materialized in BigQuery through the SQL workflow documented under [`../sql/`](../sql/).

The raw gridded agro-meteorological source files amount to approximately **7 GB** in total. They are therefore intentionally kept in Google Cloud Storage rather than versioned in this repository.

Keeping these files in object storage avoids adding several gigabytes of high-granularity source data to Git history while preserving the complete upstream dataset required to rebuild the climate-processing workflow. After spatial and temporal processing, the substantially smaller curated and modelling-ready datasets can instead be versioned as CSV snapshots, making the analytical part of the project directly reproducible without duplicating the full raw data volume.

The corresponding BigQuery modelling resource is:

```text
agriclimate-intelligence.ml.modeling_dataset_v1
```

The SQL scripts used to create and populate the BigQuery datasets are documented in [`../sql/README.md`](../sql/README.md).

## Local and cloud execution

The modelling notebook supports two alternative ways of loading the analytical data:

```text
                         ┌── BigQuery analytical table
Data preparation ────────┤
                         └── versioned local CSV snapshot
```

The local CSV files are the simplest option for reproducing the project after cloning the repository.

BigQuery provides the cloud-side implementation of the same workflow and demonstrates how the analytical dataset can be generated and consumed without relying on local files.

Cloud execution requires valid Google Cloud credentials and permissions for the relevant project resources.

## Reproducing the modelling dataset

The modelling dataset can be reproduced from the curated cloud-side datasets by:

1. obtaining and preparing the source agricultural-production and JRC MARS agro-meteorological data from the AGRI4CAST Resources Portal;
2. processing the raw meteorological files and preparing the curated climate and agricultural-production tables;
3. executing the BigQuery scripts documented in [`../sql/README.md`](../sql/README.md);
4. materializing `agriclimate-intelligence.ml.modeling_dataset_v1`;
5. querying the resulting table directly from the modelling notebook or exporting an equivalent CSV snapshot.

For users interested primarily in reproducing the analysis and modelling results, the versioned `modelling_data.csv` file can instead be used directly.

Rebuilding the complete upstream climate pipeline requires the raw JRC MARS gridded agro-meteorological files. These files are not included in the repository because their combined size is approximately **7 GB**.

## Repository strategy

The project deliberately separates **large source data** from **compact analytical snapshots**.

The original JRC MARS gridded agro-meteorological files are retained in Google Cloud Storage, where several gigabytes of high-granularity data can be managed efficiently without inflating the repository or its Git history. After preprocessing and aggregation, the much smaller analytical datasets are suitable for direct versioning and are included here as static CSV snapshots.

This provides a practical compromise between provenance, reproducibility and repository size:

* the **AGRI4CAST Resources Portal** remains the authoritative upstream source for the agricultural and agro-meteorological data;
* Google Cloud Storage preserves the large raw meteorological inputs required for a complete rebuild;
* BigQuery provides the curated cloud-side analytical layer;
* the versioned CSV files make the exploratory analysis and modelling workflow directly accessible after cloning the repository.

The repository therefore remains self-contained for its main analytical and modelling use cases while preserving clear data provenance and a scalable cloud-side path for full data regeneration.