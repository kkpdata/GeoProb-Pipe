from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from scipy.stats import gumbel_r

from app.classes.waterlevel_statistics import WaterlevelStatistics


def _get_new_color(ax: Axes) -> tuple:
    """Obtain the plot colors that are already used and make sure to select a new, distinct color for the current plot

    Args:
        ax (Axes): axes used for the plot
        start_colors (int, optional): start number of distinct colors. Defaults to 1.
        max_colors (int, optional): max. number of distinct colors. Defaults to 1000.

    Raises:
        ValueError: raised if no new, distinct color could be found (occurs if too many lines are plotted)

    Returns:
        _type_: _description_
    """

    # Get the colors used by existing lines
    used_colors = [line.get_color() for line in ax.get_lines()]

    # Get the colormap
    list_cmap = ["tab10", "Set2"]

    for cmap_name in list_cmap:
        cmap = plt.get_cmap(cmap_name)

        # Iterate over the colors in the colormap
        for i in range(cmap.N):
            color = cmap(i)
            if color not in used_colors:
                return color

    raise ValueError(
        "Too many fragility curves, no new colors for the plot could be assigned. Add more cmap options to choose from."
    )


# FIXME fix layout
# FIXME percentages of pie plots don't seem to match those shown in pie chart in PTK GUI
def _plot_influence_factors(df_influence_factors: pd.DataFrame):

    # More concise way to get unique water levels
    waterlevels = df_influence_factors.index.levels[0]

    # Create a figure with subplots (one for each unique waterlevel)
    fig, axes = plt.subplots(1, len(waterlevels), figsize=(len(waterlevels) * 5, 5))

    # Ensure axes is iterable even if only one subplot
    if len(waterlevels) == 1:
        axes = [axes]

    # Colors for pie chart
    colors = plt.cm.tab20.colors

    for i, waterlevel in enumerate(waterlevels):

        # Get the data for each waterlevel
        subset = df_influence_factors.loc[waterlevel] ** 2

        # Plot pie chart
        wedges, texts, autotexts = axes[i].pie(
            subset["influence_factor"], labels=None, autopct="%1.1f%%", startangle=90, colors=colors[: len(subset)]
        )

        # Title for each pie chart
        axes[i].set_title(f"Waterlevel: {waterlevel}")

    # Add a single legend outside the plot
    fig.legend(wedges, subset.index, title="Variables", loc="center right", bbox_to_anchor=(1.2, 0.5))

    plt.tight_layout()
    plt.subplots_adjust(right=0.85)  # Make room for the legend
    plt.show()


# FIXME docstring updaten
def _plot_fragility_curve(
    waterlevels: pd.Series,
    betas: pd.Series,
    show: bool = True,
    ax: Optional[Axes] = None,
    color: Optional[str | tuple] = None,
    label: Optional[str] = "Fragility Points",
) -> Axes | None:
    """Plots a fragility curve based on given water levels and reliability indices (betas).

    Args:
        waterlevels (pd.Series): waterlevels for which betas were calculated
        betas (pd.Series): beta values corresponding to the abovementioned waterlevels
        show (bool, optional): whether to show the plot or not. If show=False, the function returns the ax of the plot (can be used to plot multiple fragility curves in one figure). Defaults to True.
        ax (Optional[Axes], optional): previously generated ax to add the new fragility curve plot to. Defaults to None.
        label (Optional[str], optional): graph label. Defaults to None.

    Returns:
        Axes | None: returns None if the plot is shown (so show=True), else returns Axes-object which can be used later on in the script (e.g. to add more data)
    """

    if ax is None:
        # If no axis was given as input argument, generate a new axis
        fig, ax = plt.subplots()

    if color is None:
        # If no color was given as input argument, generate a new distinct color
        color = _get_new_color(ax)

    ax.plot(
        waterlevels,
        betas,
        label=f"{label}",
        color=color,
        marker="o",
        linestyle="-",
    )

    ax.set_xlabel("Waterlevel, h [m+NAP]")
    ax.set_ylabel(r"Reliability index, $\beta$")
    ax.set_title("Fragility curve")
    ax.grid()
    plt.legend()

    if show:
        plt.show()
    else:
        return ax


