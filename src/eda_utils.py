# =============================================================================
# eda_utils.py

# It covers univariate, bivariate and tri-variate analysis for numeric,
# categorical and temporal variables, but it only produces descriptive
# statistics and charts: there is no hypothesis test.
#
# Every plotting function returns the figure and the axes, so the charts can be
# reused or composed into subplot grids. The functions also print/display a
# short descriptive summary while running, which is the point of interactive EDA.
#
# The visual identity is shared across all charts: the gold/teal palette, the
# seaborn white style, the top and right borders removed and the titles aligned
# to the left in bold.
# =============================================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

# display() is used to show the summary tables. Outside a notebook it is not
# defined, so it is replaced with print to avoid a crash.
try:
    from IPython.display import display
except ImportError:
    display = print


# =============================================================================
# STYLE AND PALETTE
# =============================================================================

# The project palette, made of gold, teal and a few neutral grays.
plot_palette = [
    "#D4A02A",  # gold
    "#4F7C7D",  # teal
    "#2E2E2E",  # dark
    "#7A7A7A",  # medium gray
    "#CFCFCF",  # light gray
    "#B8871A",  # dark gold
    "#3E6F70",  # dark teal
    "#A6A6A6",  # intermediate gray
    "#E0B84C",  # light gold
    "#595959"   # strong gray
]

# Semantic aliases for the most used colors, so the charts read by intention and
# not by palette index.
GOLD = plot_palette[0]
TEAL = plot_palette[1]
DARK = plot_palette[2]
GRAY_MED = plot_palette[3]
GRAY_LIGHT = plot_palette[4]

# Diverging colormap built from the palette: teal for the negative side, a light
# neutral in the middle and gold for the positive side. It is centered on zero,
# so it is the natural choice for correlation heatmaps and signed values.
diverging_cmap = LinearSegmentedColormap.from_list(
    "gold_teal_diverging",
    [TEAL, "#8FB0B0", "#F2F2F2", "#E8CE86", GOLD],
    N=256
)

# Sequential colormap (light to teal), for heatmaps where only the magnitude
# matters and there is no meaningful zero.
sequential_cmap = LinearSegmentedColormap.from_list(
    "teal_sequential",
    ["#F2F2F2", "#9FC0C0", TEAL, "#2E5556"],
    N=256
)

sns.set_style("white")


# This helper applies the shared visual identity to matplotlib global settings.
# It is called at the beginning of every plotting function so the style is
# consistent even if the user changed the defaults in the meantime.
def set_plot_style():
    sns.set_style("white")
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.spines.right"] = False
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 11
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["legend.frameon"] = False


# =============================================================================
# PRIVATE HELPERS
# =============================================================================

# This helper checks that all the requested columns exist in the dataframe and
# raises a clear error listing the missing ones, instead of failing later deep
# inside pandas or matplotlib with a cryptic message.
def _check_columns(data, columns):
    missing = [c for c in columns if c not in data.columns]
    if missing:
        raise ValueError("Columns not found in dataframe: " + str(missing))


# This helper decides whether a new figure has to be created or an existing axes
# passed by the caller has to be reused. It returns the figure, the axes and a
# flag (created) that tells if we own the figure. The flag is used to call
# tight_layout only when we created the figure, avoiding warnings when the chart
# is drawn inside an external subplot grid.
def _resolve_ax(ax, figsize):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
        return fig, ax, True
    return ax.figure, ax, False


# This helper removes the top and right borders to keep the shared minimal look.
def _clean_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return ax


# This helper returns n colors from the palette, repeating it when more colors
# than available are requested, so a chart with many categories never runs out.
def _get_palette(n_colors):
    if n_colors <= len(plot_palette):
        return plot_palette[:n_colors]
    reps = int(np.ceil(n_colors / len(plot_palette)))
    return (plot_palette * reps)[:n_colors]


# This helper turns a column name into a readable label (underscores to spaces,
# title case), used for titles and axis labels.
def _pretty(label):
    return str(label).replace("_", " ").strip().title()


