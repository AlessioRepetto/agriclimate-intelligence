import numpy as np
import pandas as pd


REQUIRED_COLUMNS = [
    "IDCELL",
    "LATITUDE",
    "LONGITUDE",
    "ALTITUDE",
    "DAY",
    "TEMPERATURE_MAX",
    "TEMPERATURE_MIN",
    "TEMPERATURE_AVG",
    "WINDSPEED",
    "VAPOURPRESSURE",
    "PRECIPITATION",
    "ET0",
    "RADIATION",
]

NUMERIC_COLUMNS = [
    #"LATITUDE",
    #"LONGITUDE",
    "ALTITUDE",
    "TEMPERATURE_MAX",
    "TEMPERATURE_MIN",
    "TEMPERATURE_AVG",
    "WINDSPEED",
    "VAPOURPRESSURE",
    "PRECIPITATION",
    "ET0",
    "RADIATION",
]

NON_NEGATIVE_COLUMNS = [
    "WINDSPEED",
    "PRECIPITATION",
    "ET0",
    "RADIATION",
]

FLAG_COLUMNS = [
    "FROST",
    "HOT_30",
    "HOT_35",
    "RAIN_20",
    "RAIN_50",
    "EXTREME_HEAT",
    "VERY_EXTREME_HEAT",
    "EXTREME_COLD",
    "EXTREME_RAIN",
    "VERY_EXTREME_RAIN",
    "EXTREME_WIND",
    "WET_CELL",
]

STREAK_FLAGS = {
    "MAX_CONSECUTIVE_EXTREME_HEAT_DAYS": "EXTREME_HEAT_DAY",
    "MAX_CONSECUTIVE_VERY_EXTREME_HEAT_DAYS": "VERY_EXTREME_HEAT_DAY",
    "MAX_CONSECUTIVE_EXTREME_COLD_DAYS": "EXTREME_COLD_DAY",
    "MAX_CONSECUTIVE_EXTREME_RAIN_DAYS": "EXTREME_RAIN_DAY",
    "MAX_CONSECUTIVE_VERY_EXTREME_RAIN_DAYS": "VERY_EXTREME_RAIN_DAY",
    "MAX_CONSECUTIVE_EXTREME_WIND_DAYS": "EXTREME_WIND_DAY",
    "MAX_CONSECUTIVE_DRY_DAYS_AREA_MEAN": "DRY_DAY_AREA_MEAN",
    "MAX_CONSECUTIVE_WET_DAYS_AREA_MEAN": "WET_DAY_AREA_MEAN",
    "MAX_CONSECUTIVE_FROST_10PCT_DAYS": "FROST_DAY_10PCT",
    "MAX_CONSECUTIVE_HOT_30_10PCT_DAYS": "HOT_30_DAY_10PCT",
    "MAX_CONSECUTIVE_HOT_35_10PCT_DAYS": "HOT_35_DAY_10PCT",
}

REFERENCE_END_YEAR = 2010
MINIMUM_AREA_FRACTION = 0.10
WET_CELL_THRESHOLD = 1.0

ALTERNATIVE_DATE_FORMAT = (
    "agrigento.csv", 
    "campobasso.csv",
    "chieti.csv",
    "enna.csv",
    "genova.csv",
    "la spezia.csv",
    "lecce.csv",
    "livorno.csv",
    "oristano.csv",
    "parma.csv"
    )


# Adds the optional source name to validation errors without changing the output dataframe.
def _error_message(message, source_name):
    if source_name is None:
        return message

    return f"Dataset '{source_name}': {message}"


