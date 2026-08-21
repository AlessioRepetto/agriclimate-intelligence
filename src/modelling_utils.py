# =============================================================================
# modelling_utils.py
#
# Reusable utilities for quantile-regression modelling, temporal validation,
# feature selection, CatBoost fitting, post-processing and national-level
# visualisation in the AgriClimate Intelligence project.
#
# Plotting reuses the visual identity defined centrally in eda_utils.py.
# =============================================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from catboost import CatBoostRegressor

from sklearn.feature_selection import SequentialFeatureSelector
from sklearn.linear_model import QuantileRegressor
from sklearn.metrics import make_scorer, mean_pinball_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from eda_utils import set_plot_style, GOLD, TEAL, TEAL_LIGHT, DARK, GRAY_MED


__all__ = [
    "pinball",
    "make_linear_pipeline",
    "rolling_history_median",
    "temporal_cv_indices",
    "temporal_cv_scores",
    "evaluate_feature_set",
    "fit_sfs",
    "selected_feature_table",
    "native_feature_names",
    "make_regularized_linear_pipeline",
    "q2_l1_cv_scores",
    "select_l1_alpha",
    "evaluate_regularized_feature_set",
    "make_catboost_q2_model",
    "fit_catboost_q2",
    "correction_function",
    "add_quantile_limits",
    "aggregate_national_predictions",
    "plot_national_quantile_forecast",
]


# =============================================================================
# CORE QUANTILE MODELLING
# =============================================================================

# Return the pinball loss associated with one conditional quantile.
def pinball(y_true, y_pred, quantile):
    return mean_pinball_loss(
        y_true,
        y_pred,
        alpha=quantile,
    )


# Build the unregularized linear quantile model used throughout the notebook.
# Scaling remains inside the pipeline so it is refitted inside every temporal
# fold together with the model.
def make_linear_pipeline(quantile):
    return Pipeline([
        ("scaler", StandardScaler()),
        ("model", QuantileRegressor(
            quantile=quantile,
            alpha=0.0,
            solver="highs",
        )),
    ])


# Compute a rolling historical median using only yields observed in previous
# calendar years for the requested grouping columns.
def rolling_history_median(frame, group_columns, years=5):
    observed = frame.loc[frame["yield"].notna()]

    lookup = (
        observed
        .groupby(group_columns + ["harvest_year"])["yield"]
        .apply(list)
        .to_dict()
    )

    medians = []

    for row in frame[group_columns + ["harvest_year"]].itertuples(
        index=False,
        name=None,
    ):
        group_key = row[:-1]
        harvest_year = row[-1]

        values = []
        for lag in range(1, years + 1):
            values.extend(
                lookup.get(
                    group_key + (harvest_year - lag,),
                    [],
                )
            )

        medians.append(
            np.median(values) if values else np.nan
        )

    return pd.Series(
        medians,
        index=frame.index,
    )


# Convert year-based temporal folds into positional indices, which is the format
# expected by sklearn's SequentialFeatureSelector.
def temporal_cv_indices(frame, cv_folds):
    years = frame["harvest_year"].reset_index(drop=True)
    splits = []

    for _, validation_start, validation_end in cv_folds:
        train_idx = np.flatnonzero(
            (years < validation_start).to_numpy()
        )
        validation_idx = np.flatnonzero(
            years.between(
                validation_start,
                validation_end,
            ).to_numpy()
        )

        splits.append(
            (train_idx, validation_idx)
        )

    return splits


# Evaluate a feature set fold by fold for every requested quantile.
def temporal_cv_scores(frame, features, quantiles, cv_folds):
    rows = []

    for fold_name, validation_start, validation_end in cv_folds:
        train = frame[
            frame["harvest_year"] < validation_start
        ]

        validation = frame[
            frame["harvest_year"].between(
                validation_start,
                validation_end,
            )
        ]

        for quantile_name, quantile in quantiles.items():
            model = make_linear_pipeline(quantile)

            model.fit(
                train[features],
                train["yield"],
            )

            prediction = model.predict(
                validation[features]
            )

            rows.append({
                "fold": fold_name,
                "quantile": quantile_name,
                "pinball": pinball(
                    validation["yield"],
                    prediction,
                    quantile,
                ),
            })

    return pd.DataFrame(rows)