# This helper places a left aligned bold title (and an optional subtitle) above
# the axes. It works in axes fraction coordinates so the alignment does not move
# when the tick labels get wider. It is the single place where the title style
# is defined, so all the single axis charts look the same.
def _left_title(ax, title, subtitle=None):
    if subtitle:
        ax.text(0.0, 1.10, title, transform=ax.transAxes, ha="left", va="bottom",
                fontsize=14, fontweight="bold", color=DARK)
        ax.text(0.0, 1.02, subtitle, transform=ax.transAxes, ha="left", va="bottom",
                fontsize=11, color=GRAY_MED)
    else:
        ax.text(0.0, 1.02, title, transform=ax.transAxes, ha="left", va="bottom",
                fontsize=14, fontweight="bold", color=DARK)
    return ax


# This helper is the equivalent of _left_title but for figures with more than one
# axes, where a single figure level title is needed.
def _figure_title(fig, title, subtitle=None):
    fig.suptitle(title, x=0.01, y=1.02, ha="left", fontweight="bold", fontsize=14)
    if subtitle:
        fig.text(0.01, 0.97, subtitle, ha="left", va="top", fontsize=11, color=GRAY_MED)
    return fig


# This helper prints a compact diagnostic of the missing values (and of the zero
# values, only for numeric columns, since a zero is often a hidden missing) and
# returns the same numbers as a dict for later use.
def _missing_report(data, col):
    n = len(data)
    n_missing = int(data[col].isna().sum())
    # Zeros are counted only for numeric columns, where they are meaningful.
    if pd.api.types.is_numeric_dtype(data[col]):
        n_zero = int((data[col] == 0).sum())
    else:
        n_zero = 0
    message = "'" + col + "': " + str(n_missing) + " missing (" + format(n_missing / n, ".1%") + ")"
    if n_zero:
        message += ", " + str(n_zero) + " zeros (" + format(n_zero / n, ".1%") + ")"
    print(message)
    return {"n": n, "n_missing": n_missing, "n_zero": n_zero}


# This helper builds the frequency table (absolute and relative) of a column,
# used both by the categorical and the discrete univariate functions.
def _frequency_table(data, col):
    # value_counts gives the absolute frequency; reset_index turns the values,
    # that were the index, into a proper column.
    table = data[col].value_counts(dropna=False).reset_index()
    table.columns = [_pretty(col), "abs_freq"]
    # The relative frequency is added as a percentage of the total rows.
    table["rel_freq_%"] = (table["abs_freq"] / len(data) * 100).round(2)
    return table


# This function classifies a series as temporal, discrete, continuous or
# categorical. It is used by describe_variable to send a column to the right
# univariate routine, so the caller does not need to know the dtype in advance.
def infer_variable_type(series, discrete_threshold=15):
    # A datetime column is temporal.
    if pd.api.types.is_datetime64_any_dtype(series):
        return "temporal"
    # A numeric column is either discrete or continuous.
    if pd.api.types.is_numeric_dtype(series):
        non_null = series.dropna()
        # The column is considered integer like when all its values equal their
        # rounded version.
        if len(non_null):
            is_integer_like = np.array_equal(non_null, non_null.round())
        else:
            is_integer_like = False
        # Few distinct integer values means the variable is better seen as
        # discrete (a count plot) rather than continuous (a histogram).
        if is_integer_like and series.nunique(dropna=True) <= discrete_threshold:
            return "discrete"
        return "continuous"
    # Everything else (object, category, bool) is treated as categorical.
    return "categorical"

# =============================================================================
# DATASET OVERVIEW
# =============================================================================

# This function builds a compact per-column diagnostic table: dtype, non-null
# count, number of unique values, and missing count (absolute and relative).
# It is meant to be the first call of an EDA session, before drilling into any
# single variable with describe_variable. Every count is computed with a
# vectorized pass over the dataframe, rather than column by column in Python.
def summarize_columns(data, sort_by=None, ascending=True):
    n = len(data)
    columns_summary = pd.DataFrame({
        "Column": data.columns,
        "Data Type": data.dtypes.astype(str).values,
        "Total Values": data.notna().sum().values,
        "Unique Values": data.nunique(dropna=True).values,
        "NaN Values": data.isna().sum().values,
    })
    columns_summary["NaN %"] = (columns_summary["NaN Values"] / n * 100).round(2)

    if sort_by:
        columns_summary = columns_summary.sort_values(sort_by, ascending=ascending)

    display(columns_summary)
    return columns_summary