# Converts dates and numerical fields to the types required by the transformation.
def _prepare_input_dataframe(df, source_name):
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            _error_message(
                "the input object must be a pandas DataFrame.",
                source_name,
            )
        )

    if df.empty:
        raise ValueError(
            _error_message(
                "the dataframe is empty.",
                source_name,
            )
        )

    duplicated_column_names = df.columns[df.columns.duplicated()].tolist()
    if duplicated_column_names:
        raise ValueError(
            _error_message(
                "duplicated column names were found: "
                + ", ".join(map(str, duplicated_column_names)),
                source_name,
            )
        )

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]
    if missing_columns:
        raise ValueError(
            _error_message(
                "required columns are missing: "
                + ", ".join(missing_columns),
                source_name,
            )
        )

    prepared = df.copy()

    null_counts = prepared[REQUIRED_COLUMNS].isna().sum()
    null_counts = null_counts[null_counts > 0]
    if not null_counts.empty:
        details = ", ".join(
            f"{column}={count}"
            for column, count in null_counts.items()
        )
        raise ValueError(
            _error_message(
                "null values were found in required columns: " + details,
                source_name,
            )
        )

    try:
        #date_format = ("%d/%m/%Y %H:%M" if source_name in ALTERNATIVE_DATE_FORMAT else "%Y-%m-%d %H:%M:%S")
        
        prepared["DAY"] = pd.to_datetime(
            prepared["DAY"],
            format="%Y-%m-%d %H:%M:%S",
            errors="raise",
        ).dt.normalize()
    except (TypeError, ValueError) as error:
        raise ValueError(
            _error_message(
                "the DAY column contains values that cannot be converted to valid dates.",
                source_name,
            )
        ) from error

    invalid_numeric_columns = []
    for column in NUMERIC_COLUMNS:
        try:
            prepared[column] = pd.to_numeric(
                prepared[column],
                errors="raise",
            )
        except (TypeError, ValueError):
            invalid_numeric_columns.append(column)

    if invalid_numeric_columns:
        raise ValueError(
            _error_message(
                "non-numeric values were found in these columns: "
                + ", ".join(invalid_numeric_columns),
                source_name,
            )
        )

    return prepared

# Reorders the three existing temperature values from minimum to maximum.
def _reorder_temperature_columns(df):
    temperature_columns = [
        "TEMPERATURE_MIN",
        "TEMPERATURE_AVG",
        "TEMPERATURE_MAX",
    ]

    df.loc[:, temperature_columns] = np.sort(
        df[temperature_columns].to_numpy(),
        axis=1,
    )

    return df


# Runs the integrity checks that were previously inspected visually in the notebook.
def _validate_input_dataframe(df, source_name):
    duplicated_rows = df.duplicated(
        subset=["IDCELL", "DAY"],
        keep=False,
    )
    if duplicated_rows.any():
        examples = (
            df.loc[duplicated_rows, ["IDCELL", "DAY"]]
            .sort_values(["IDCELL", "DAY"])
            .head(10)
            .to_string(index=False)
        )
        raise ValueError(
            _error_message(
                f"{int(duplicated_rows.sum())} rows have duplicated IDCELL-DAY keys. "
                "First duplicated keys:\n"
                + examples,
                source_name,
            )
        )

    cell_geography = (
        df.groupby("IDCELL", observed=True)
        .agg(
            latitude_values=("LATITUDE", "nunique"),
            longitude_values=("LONGITUDE", "nunique"),
            altitude_values=("ALTITUDE", "nunique"),
        )
    )

    inconsistent_geography = cell_geography.ne(1).any(axis=1)
    if inconsistent_geography.any():
        details = (
            cell_geography.loc[inconsistent_geography]
            .head(20)
            .to_string()
        )
        raise ValueError(
            _error_message(
                "some cell IDs are associated with changing latitude, longitude, or altitude values. "
                "First inconsistent cells:\n"
                + details,
                source_name,
            )
        )

    expected_cells = df["IDCELL"].nunique()
    cells_by_day = df.groupby("DAY", observed=True)["IDCELL"].nunique()
    incomplete_days = cells_by_day[cells_by_day != expected_cells]
    if not incomplete_days.empty:
        details = ", ".join(
            f"{day:%Y-%m-%d}={count}"
            for day, count in incomplete_days.head(20).items()
        )
        raise ValueError(
            _error_message(
                f"the set of grid cells is not constant over time. Expected {expected_cells} cells per day; "
                "problematic dates and observed counts: "
                + details,
                source_name,
            )
        )

    invalid_temperatures = (
        (df["TEMPERATURE_MIN"] > df["TEMPERATURE_AVG"])
        | (df["TEMPERATURE_AVG"] > df["TEMPERATURE_MAX"])
        | (df["TEMPERATURE_MIN"] > df["TEMPERATURE_MAX"])
    )
    if invalid_temperatures.any():
        examples = (
            df.loc[
                invalid_temperatures,
                [
                    "IDCELL",
                    "DAY",
                    "TEMPERATURE_MIN",
                    "TEMPERATURE_AVG",
                    "TEMPERATURE_MAX",
                ],
            ]
            .head(10)
            .to_string(index=False)
        )
        raise ValueError(
            _error_message(
                f"{int(invalid_temperatures.sum())} rows contain inconsistent temperatures. "
                "TEMPERATURE_MIN must be <= TEMPERATURE_AVG <= TEMPERATURE_MAX. "
                "First invalid rows:\n"
                + examples,
                source_name,
            )
        )

    negative_counts = {
        column: int((df[column] < 0).sum())
        for column in NON_NEGATIVE_COLUMNS
        if (df[column] < 0).any()
    }
    if negative_counts:
        details = ", ".join(
            f"{column}={count}"
            for column, count in negative_counts.items()
        )
        raise ValueError(
            _error_message(
                "negative values were found in columns that must be non-negative: "
                + details,
                source_name,
            )
        )