# Summarize one feature set with its in-sample loss on the complete development
# period and its mean loss across the temporal CV folds.
def evaluate_feature_set(frame, features, quantiles, cv_folds):
    row = {}

    for quantile_name, quantile in quantiles.items():
        model = make_linear_pipeline(quantile)

        model.fit(
            frame[features],
            frame["yield"],
        )

        train_prediction = model.predict(
            frame[features]
        )

        row[f"Train {quantile_name}"] = pinball(
            frame["yield"],
            train_prediction,
            quantile,
        )

    cv = (
        temporal_cv_scores(
            frame,
            features,
            quantiles,
            cv_folds,
        )
        .groupby("quantile")["pinball"]
        .mean()
    )

    for quantile_name in quantiles:
        row[f"CV {quantile_name}"] = cv[quantile_name]

    return row


# Run forward Sequential Feature Selection using Q2 and temporal folds.
def fit_sfs(
    frame,
    candidate_features,
    q2_quantile,
    tolerance,
    cv_folds,
):
    scorer = make_scorer(
        mean_pinball_loss,
        alpha=q2_quantile,
        greater_is_better=False,
    )

    X = frame[candidate_features].reset_index(drop=True)
    y = frame["yield"].reset_index(drop=True)

    selector = SequentialFeatureSelector(
        estimator=make_linear_pipeline(q2_quantile),
        n_features_to_select="auto",
        tol=tolerance,
        direction="forward",
        scoring=scorer,
        cv=temporal_cv_indices(frame, cv_folds),
        n_jobs=-1,
    )

    selector.fit(X, y)

    selected_features = (
        X.columns[selector.get_support()]
        .tolist()
    )

    return selector, selected_features


# Build a readable table for a selected feature set, distinguishing historical
# predictors from climate variables and extracting the crop-phase suffix.
def selected_feature_table(selected_features, historical_features):
    rows = []

    for feature in selected_features:
        source = (
            "historical"
            if feature in historical_features
            else "climate"
        )

        phase = None
        if "__" in feature:
            phase = feature.split("__", 1)[1]

        rows.append({
            "feature": feature,
            "source": source,
            "phase": phase,
        })

    return pd.DataFrame(rows)


# Replace feature names through a mapping, used when a model can consume the
# native missing values instead of the zero-filled linear-model versions.
def native_feature_names(features, feature_map):
    return [
        feature_map.get(feature, feature)
        for feature in features
    ]


# =============================================================================
# L1-REGULARIZED LINEAR QUANTILE MODELS
# =============================================================================

# Build a standardized linear quantile model with L1 regularization.
def make_regularized_linear_pipeline(quantile, alpha):
    return Pipeline([
        ("scaler", StandardScaler()),
        ("model", QuantileRegressor(
            quantile=quantile,
            alpha=alpha,
            solver="highs",
        )),
    ])


# Return fold-level Q2 losses for one crop, feature set and alpha value.
def q2_l1_cv_scores(frame, features, alpha, q2_quantile, cv_folds):
    losses = []

    for fold_name, validation_start, validation_end in cv_folds:
        train = frame[
            frame["harvest_year"] < validation_start
        ]

        validation = frame[
            frame["harvest_year"].between(
                validation_start,
                validation_end,
            )
        ]

        model = make_regularized_linear_pipeline(
            q2_quantile,
            alpha,
        )

        model.fit(
            train[features],
            train["yield"],
        )

        prediction = model.predict(
            validation[features]
        )

        losses.append({
            "fold": fold_name,
            "pinball": pinball(
                validation["yield"],
                prediction,
                q2_quantile,
            ),
        })

    return pd.DataFrame(losses)


# Select the strongest alpha whose Q2 loss is effectively tied for best.
def select_l1_alpha(search_rows, tolerance):
    best_loss = search_rows["CV Q2"].min()

    eligible = search_rows[
        search_rows["CV Q2"]
        <= best_loss + tolerance
    ]

    return (
        eligible
        .sort_values("alpha", ascending=False)
        .iloc[0]
    )