# =============================================================================
# UNIVARIATE ANALYSIS
# =============================================================================

# This function describes a continuous variable. It prints the missing and zero
# counts, the skewness and the statistical summary, then it draws a histogram
# with the kernel density estimate on top of a boxplot sharing the x axis. When
# the distribution is strongly right skewed and strictly positive, both panels
# switch to a log scale automatically, so the shape stays readable.
def plot_numeric_distribution(data, col, bins=30, auto_log=True,
                              skew_threshold=4.0, figsize=(11, 6)):
    set_plot_style()
    _check_columns(data, [col])

    # First the missing/zero diagnostic, then the values coerced to numeric and
    # cleaned from the missing ones.
    _missing_report(data, col)
    values = pd.to_numeric(data[col], errors="coerce").dropna()
    if values.empty:
        raise ValueError("Column '" + col + "' has no valid numeric values.")

    # The skewness is a descriptive number: it says how asymmetric the
    # distribution is (0 is symmetric, positive means a long right tail). It also
    # drives the decision on the log scale.
    skew = float(values.skew())
    print("Skew: " + format(skew, ".3f"))
    display(values.describe().to_frame().T)

    # The log scale is used only when requested, when the skew is above the
    # threshold and when all the values are positive (log is undefined otherwise).
    # The result is cast to bool because the last condition returns a numpy
    # boolean, which seaborn reads as a log base and rejects.
    use_log = bool(auto_log and skew > skew_threshold and (values > 0).all())

    # The two panels share the x axis; the histogram is given more height than the
    # boxplot through the height ratios.
    fig, (ax_hist, ax_box) = plt.subplots(
        nrows=2, sharex=True, figsize=figsize,
        gridspec_kw={"height_ratios": [3, 1]}
    )
    sns.histplot(values, bins=bins, kde=True, ax=ax_hist,
                 color=TEAL, edgecolor="white", alpha=0.85, log_scale=use_log)
    ax_hist.set_ylabel("Frequency")
    ax_hist.set_xlabel("")
    ax_hist.grid(True, linestyle="--", linewidth=0.5, alpha=0.5)

    # The boxplot shows the mean as well, to give an idea of how far the mean is
    # from the median and therefore of the skew.
    sns.boxplot(x=values, ax=ax_box, showmeans=True,
                color=GOLD, fliersize=3, linewidth=1, log_scale=use_log)
    ax_box.set_xlabel(_pretty(col) + (" (log scale)" if use_log else ""))
    ax_box.grid(True, axis="x", linestyle="--", linewidth=0.5, alpha=0.5)

    for ax in (ax_hist, ax_box):
        _clean_axes(ax)
    _figure_title(fig, "Distribution of " + _pretty(col))
    fig.tight_layout()
    plt.show()
    #return fig, (ax_hist, ax_box)


# This function describes a discrete numeric variable. Beside the frequency
# table, it draws a count plot that spans every integer between the minimum and
# the maximum, so the values with no occurrences stay visible as gaps: this gives
# a better idea of the distribution and of possible outliers.
def plot_discrete_distribution(data, col, figsize=(11, 5), ax=None):
    set_plot_style()
    _check_columns(data, [col])
    _missing_report(data, col)

    # The table is sorted by value (not by frequency) because for a discrete
    # variable the natural order carries meaning.
    table = _frequency_table(data, col).sort_values(_pretty(col))
    display(table)

    fig, ax, created = _resolve_ax(ax, figsize)
    lo, hi = int(data[col].min()), int(data[col].max())
    # histplot with discrete=True is used instead of countplot because it lets us
    # force a bin for every integer in the range, including the empty ones.
    sns.histplot(data=data, x=col, discrete=True, shrink=0.85,
                 color=TEAL, edgecolor="white",
                 bins=np.arange(lo, hi + 1, 1), ax=ax)
    # The absolute frequency is written on top of each bar.
    if ax.containers:
        ax.bar_label(ax.containers[0], color=DARK, fontsize=9)
    # Only the integer ticks are shown on the x axis.
    ax.set_xticks(np.arange(lo, hi + 1, 1))
    ax.set_xlabel(_pretty(col))
    ax.set_ylabel("Count")
    _clean_axes(ax)
    _left_title(ax, "Value counts of " + _pretty(col))
    if created:
        fig.tight_layout()
    plt.show()
    #return fig, ax