# Adds the calendar fields used by the threshold and monthly aggregation steps.
def _add_calendar_columns(df):
    result = df.copy()
    result["YEAR"] = result["DAY"].dt.year
    result["MONTH"] = result["DAY"].dt.month
    result["YEAR_MONTH"] = result["DAY"].dt.to_period("M")
    result["DAY_OF_YEAR"] = result["DAY"].dt.dayofyear
    return result


# Computes monthly reference thresholds using observations up to and including 2010.
def _calculate_thresholds(df, source_name):
    reference = df.loc[df["YEAR"] <= REFERENCE_END_YEAR]

    if reference.empty:
        raise ValueError(
            _error_message(
                f"no observations are available up to {REFERENCE_END_YEAR}, so reference thresholds cannot be calculated.",
                source_name,
            )
        )

    available_months = set(reference["MONTH"].unique())
    missing_months = sorted(set(range(1, 13)) - available_months)
    if missing_months:
        raise ValueError(
            _error_message(
                "the reference period does not contain observations for all calendar months. Missing months: "
                + ", ".join(map(str, missing_months)),
                source_name,
            )
        )

    temperature_thresholds = (
        reference.groupby("MONTH", observed=True)
        .agg(
            TMAX_P90=(
                "TEMPERATURE_MAX",
                lambda values: values.quantile(0.90),
            ),
            TMAX_P95=(
                "TEMPERATURE_MAX",
                lambda values: values.quantile(0.95),
            ),
            TMIN_P10=(
                "TEMPERATURE_MIN",
                lambda values: values.quantile(0.10),
            ),
        )
        .reset_index()
    )

    wind_thresholds = (
        reference.groupby("MONTH", observed=True)
        .agg(
            WIND_P95=(
                "WINDSPEED",
                lambda values: values.quantile(0.95),
            )
        )
        .reset_index()
    )

    positive_precipitation = reference.loc[
        reference["PRECIPITATION"] > 0
    ]
    wet_reference_months = set(positive_precipitation["MONTH"].unique())
    missing_wet_months = sorted(set(range(1, 13)) - wet_reference_months)
    if missing_wet_months:
        raise ValueError(
            _error_message(
                "precipitation thresholds cannot be calculated because the reference period has no positive precipitation "
                "for these months: "
                + ", ".join(map(str, missing_wet_months)),
                source_name,
            )
        )

    precipitation_thresholds = (
        positive_precipitation.groupby("MONTH", observed=True)
        .agg(
            PRECIP_P95=(
                "PRECIPITATION",
                lambda values: values.quantile(0.95),
            ),
            PRECIP_P99=(
                "PRECIPITATION",
                lambda values: values.quantile(0.99),
            ),
        )
        .reset_index()
    )

    thresholds = temperature_thresholds.merge(
        precipitation_thresholds,
        on="MONTH",
        how="left",
        validate="one_to_one",
    )

    thresholds = thresholds.merge(
        wind_thresholds,
        on="MONTH",
        how="left",
        validate="one_to_one",
    )

    threshold_columns = [
        "TMAX_P90",
        "TMAX_P95",
        "TMIN_P10",
        "PRECIP_P95",
        "PRECIP_P99",
        "WIND_P95",
    ]
    if thresholds[threshold_columns].isna().any().any():
        raise ValueError(
            _error_message(
                "one or more reference thresholds could not be calculated.",
                source_name,
            )
        )

    return thresholds