# Evaluate one regularized feature set on train and temporal CV.
def evaluate_regularized_feature_set(
    frame,
    features,
    alpha,
    quantiles,
    cv_folds,
):
    row = {}

    for quantile_name, quantile in quantiles.items():
        model = make_regularized_linear_pipeline(
            quantile,
            alpha,
        )

        model.fit(
            frame[features],
            frame["yield"],
        )

        train_prediction = model.predict(
            frame[features]
        )

        row[f"Train {quantile_name}"] = pinball(
            frame["yield"],
            train_prediction,
            quantile,
        )

        fold_losses = []

        for _, validation_start, validation_end in cv_folds:
            train = frame[
                frame["harvest_year"] < validation_start
            ]

            validation = frame[
                frame["harvest_year"].between(
                    validation_start,
                    validation_end,
                )
            ]

            fold_model = make_regularized_linear_pipeline(
                quantile,
                alpha,
            )

            fold_model.fit(
                train[features],
                train["yield"],
            )

            prediction = fold_model.predict(
                validation[features]
            )

            fold_losses.append(
                pinball(
                    validation["yield"],
                    prediction,
                    quantile,
                )
            )

        row[f"CV {quantile_name}"] = np.mean(fold_losses)

    return row


# =============================================================================
# CATBOOST Q2
# =============================================================================

# Build the basic CatBoost Q2 quantile model. Keeping this in one place makes it
# easy to reuse the same specification with and without early stopping.
def make_catboost_q2_model(iterations=None):
    params = {
        "loss_function": "Quantile:alpha=0.5",
        "random_seed": 0,
        "verbose": False,
        "allow_writing_files": False,
    }

    if iterations is not None:
        params["iterations"] = iterations

    return CatBoostRegressor(**params)


# Use the most recent training years only to select the stopping iteration, then
# refit on the complete training window so no available training year is lost.
def fit_catboost_q2(
    train,
    features,
    early_stopping_years,
    early_stopping_rounds,
):
    eval_start = (
        train["harvest_year"].max()
        - early_stopping_years
        + 1
    )
    is_eval = train["harvest_year"] >= eval_start

    stopping_model = make_catboost_q2_model()
    stopping_model.fit(
        train.loc[~is_eval, features],
        train.loc[~is_eval, "yield"],
        eval_set=(
            train.loc[is_eval, features],
            train.loc[is_eval, "yield"],
        ),
        early_stopping_rounds=early_stopping_rounds,
    )

    best_iteration = stopping_model.get_best_iteration()
    best_iterations = (
        best_iteration + 1
        if best_iteration >= 0
        else stopping_model.tree_count_
    )

    model = make_catboost_q2_model(
        iterations=best_iterations
    )
    model.fit(
        train[features],
        train["yield"],
    )

    return model, best_iterations


# =============================================================================
# QUANTILE POST-PROCESSING AND NATIONAL AGGREGATION
# =============================================================================

# This function enforces the expected order between two consecutive quantiles.
# If the higher quantile falls below (or equals) the lower one, it is replaced
# by the lower quantile.
def correction_function(low, high):
    if high <= low:
        return low
    return high


# This function applies the sequential Q1 <= Q2 <= Q3 correction and derives
# the predicted interquartile range and Tukey-style outlier boundaries.
def add_quantile_limits(data, q1_col="q25", q2_col="q50", q3_col="q75"):
    required = [q1_col, q2_col, q3_col]
    missing = [column for column in required if column not in data.columns]
    if missing:
        raise ValueError("Columns not found in dataframe: " + str(missing))

    result = data.copy()

    result["q50_corrected"] = [
        correction_function(low, high)
        for low, high in zip(result[q1_col], result[q2_col])
    ]
    result["q75_corrected"] = [
        correction_function(low, high)
        for low, high in zip(result["q50_corrected"], result[q3_col])
    ]

    result["predicted_iqr"] = result["q75_corrected"] - result[q1_col]
    result["low_limit"] = (
        result[q1_col] - 1.5 * result["predicted_iqr"]
    ).clip(lower=0.0)
    result["high_limit"] = (
        result["q75_corrected"] + 1.5 * result["predicted_iqr"]
    )

    return result