# This function describes a categorical variable. It prints the frequency table
# and draws a count plot. The orientation is chosen automatically, horizontal
# above six categories for readability, unless it is forced through the
# horizontal argument. Only the most frequent max_categories are drawn.
def plot_categorical_distribution(data, col, max_categories=20, sort=True,
                                  horizontal=None, figsize=None, ax=None):
    set_plot_style()
    _check_columns(data, [col])
    _missing_report(data, col)

    # The table is computed on the non missing rows and optionally sorted by
    # frequency, then capped to the top categories.
    table = _frequency_table(data.dropna(subset=[col]), col)
    if sort:
        table = table.sort_values("abs_freq", ascending=False)
    table = table.head(max_categories)
    display(table)

    # The plotting order follows the table, so the bars and the table agree.
    order = table[_pretty(col)].astype(str).tolist()
    n_cat = len(order)
    # The orientation defaults to horizontal when there are many categories.
    if horizontal is None:
        horizontal = n_cat > 6
    # The figure size adapts to the number of categories when not given.
    if figsize is None:
        if horizontal:
            figsize = (10, max(4, 0.45 * n_cat + 1))
        else:
            figsize = (11, 5)

    fig, ax, created = _resolve_ax(ax, figsize)
    plot_data = data[data[col].notna()].astype({col: str})
    if horizontal:
        sns.countplot(data=plot_data, y=col, order=order, color=TEAL, ax=ax)
        ax.set_xlabel("Count")
        ax.set_ylabel(_pretty(col))
    else:
        sns.countplot(data=plot_data, x=col, order=order, color=TEAL, ax=ax)
        ax.set_ylabel("Count")
        ax.set_xlabel(_pretty(col))
        ax.tick_params(axis="x", rotation=45)
    if ax.containers:
        ax.bar_label(ax.containers[0], color=DARK, fontsize=9)
    _clean_axes(ax)
    _left_title(ax, "Distribution of " + _pretty(col))
    if created:
        fig.tight_layout()
    plt.show()
    #return fig, ax


# This function auto detects the type of a column and dispatches it to the right
# univariate routine, so a single call works on any column. Numeric integer like
# columns with few unique values are treated as discrete, other numerics as
# continuous, object and category as categorical. A datetime column is only
# summarized (range and number of timestamps) since a proper temporal view needs
# a value to aggregate and belongs to the temporal section.
def describe_variable(data, col, **kwargs):
    _check_columns(data, [col])
    kind = infer_variable_type(data[col])
    print("Detected type for '" + col + "': " + kind)
    if kind == "continuous":
        plot_numeric_distribution(data, col, **kwargs)
    if kind == "discrete":
        plot_discrete_distribution(data, col, **kwargs)
    if kind == "categorical":
        plot_categorical_distribution(data, col, **kwargs)
    # The remaining case is the temporal one.
    s = pd.to_datetime(data[col], errors="coerce").dropna()
    print("Range: " + str(s.min()) + " -> " + str(s.max())
          + "  |  " + str(s.nunique()) + " unique timestamps")


# =============================================================================
# BIVARIATE ANALYSIS
# =============================================================================