#  FIXME docstring updaten
def _plot_multiple_fragility_curves(dict_fragility_curve_data: dict, show: Optional[bool] = True) -> None:
    """_summary_

    Args:
        dict_fragility_curve_data (dict): dict with format {fragility curve name: dataframe with waterlevels and betas}
        show (Optional[bool], optional): If True, displays the plot. Defaults to True.
    """

    # Create a new figure and axes
    fig, ax = plt.subplots()

    # Loop through the fragility curves
    for name, df_overview in dict_fragility_curve_data.items():
        ax = _plot_fragility_curve(df_overview["waterlevel"], df_overview["beta"], show=False, ax=ax, label=name)

    if show:
        plt.show()


# FIXME add missing data docstring
def plot_waterlevel_statistics(
    waterlevels: pd.Series,
    betas: pd.Series,
    df_inter_extrapolated: pd.DataFrame,
    waterlevel_statistics: WaterlevelStatistics,
    ax_beta: Optional[Axes] = None,
) -> None:
    """Plot the fragility curve with the waterlevel statistics (histogram of waterlevel occurrences and
    a fitted probability density function (PDF)).

    Args:
        df_results (pd.DataFrame): DataFrame from which the waterlevel and corresponding beta (reliability index) values from the PTK calculations are obtained.
        df_inter_extrapolated (pd.DataFrame): _description_
        waterlevel_statistics (WaterlevelStatistics): contains mu (mean, location parameter) and sigma (standard deviation, scale parameter) of the Gumbel distribution that described the waterlevel statistics.
        ax_beta (Axes, optional): axis to plot fragility curve on, only necessary if you want to plot multiple fragility curves on the same axis. If not, the axis is generated in the plot function. Defaults to None.
    """

    if ax_beta is None:
        # If no axis was given as input argument, generate a new one axis
        fig, ax_beta = plt.subplots()

    # Create histogram of waterlevel to which the PDF is a fit
    histogram = gumbel_r.rvs(loc=waterlevel_statistics.mu, scale=waterlevel_statistics.sigma, size=1000)

    # Axis of beta plot
    ax_beta.plot(waterlevels, betas, label="Fragility Points", color="b", marker="o", linestyle=None)
    ax_beta.plot(
        df_inter_extrapolated["new_waterlevel"],
        df_inter_extrapolated["new_beta"],
        label="Extrapolated Fragility Curve",
        color=_get_new_color(ax_beta),
        marker="+",
        linestyle="--",
    )
    ax_beta.set_xlabel("Waterlevel, h [m+NAP]")
    ax_beta.set_ylabel(r"Reliability index, $\beta$")
    ax_beta.set_title("Fragility curve & waterlevel statistics")
    ax_beta.grid()

    # Axis of water statistics PDF plot
    ax_pdf = ax_beta.twinx()
    ax_pdf.plot(  # type: ignore
        df_inter_extrapolated["new_waterlevel"],
        df_inter_extrapolated["fh_pdf_waterlevel"],
        "r-",
        lw=5,
        alpha=0.6,
        label="PDF waterlevel statistics $f_h$",
    )

    # FIXME: the bins are "auto" defined, but most likely should be the same size as the bins used in determining the waterlevel statistics (mu/sigma)
    ax_pdf.hist(  # type: ignore
        histogram,
        density=True,
        bins="auto",
        histtype="stepfilled",
        alpha=0.5,
        label="PDF histogram waterlevel statistics $f_h$",
    )
    ax_pdf.set_ylabel("PDF waterlevel statistics $f_h$")
    ax_pdf.grid()

    # Combine the handles and labels from both axes
    lines_1, labels_1 = ax_beta.get_legend_handles_labels()
    lines_2, labels_2 = ax_pdf.get_legend_handles_labels()  # type: ignore

    # Create a single legend
    ax_pdf.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2)  # type: ignore

    plt.show()