# This function converts province-level yield estimates into production,
# aggregates the productions nationally by crop and year, and only then derives
# the corresponding national yields from total production / total area.
def aggregate_national_predictions(
    data,
    crop_col="crop",
    year_col="harvest_year",
    area_col="area",
    production_col="production",
):
    required = [
        crop_col,
        year_col,
        area_col,
        production_col,
        "q25",
        "q50_corrected",
        "q75_corrected",
        "low_limit",
        "high_limit",
    ]
    missing = [column for column in required if column not in data.columns]
    if missing:
        raise ValueError("Columns not found in dataframe: " + str(missing))

    if data[required].isna().any().any():
        raise ValueError("National aggregation requires complete area, production and prediction columns.")
    if (data[area_col] <= 0).any():
        raise ValueError("Cultivated area must be strictly positive for national yield aggregation.")

    province = data.copy()

    yield_to_production = {
        "q25": "production_q1",
        "q50_corrected": "production_q2",
        "q75_corrected": "production_q3",
        "low_limit": "production_low_limit",
        "high_limit": "production_high_limit",
    }

    for yield_column, estimated_production_column in yield_to_production.items():
        province[estimated_production_column] = (
            province[area_col] * province[yield_column]
        )

    production_columns = list(yield_to_production.values())

    national = (
        province.groupby([crop_col, year_col], as_index=False)[
            [area_col, production_col] + production_columns
        ]
        .sum()
        .sort_values([crop_col, year_col])
        .reset_index(drop=True)
    )

    national["yield_real"] = national[production_col] / national[area_col]
    national["yield_q1"] = national["production_q1"] / national[area_col]
    national["yield_q2"] = national["production_q2"] / national[area_col]
    national["yield_q3"] = national["production_q3"] / national[area_col]
    national["yield_low_limit"] = national["production_low_limit"] / national[area_col]
    national["yield_high_limit"] = national["production_high_limit"] / national[area_col]

    national["low_outlier"] = national["yield_real"] < national["yield_low_limit"]
    national["high_outlier"] = national["yield_real"] > national["yield_high_limit"]

    return province, national


# This function draws the national observed yield, corrected quantile forecast,
# interquartile band and outlier boundaries for one crop.
def plot_national_quantile_forecast(
    data,
    crop,
    crop_col="crop",
    year_col="harvest_year",
    figsize=(16, 8),
):
    required = [
        crop_col,
        year_col,
        "yield_real",
        "yield_q1",
        "yield_q2",
        "yield_q3",
        "yield_low_limit",
        "yield_high_limit",
        "low_outlier",
        "high_outlier",
    ]
    missing = [column for column in required if column not in data.columns]
    if missing:
        raise ValueError("Columns not found in dataframe: " + str(missing))

    plot_data = data[data[crop_col] == crop].sort_values(year_col).copy()
    if plot_data.empty:
        raise ValueError("No rows found for crop: " + str(crop))

    set_plot_style()
    fig, ax = plt.subplots(figsize=figsize)

    low_outliers = plot_data["low_outlier"]
    high_outliers = plot_data["high_outlier"]

    ax.scatter(
        plot_data.loc[low_outliers, year_col],
        plot_data.loc[low_outliers, "yield_real"],
        color=GOLD,
        label="Low outlier",
        zorder=5,
        marker="v",
        s=120,
    )
    ax.scatter(
        plot_data.loc[high_outliers, year_col],
        plot_data.loc[high_outliers, "yield_real"],
        color=GOLD,
        label="High outlier",
        zorder=5,
        marker="^",
        s=120,
    )

    ax.plot(
        plot_data[year_col],
        plot_data["yield_q2"],
        label="50th percentile (median)",
        linestyle="--",
        color=TEAL,
        linewidth=1.4,
        marker="x",
    )
    ax.fill_between(
        plot_data[year_col],
        plot_data["yield_q1"],
        plot_data["yield_q3"],
        color=TEAL_LIGHT,
        alpha=0.25,
        label="Interquartile range",
    )

    ax.plot(
        plot_data[year_col],
        plot_data["yield_low_limit"],
        label="Low outlier limit",
        linestyle=":",
        color=GOLD,
        linewidth=1.1,
    )
    ax.plot(
        plot_data[year_col],
        plot_data["yield_high_limit"],
        label="High outlier limit",
        linestyle=":",
        color=GOLD,
        linewidth=1.1,
    )

    ax.plot(
        plot_data[year_col],
        plot_data["yield_real"],
        label="Observed national yield",
        color=DARK,
        linewidth=1.8,
        marker="o",
    )

    start_year = int(plot_data[year_col].min())
    end_year = int(plot_data[year_col].max())

    ax.set_title(
        f"{crop} - National yield: {start_year} → {end_year}",
        loc="left",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xlabel("Harvest year")
    ax.set_ylabel("Yield")
    ax.tick_params(axis="x", colors=GRAY_MED)
    ax.tick_params(axis="y", colors=GRAY_MED)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False)

    fig.tight_layout(pad=2)
    plt.show()
    return fig, ax