# This function shows the relationship between two numeric variables. It draws a
# scatterplot (optionally colored by a category) with a regression line, and it
# prints the correlation between the two variables. The correlation is a number
# between -1 and 1: close to 1 means they grow together, close to -1 means one
# grows while the other decreases, close to 0 means no linear relationship.
def numeric_vs_numeric(data, x_col, y_col, hue_col=None, reg_line=True,
                       figsize=(7, 6), ax=None):
    set_plot_style()
    cols = [x_col, y_col]
    if hue_col:
        cols.append(hue_col)
    _check_columns(data, cols)

    # The two numeric columns are coerced and the rows missing on either of them
    # are dropped, so the correlation and the plot use the same data.
    d = data[cols].copy()
    d[x_col] = pd.to_numeric(d[x_col], errors="coerce")
    d[y_col] = pd.to_numeric(d[y_col], errors="coerce")
    d = d.dropna(subset=[x_col, y_col])
    if d.empty:
        raise ValueError("No valid rows for the requested scatterplot.")

    correlation = d[x_col].corr(d[y_col])
    print("Correlation = " + format(correlation, ".4f") + "  (n = " + str(len(d)) + ")")

    fig, ax, created = _resolve_ax(ax, figsize)
    # With a hue the points are colored by category and a legend is placed
    # outside the plot; without a hue a single teal is used.
    if hue_col:
        sns.scatterplot(data=d, x=x_col, y=y_col, hue=hue_col,
                        palette=_get_palette(d[hue_col].nunique()),
                        alpha=0.7, edgecolor="white", linewidth=0.4, ax=ax)
        ax.legend(title=_pretty(hue_col), bbox_to_anchor=(1.02, 1), loc="upper left")
    else:
        sns.scatterplot(data=d, x=x_col, y=y_col, color=TEAL,
                        alpha=0.7, edgecolor="white", linewidth=0.4, ax=ax)
    # The regression line is drawn separately, without repeating the scatter, so
    # it works the same with or without a hue.
    if reg_line:
        sns.regplot(data=d, x=x_col, y=y_col, scatter=False,
                    line_kws={"color": GOLD, "linewidth": 2}, ax=ax)

    ax.set_xlabel(_pretty(x_col))
    ax.set_ylabel(_pretty(y_col))
    _clean_axes(ax)
    _left_title(ax, _pretty(y_col) + " vs " + _pretty(x_col))
    if created:
        fig.tight_layout()
    plt.show()
    #return fig, ax


# This function shows how a numeric variable behaves across the values of a
# categorical one. It prints the descriptive summary of the numeric column for
# each group (count, mean, quartiles, and so on) and draws a violin (or box)
# plot, with the groups ordered by median, so the differences between groups can
# be read directly from the chart.
def categorical_vs_numeric(data, cat_col, num_col, kind="violin",
                           max_categories=15, figsize=(8, 6), ax=None):
    set_plot_style()
    _check_columns(data, [cat_col, num_col])

    d = data[[cat_col, num_col]].copy()
    d[num_col] = pd.to_numeric(d[num_col], errors="coerce")
    d = d.dropna(subset=[cat_col, num_col])
    if d.empty:
        raise ValueError("No valid rows for the requested categorical/numeric analysis.")

    # Only the most frequent categories are kept, then the groups are ordered by
    # median so the plot reads from the highest to the lowest.
    top = d[cat_col].value_counts().head(max_categories).index
    d = d[d[cat_col].isin(top)]
    order = d.groupby(cat_col)[num_col].median().sort_values(ascending=False).index.tolist()

    # The summary of the numeric variable for each group.
    display(d.groupby(cat_col)[num_col].describe())

    fig, ax, created = _resolve_ax(ax, figsize)
    if kind == "violin":
        sns.violinplot(data=d, x=num_col, y=cat_col, order=order, color=TEAL,
                       inner="quart", linewidth=1, linecolor="white", ax=ax)
    else:
        # For the boxplot the color is mapped through hue (with the legend off)
        # to follow the current seaborn behaviour.
        sns.boxplot(data=d, x=num_col, y=cat_col, order=order, hue=cat_col,
                    hue_order=order, palette=_get_palette(len(order)),
                    legend=False, showmeans=True, ax=ax)
    ax.set_xlabel(_pretty(num_col))
    ax.set_ylabel(_pretty(cat_col))
    _clean_axes(ax)
    _left_title(ax, _pretty(num_col) + " by " + _pretty(cat_col))
    if created:
        fig.tight_layout()
    plt.show()
    #return fig, ax