# Adds fixed-threshold and reference-threshold indicators at cell-day level.
def _add_cell_level_indicators(df, thresholds):
    result = df.merge(
        thresholds,
        on="MONTH",
        how="left",
        validate="many_to_one",
    )

    result["WET_CELL"] = (
        result["PRECIPITATION"] >= WET_CELL_THRESHOLD
    )

    result["FROST"] = result["TEMPERATURE_MIN"] < 0
    result["HOT_30"] = result["TEMPERATURE_MAX"] >= 30
    result["HOT_35"] = result["TEMPERATURE_MAX"] >= 35
    result["RAIN_20"] = result["PRECIPITATION"] >= 20
    result["RAIN_50"] = result["PRECIPITATION"] >= 50

    result["EXTREME_HEAT"] = (
        result["TEMPERATURE_MAX"] > result["TMAX_P90"]
    )
    result["VERY_EXTREME_HEAT"] = (
        result["TEMPERATURE_MAX"] > result["TMAX_P95"]
    )
    result["EXTREME_COLD"] = (
        result["TEMPERATURE_MIN"] < result["TMIN_P10"]
    )
    result["EXTREME_RAIN"] = (
        (result["PRECIPITATION"] >= WET_CELL_THRESHOLD)
        & (result["PRECIPITATION"] > result["PRECIP_P95"])
    )
    result["VERY_EXTREME_RAIN"] = (
        (result["PRECIPITATION"] >= WET_CELL_THRESHOLD)
        & (result["PRECIPITATION"] > result["PRECIP_P99"])
    )
    result["EXTREME_WIND"] = (
        result["WINDSPEED"] > result["WIND_P95"]
    )

    return result


# Aggregates cell-day observations into the temporary daily provincial dataframe.
def _aggregate_to_daily_province(df, area_weight):
    rows = []
    expected_cells = df["IDCELL"].nunique()

    for day, group in df.groupby(
        "DAY",
        sort=True,
        observed=True,
    ):
        n_observed_cells = group["IDCELL"].nunique()

        if n_observed_cells != expected_cells:
            raise ValueError(
                f"The day {day:%Y-%m-%d} contains {n_observed_cells} cells, while {expected_cells} were expected."
            )

        row = {
            "DAY": day,
            "N_CELLS": n_observed_cells,
            "TEMPERATURE_AVG_AREA": group["TEMPERATURE_AVG"].mean(),
            "TEMPERATURE_MAX_AREA": group["TEMPERATURE_MAX"].mean(),
            "TEMPERATURE_MIN_AREA": group["TEMPERATURE_MIN"].mean(),
            "TEMPERATURE_MAX_LOCAL": group["TEMPERATURE_MAX"].max(),
            "TEMPERATURE_MIN_LOCAL": group["TEMPERATURE_MIN"].min(),
            "TEMPERATURE_SPATIAL_STD": group["TEMPERATURE_AVG"].std(),
            "PRECIPITATION_AREA": group["PRECIPITATION"].mean(),
            "PRECIPITATION_LOCAL_MAX": group["PRECIPITATION"].max(),
            "PRECIPITATION_SPATIAL_STD": group["PRECIPITATION"].std(),
            "WINDSPEED_AREA": group["WINDSPEED"].mean(),
            "WINDSPEED_LOCAL_MAX": group["WINDSPEED"].max(),
            "VAPOURPRESSURE_AREA": group["VAPOURPRESSURE"].mean(),
            "ET0_AREA": group["ET0"].mean(),
            "RADIATION_AREA": group["RADIATION"].mean(),
        }

        for flag in FLAG_COLUMNS:
            affected_cells = int(group[flag].sum())
            row[f"{flag}_AREA_FRACTION"] = (
                affected_cells * area_weight
            )

        rows.append(row)

    daily = pd.DataFrame(rows)
    daily["YEAR"] = daily["DAY"].dt.year
    daily["MONTH"] = daily["DAY"].dt.month
    daily["YEAR_MONTH"] = daily["DAY"].dt.to_period("M")

    return daily


# Converts daily area fractions and provincial averages into daily event flags.
def _add_daily_province_flags(daily):
    result = daily.copy()

    result["EXTREME_RAIN_DAY"] = (
        result["EXTREME_RAIN_AREA_FRACTION"]
        >= MINIMUM_AREA_FRACTION
    )
    result["VERY_EXTREME_RAIN_DAY"] = (
        result["VERY_EXTREME_RAIN_AREA_FRACTION"]
        >= MINIMUM_AREA_FRACTION
    )
    result["EXTREME_HEAT_DAY"] = (
        result["EXTREME_HEAT_AREA_FRACTION"]
        >= MINIMUM_AREA_FRACTION
    )
    result["VERY_EXTREME_HEAT_DAY"] = (
        result["VERY_EXTREME_HEAT_AREA_FRACTION"]
        >= MINIMUM_AREA_FRACTION
    )
    result["EXTREME_COLD_DAY"] = (
        result["EXTREME_COLD_AREA_FRACTION"]
        >= MINIMUM_AREA_FRACTION
    )
    result["EXTREME_WIND_DAY"] = (
        result["EXTREME_WIND_AREA_FRACTION"]
        >= MINIMUM_AREA_FRACTION
    )
    result["RAIN_20_DAY"] = (
        result["RAIN_20_AREA_FRACTION"]
        >= MINIMUM_AREA_FRACTION
    )
    result["RAIN_50_DAY"] = (
        result["RAIN_50_AREA_FRACTION"]
        >= MINIMUM_AREA_FRACTION
    )
    result["WET_DAY_AREA_MEAN"] = (
        result["PRECIPITATION_AREA"] >= WET_CELL_THRESHOLD
    )
    result["WET_DAY_SPATIAL"] = (
        result["WET_CELL_AREA_FRACTION"]
        >= MINIMUM_AREA_FRACTION
    )
    result["DRY_DAY_AREA_MEAN"] = (
        result["PRECIPITATION_AREA"] < WET_CELL_THRESHOLD
    )
    result["DRY_DAY_ALL_CELLS"] = (
        result["WET_CELL_AREA_FRACTION"] == 0
    )
    result["FROST_DAY_10PCT"] = (
        result["FROST_AREA_FRACTION"]
        >= MINIMUM_AREA_FRACTION
    )
    result["HOT_30_DAY_10PCT"] = (
        result["HOT_30_AREA_FRACTION"]
        >= MINIMUM_AREA_FRACTION
    )
    result["HOT_35_DAY_10PCT"] = (
        result["HOT_35_AREA_FRACTION"]
        >= MINIMUM_AREA_FRACTION
    )

    return result


# Computes a mean using only values greater than zero and returns zero when none are present.
def _mean_when_positive(values):
    positive_values = values[values > 0]

    if positive_values.empty:
        return 0.0

    return positive_values.mean()


# Computes the longest sequence of consecutive calendar days for one daily event flag.
def _longest_consecutive_event_days(group, flag_column):
    ordered = (
        group.loc[:, ["DAY", flag_column]]
        .sort_values("DAY")
        .reset_index(drop=True)
    )

    if ordered.empty:
        return 0

    event = ordered[flag_column].fillna(False).astype(bool)
    follows_previous_day = (
        ordered["DAY"].diff().eq(pd.Timedelta(days=1))
    )
    previous_day_was_event = event.shift(fill_value=False)
    starts_new_sequence = (
        event
        & (
            ~previous_day_was_event
            | ~follows_previous_day
        )
    )

    sequence_id = starts_new_sequence.cumsum()
    sequence_lengths = event.groupby(sequence_id).sum()

    return int(sequence_lengths.max())