# This function shows the relationship between two categorical variables. It
# prints the contingency table (how many rows fall in each combination of
# categories) and draws a 100% stacked bar that shows, inside each level of the
# first variable, the composition of the second one, so it is easy to see how the
# mix changes from one group to another.
def categorical_vs_categorical(data, col1, col2, normalize="index",
                               figsize=(8, 6), ax=None):
    set_plot_style()
    _check_columns(data, [col1, col2])

    d = data[[col1, col2]].dropna().astype(str)
    if d.empty:
        raise ValueError("No valid rows for the requested categorical/categorical analysis.")

    # The contingency table holds the counts for each combination of categories.
    contingency = pd.crosstab(d[col1], d[col2])
    display(contingency)

    # A second table holds the proportions instead of the counts (normalized by
    # row by default), which is what the stacked bar displays.
    proportions = pd.crosstab(d[col1], d[col2], normalize=normalize)

    fig, ax, created = _resolve_ax(ax, figsize)
    proportions.plot(kind="barh", stacked=True, ax=ax,
                     color=_get_palette(proportions.shape[1]), edgecolor="white")
    ax.set_xlabel("Proportion")
    ax.set_ylabel(_pretty(col1))
    ax.set_xlim(0, 1)
    ax.legend(title=_pretty(col2), bbox_to_anchor=(1.02, 1), loc="upper left")
    _clean_axes(ax)
    _left_title(ax, _pretty(col2) + " composition by " + _pretty(col1))
    if created:
        fig.tight_layout()
    plt.show()
    #return fig, ax


# =============================================================================
# TEMPORAL ANALYSIS
# =============================================================================

# This function plots one or more series against time. The x axis is the datetime
# column when date_col is given, otherwise the dataframe index. The normalize
# option min-max scales each series to the 0 to 1 range, so series with different
# units can be compared by shape, and hline draws a horizontal reference line.
def plot_time_series(data, columns, date_col=None, normalize=False,
                     hline=None, figsize=(11, 5), ax=None):
    set_plot_style()
    # A single column name is accepted as well as a list.
    if isinstance(columns, str):
        columns = [columns]
    cols_to_check = list(columns)
    if date_col:
        cols_to_check.append(date_col)
    _check_columns(data, cols_to_check)

    d = data.copy()
    # When a date column is given it is parsed, the unparseable rows are dropped
    # and the data is sorted in time; otherwise the index is used as it is.
    if date_col:
        d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
        d = d.dropna(subset=[date_col]).sort_values(date_col)
        x = d[date_col]
    else:
        x = d.index

    # The selected columns are coerced to numeric all at once.
    series = d[list(columns)].apply(pd.to_numeric, errors="coerce")
    if series.dropna(how="all").empty:
        raise ValueError("No valid numeric data for the requested time series.")
    if normalize:
        series = (series - series.min()) / (series.max() - series.min())

    fig, ax, created = _resolve_ax(ax, figsize)
    # Each series is drawn with its own color from the palette.
    for i, col in enumerate(columns):
        ax.plot(x, series[col], label=_pretty(col),
                color=plot_palette[i % len(plot_palette)], linewidth=2)
    # The optional threshold line.
    if hline is not None:
        ax.axhline(hline, linestyle="--", color=DARK, linewidth=1.2,
                   label="Threshold = " + str(hline))

    ax.set_xlabel(_pretty(date_col) if date_col else "Index")
    ax.set_ylabel("Normalized value" if normalize else "Value")
    # The legend is placed outside the plot on the right, so it never covers the
    # lines.
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)
    ax.tick_params(axis="x", rotation=45)
    _clean_axes(ax)
    _left_title(ax, "Time series: " + ", ".join(_pretty(c) for c in columns))
    if created:
        fig.tight_layout()
    plt.show()
    #return fig, ax