# Aggregates the configured daily event sequences to monthly maximum streak lengths.
def _aggregate_streaks_to_monthly(daily):
    missing_columns = [
        flag_column
        for flag_column in STREAK_FLAGS.values()
        if flag_column not in daily.columns
    ]
    if missing_columns:
        raise KeyError(
            "The following daily flag columns are missing: "
            + ", ".join(missing_columns)
        )

    rows = []

    for year_month, group in daily.groupby(
        "YEAR_MONTH",
        sort=True,
        observed=True,
    ):
        row = {"YEAR_MONTH": year_month}

        for output_column, flag_column in STREAK_FLAGS.items():
            row[output_column] = _longest_consecutive_event_days(
                group=group,
                flag_column=flag_column,
            )

        rows.append(row)

    return pd.DataFrame(
        rows,
        columns=[
            "YEAR_MONTH",
            *STREAK_FLAGS.keys(),
        ],
    )


# Computes monthly statistics directly from all cell-day observations.
def _aggregate_raw_to_monthly(df):
    monthly_raw = (
        df.groupby(
            "YEAR_MONTH",
            sort=True,
            observed=True,
        )
        .agg(
            OBSERVED_DAYS=("DAY", "nunique"),
            N_CELLS=("IDCELL", "nunique"),
            TEMPERATURE_AVG_MONTH=("TEMPERATURE_AVG", "mean"),
            TEMPERATURE_MAX_MONTH=("TEMPERATURE_MAX", "max"),
            TEMPERATURE_MIN_MONTH=("TEMPERATURE_MIN", "min"),
            PRECIPITATION_SUM_ALL_POINTS=("PRECIPITATION", "sum"),
            PRECIPITATION_DAILY_AVG=("PRECIPITATION", "mean"),
            PRECIPITATION_LOCAL_DAILY_MAX=("PRECIPITATION", "max"),
            WINDSPEED_AVG_MONTH=("WINDSPEED", "mean"),
            WINDSPEED_LOCAL_MAX=("WINDSPEED", "max"),
            VAPOURPRESSURE_AVG_MONTH=("VAPOURPRESSURE", "mean"),
            ET0_SUM_ALL_POINTS=("ET0", "sum"),
            ET0_DAILY_AVG=("ET0", "mean"),
            RADIATION_SUM_ALL_POINTS=("RADIATION", "sum"),
            RADIATION_DAILY_AVG=("RADIATION", "mean"),
        )
        .reset_index()
    )

    monthly_raw["PRECIPITATION_TOTAL_MONTH"] = (
        monthly_raw["PRECIPITATION_SUM_ALL_POINTS"]
        / monthly_raw["N_CELLS"]
    )
    monthly_raw["ET0_TOTAL_MONTH"] = (
        monthly_raw["ET0_SUM_ALL_POINTS"]
        / monthly_raw["N_CELLS"]
    )
    monthly_raw["RADIATION_TOTAL_MONTH"] = (
        monthly_raw["RADIATION_SUM_ALL_POINTS"]
        / monthly_raw["N_CELLS"]
    )

    monthly_raw = monthly_raw.drop(
        columns=[
            "PRECIPITATION_SUM_ALL_POINTS",
            "ET0_SUM_ALL_POINTS",
            "RADIATION_SUM_ALL_POINTS",
        ]
    )

    return monthly_raw


# Aggregates indicators whose meaning depends on the temporary daily provincial state.
def _aggregate_daily_features_to_monthly(daily):
    monthly_daily = (
        daily.groupby(
            "YEAR_MONTH",
            sort=True,
            observed=True,
        )
        .agg(
            OBSERVED_DAYS_DAILY=("DAY", "nunique"),
            N_CELLS_DAILY=("N_CELLS", "max"),
            TEMPERATURE_DAILY_STD=("TEMPERATURE_AVG_AREA", "std"),
            TEMPERATURE_SPATIAL_STD_AVG=("TEMPERATURE_SPATIAL_STD", "mean"),
            PRECIPITATION_AREA_DAILY_MAX=("PRECIPITATION_AREA", "max"),
            PRECIPITATION_SPATIAL_STD_AVG=("PRECIPITATION_SPATIAL_STD", "mean"),
            WET_DAYS_AREA_MEAN=("WET_DAY_AREA_MEAN", "sum"),
            WET_DAYS_SPATIAL=("WET_DAY_SPATIAL", "sum"),
            DRY_DAYS_AREA_MEAN=("DRY_DAY_AREA_MEAN", "sum"),
            DRY_DAYS_ALL_CELLS=("DRY_DAY_ALL_CELLS", "sum"),
            WET_AREA_FRACTION_AVG=("WET_CELL_AREA_FRACTION", "mean"),
            WET_AREA_FRACTION_MAX=("WET_CELL_AREA_FRACTION", "max"),
            WET_AREA_WHEN_PRESENT=("WET_CELL_AREA_FRACTION", _mean_when_positive),
            DAYS_RAIN_20=("RAIN_20_DAY", "sum"),
            DAYS_RAIN_50=("RAIN_50_DAY", "sum"),
            RAIN_20_AREA_FRACTION_MAX=("RAIN_20_AREA_FRACTION", "max"),
            RAIN_50_AREA_FRACTION_MAX=("RAIN_50_AREA_FRACTION", "max"),
            DAYS_EXTREME_RAIN=("EXTREME_RAIN_DAY", "sum"),
            DAYS_VERY_EXTREME_RAIN=("VERY_EXTREME_RAIN_DAY", "sum"),
            EXTREME_RAIN_AREA_FRACTION_AVG=("EXTREME_RAIN_AREA_FRACTION", "mean"),
            EXTREME_RAIN_AREA_FRACTION_MAX=("EXTREME_RAIN_AREA_FRACTION", "max"),
            EXTREME_RAIN_AREA_WHEN_PRESENT=("EXTREME_RAIN_AREA_FRACTION", _mean_when_positive),
            VERY_EXTREME_RAIN_AREA_FRACTION_MAX=("VERY_EXTREME_RAIN_AREA_FRACTION", "max"),
            DAYS_EXTREME_HEAT=("EXTREME_HEAT_DAY", "sum"),
            DAYS_VERY_EXTREME_HEAT=("VERY_EXTREME_HEAT_DAY", "sum"),
            EXTREME_HEAT_AREA_FRACTION_AVG=("EXTREME_HEAT_AREA_FRACTION", "mean"),
            EXTREME_HEAT_AREA_FRACTION_MAX=("EXTREME_HEAT_AREA_FRACTION", "max"),
            EXTREME_HEAT_AREA_WHEN_PRESENT=("EXTREME_HEAT_AREA_FRACTION", _mean_when_positive),
            DAYS_EXTREME_COLD=("EXTREME_COLD_DAY", "sum"),
            EXTREME_COLD_AREA_FRACTION_AVG=("EXTREME_COLD_AREA_FRACTION", "mean"),
            EXTREME_COLD_AREA_FRACTION_MAX=("EXTREME_COLD_AREA_FRACTION", "max"),
            EXTREME_COLD_AREA_WHEN_PRESENT=("EXTREME_COLD_AREA_FRACTION", _mean_when_positive),
            DAYS_EXTREME_WIND=("EXTREME_WIND_DAY", "sum"),
            EXTREME_WIND_AREA_FRACTION_AVG=("EXTREME_WIND_AREA_FRACTION", "mean"),
            EXTREME_WIND_AREA_FRACTION_MAX=("EXTREME_WIND_AREA_FRACTION", "max"),
            EXTREME_WIND_AREA_WHEN_PRESENT=("EXTREME_WIND_AREA_FRACTION", _mean_when_positive),
            DAYS_FROST_ANY_AREA=("FROST_AREA_FRACTION", lambda values: int((values > 0).sum())),
            DAYS_FROST_10PCT=("FROST_DAY_10PCT", "sum"),
            DAYS_HOT_30_ANY_AREA=("HOT_30_AREA_FRACTION", lambda values: int((values > 0).sum())),
            DAYS_HOT_30_10PCT=("HOT_30_DAY_10PCT", "sum"),
            DAYS_HOT_35_ANY_AREA=("HOT_35_AREA_FRACTION", lambda values: int((values > 0).sum())),
            DAYS_HOT_35_10PCT=("HOT_35_DAY_10PCT", "sum"),
        )
        .reset_index()
    )

    monthly_streaks = _aggregate_streaks_to_monthly(daily)

    return monthly_daily.merge(
        monthly_streaks,
        on="YEAR_MONTH",
        how="left",
        validate="one_to_one",
    )