# This function draws a 100% stacked area of the row-wise composition of the
# columns over time. Each column is shown as its share of the row total, so the
# chart tells how the mix evolves rather than the absolute magnitudes. When no
# columns are given, all the numeric ones are used.
def plot_stacked_area_percent(data, columns=None, date_col=None,
                              figsize=(11, 5), ax=None):
    set_plot_style()
    # Default to all numeric columns when none are passed.
    if columns is None:
        columns = data.select_dtypes(include=[np.number]).columns.tolist()
    if isinstance(columns, str):
        columns = [columns]
    cols_to_check = list(columns)
    if date_col:
        cols_to_check.append(date_col)
    _check_columns(data, cols_to_check)

    d = data.copy()
    if date_col:
        d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
        d = d.dropna(subset=[date_col]).sort_values(date_col)
        x = d[date_col]
    else:
        x = d.index

    series = d[list(columns)].apply(pd.to_numeric, errors="coerce")
    # The share is the value divided by the row total; a zero total would give a
    # division by zero, so it is replaced with NaN and dropped afterwards.
    row_totals = series.sum(axis=1).replace(0, np.nan)
    shares = series.div(row_totals, axis=0)
    mask = shares.notna().any(axis=1)
    shares, x = shares[mask], x[mask]
    if shares.empty:
        raise ValueError("No valid data after computing row-wise shares.")

    fig, ax, created = _resolve_ax(ax, figsize)
    ax.stackplot(x, [shares[c] for c in columns],
                 labels=[_pretty(c) for c in columns],
                 colors=_get_palette(len(columns)))
    ax.set_xlabel(_pretty(date_col) if date_col else "Index")
    ax.set_ylabel("Share of total")
    ax.set_ylim(0, 1)
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    # For an area chart all the borders are removed, not only top and right.
    for spine in ax.spines.values():
        spine.set_visible(False)
    _left_title(ax, "Composition over time")
    if created:
        fig.tight_layout()
    plt.show()
    #return fig, ax


# This function draws a heatmap of a value aggregated over two calendar
# components. By default the rows are the months and the columns the years, which
# exposes at the same time the seasonal cycle (reading down a column) and the
# year over year drift (reading across a row). The row and col arguments accept
# year, month, quarter, weekday, day or hour.
def plot_seasonality_heatmap(data, date_col, value_col, agg="mean",
                             row="month", col="year", figsize=(11, 6), annot=True):
    set_plot_style()
    _check_columns(data, [date_col, value_col])

    d = data[[date_col, value_col]].copy()
    d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
    d[value_col] = pd.to_numeric(d[value_col], errors="coerce")
    d = d.dropna(subset=[date_col, value_col])
    if d.empty:
        raise ValueError("No valid datetime/value pairs for the heatmap.")

    # This inner helper extracts the requested calendar component from a datetime
    # series, keeping the mapping in a single place.
    def component(series, name):
        dt = series.dt
        mapping = {"year": dt.year, "month": dt.month, "quarter": dt.quarter,
                   "weekday": dt.dayofweek, "day": dt.day, "hour": dt.hour}
        return mapping[name]

    d["_row"] = component(d[date_col], row)
    d["_col"] = component(d[date_col], col)
    # The pivot table aggregates the value on the two components.
    pivot = d.pivot_table(index="_row", columns="_col", values=value_col, aggfunc=agg)

    # When a component is the month, its numbers are replaced with the short
    # names, keeping the calendar order.
    if row == "month":
        pivot.index = [pd.Timestamp(2000, m, 1).strftime("%b") for m in pivot.index]
    if col == "month":
        pivot.columns = [pd.Timestamp(2000, m, 1).strftime("%b") for m in pivot.columns]

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(pivot, cmap=sequential_cmap, annot=annot, fmt=".1f",
                linewidths=0.5, linecolor="white",
                cbar_kws={"shrink": 0.8, "label": agg + " of " + _pretty(value_col)}, ax=ax)
    ax.set_xlabel(_pretty(col))
    ax.set_ylabel(_pretty(row))
    _left_title(ax, _pretty(value_col) + ": " + row + " x " + col + " seasonality")
    fig.tight_layout()
    plt.show()
    #return fig, ax