# Aggregates static altitude values once per unique grid cell.
def _calculate_province_altitude_features(df):
    altitude_by_cell = (
        df.groupby("IDCELL", observed=True)["ALTITUDE"]
        .agg(
            altitude_values="nunique",
            altitude="first",
        )
    )

    inconsistent_cells = altitude_by_cell["altitude_values"] != 1
    if inconsistent_cells.any():
        problematic_cells = (
            altitude_by_cell.loc[inconsistent_cells]
            .index
            .tolist()
        )
        raise ValueError(
            "Some cells have inconsistent altitude values: "
            + ", ".join(map(str, problematic_cells))
        )

    altitude = altitude_by_cell["altitude"]

    return {
        "ALTITUDE_MEAN": altitude.mean(),
        "ALTITUDE_STD": altitude.std(),
        "ALTITUDE_MIN": altitude.min(),
        "ALTITUDE_MAX": altitude.max(),
        "ALTITUDE_RANGE": altitude.max() - altitude.min(),
    }


# Merges the raw monthly branch, daily monthly branch, and static altitude features.
def _build_monthly_dataset(df, daily, source_name):
    monthly_raw = _aggregate_raw_to_monthly(df)
    monthly_daily = _aggregate_daily_features_to_monthly(daily)

    monthly = monthly_raw.merge(
        monthly_daily,
        on="YEAR_MONTH",
        how="inner",
        validate="one_to_one",
    )

    if len(monthly) != len(monthly_raw) or len(monthly) != len(monthly_daily):
        raise ValueError(
            _error_message(
                "the two monthly aggregation branches do not contain the same months.",
                source_name,
            )
        )

    inconsistent_coverage = (
        (monthly["OBSERVED_DAYS"] != monthly["OBSERVED_DAYS_DAILY"])
        | (monthly["N_CELLS"] != monthly["N_CELLS_DAILY"])
    )
    if inconsistent_coverage.any():
        problematic_months = monthly.loc[
            inconsistent_coverage,
            [
                "YEAR_MONTH",
                "OBSERVED_DAYS",
                "OBSERVED_DAYS_DAILY",
                "N_CELLS",
                "N_CELLS_DAILY",
            ],
        ]
        raise ValueError(
            _error_message(
                "raw and daily aggregation branches have inconsistent coverage:\n"
                + problematic_months.to_string(index=False),
                source_name,
            )
        )

    monthly = monthly.drop(
        columns=[
            "OBSERVED_DAYS_DAILY",
            "N_CELLS_DAILY",
        ]
    )

    altitude_features = _calculate_province_altitude_features(df)
    monthly = monthly.assign(**altitude_features)

    return monthly


# Validates and transforms one already-loaded provincial dataframe into the final monthly dataset.
def transform_province_dataframe(df, source_name=None):
    prepared = _prepare_input_dataframe(
        df=df,
        source_name=source_name,
    )

    # Instead of raising an error if temperature values are mixed, they are switched to make sure
    # that temperature max is the highest and temperature min the lowest
    # This is done after having checked all datasets and reported the various errors
    # Afterwards there is anyway a control that raises an error in case for some weason this swap operation is not enough
    prepared = _reorder_temperature_columns(prepared)

    _validate_input_dataframe(
        df=prepared,
        source_name=source_name,
    )

    prepared = _add_calendar_columns(prepared)
    thresholds = _calculate_thresholds(
        df=prepared,
        source_name=source_name,
    )
    prepared = _add_cell_level_indicators(
        df=prepared,
        thresholds=thresholds,
    )

    area_weight = 1 / prepared["IDCELL"].nunique()
    daily = _aggregate_to_daily_province(
        df=prepared,
        area_weight=area_weight,
    )
    daily = _add_daily_province_flags(daily)

    return _build_monthly_dataset(
        df=prepared,
        daily=daily,
        source_name=source_name,
    )