# =============================================================================
# MULTIVARIATE ANALYSIS
# =============================================================================

# This function draws a correlation heatmap across the numeric columns, using the
# branded diverging colormap centered on zero. The method can be pearson,
# spearman or kendall. By default the upper triangle is masked, since the matrix
# is symmetric and the two halves would repeat the same information. The
# correlation matrix is a descriptive summary, not a test: each cell is just the
# correlation between two columns.
def plot_correlation_heatmap(data, method="pearson", columns=None,
                             mask_upper=True, annot=True, figsize=(10, 8)):
    set_plot_style()
    # Either the given columns or all the numeric ones are used.
    if columns:
        numeric = data[list(columns)]
    else:
        numeric = data.select_dtypes(include=[np.number])
    numeric = numeric.dropna(axis=1, how="all")
    if numeric.shape[1] < 2:
        raise ValueError("At least two numeric columns are required.")

    corr = numeric.corr(method=method)
    # The mask hides the upper triangle (above the diagonal) when requested.
    if mask_upper:
        mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    else:
        mask = None

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(corr, mask=mask, annot=annot, fmt=".2f", cmap=diverging_cmap,
                center=0, vmin=-1, vmax=1, linewidths=0.5, linecolor="white",
                square=True, cbar_kws={"shrink": 0.8}, ax=ax)
    _left_title(ax, "Correlation heatmap (" + method + ")")
    fig.tight_layout()
    plt.show()
    #return fig, ax


# This function draws a faceted scatter of x versus y split by a category, with a
# regression line in each facet. It also prints the overall correlation and the
# correlation computed inside each group: when these numbers disagree, it means
# the relationship between x and y is not the same across the groups, so the
# category is worth keeping in mind. No test is performed, only the correlation
# values are reported.
def numeric_vs_numeric_by_category(data, x_col, y_col, cat_col,
                                   col_wrap=3, height=3.0):
    set_plot_style()
    _check_columns(data, [x_col, y_col, cat_col])

    d = data[[x_col, y_col, cat_col]].copy()
    d[x_col] = pd.to_numeric(d[x_col], errors="coerce")
    d[y_col] = pd.to_numeric(d[y_col], errors="coerce")
    d = d.dropna(subset=[x_col, y_col, cat_col])
    if d.empty:
        raise ValueError("No valid rows for the requested tri-variate analysis.")

    # One scatter with a regression line is drawn for each value of the category.
    g = sns.FacetGrid(d, col=cat_col, col_wrap=col_wrap, height=height, aspect=1.1)
    g.map_dataframe(sns.regplot, x=x_col, y=y_col,
                    scatter_kws={"s": 20, "alpha": 0.6, "color": TEAL},
                    line_kws={"color": GOLD, "linewidth": 1.4})
    g.set_titles(col_template="{col_name}", size=10, fontweight="bold")
    g.set_axis_labels(_pretty(x_col), _pretty(y_col))
    g.figure.suptitle(
        _pretty(y_col) + " vs " + _pretty(x_col) + " by " + _pretty(cat_col),
        x=0.01,
        y=1.02,
        ha="left",
        va="bottom",
        fontweight="bold",
        fontsize=14
        )

    # Leave more space between the main title and the facet titles.
    g.figure.subplots_adjust(top=0.84)

    # The overall correlation first, then the correlation inside each group: if
    # they disagree, the category is changing the relationship.
    correlation = d[x_col].corr(d[y_col])
    print("Overall correlation = " + format(correlation, ".4f"))
    for label, sub in d.groupby(cat_col):
        # A correlation needs at least a few points to be meaningful.
        if len(sub) > 2:
            r = sub[x_col].corr(sub[y_col])
            print("  " + str(label) + ": correlation = " + format(r, ".4f")
                  + " (n = " + str(len(sub)) + ")")
    plt.show()
    #return g
