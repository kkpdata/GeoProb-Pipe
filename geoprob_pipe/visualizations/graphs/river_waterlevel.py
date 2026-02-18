from __future__ import annotations
import os
import numpy as np
from pandas import DataFrame, concat, Series
from geopandas import GeoDataFrame
import plotly.colors as pc
from plotly.graph_objects import Figure, Scatter
from typing import TYPE_CHECKING, Dict, List, Tuple
from geoprob_pipe.cmd_app.parameter_input.expand_input_tables import run_expand_input_tables
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


TARGET_FREQS = np.array([
        0.1, 0.033333333, 0.01, 0.003333333, 0.001, 0.000333333, 0.0001, 3.33333E-05, 0.00001, 3.33333E-06])


def _collect_data(geoprob_pipe: GeoProbPipe) -> Tuple[DataFrame, GeoDataFrame, DataFrame, DataFrame]:

    # Collect uittredepunten
    gdf_uittredepunten = geoprob_pipe.input_data.uittredepunten.gdf

    # Collect physical values
    df = geoprob_pipe.results.df_alphas_influence_factors_and_physical_values(
        system_only=True, filter_deterministic=False, filter_derived=False)
    df = df[["uittredepunt_id", "ondergrondscenario_id", "vak_id", "variable", "distribution_type", "physical_value"]]
    df = df.merge(gdf_uittredepunten[["uittredepunt_id", "metrering", "hrd_name"]], on="uittredepunt_id", how="left")

    # Collect Beta results uittredepunten
    df_beta = geoprob_pipe.results.df_beta_uittredepunten

    # Collect hydra curves (from expansion to uittredepunt-level)
    df_input: DataFrame = run_expand_input_tables(
        geoprob_pipe.input_data.app_settings.geopackage_filepath, add_frag_ref=True)
    df_input = df_input[df_input["parameter_name"] == "buitenwaterstand"]
    df_input = concat(
        objs=[df_input.drop(columns=['parameter_input']),   # Removal of parameter_input column
              df_input['parameter_input'].apply(Series)], # Expansion of dict in parameter_input-column
        axis=1)

    return df, gdf_uittredepunten, df_beta, df_input


def _collect_hydra_curves(
        df: DataFrame, gdf_uittredepunten: GeoDataFrame) -> Dict[float, Dict[str, List[float]]]:
    hydra_curves = {freq: {"metrering": [], "level": []} for freq in TARGET_FREQS}

    for _, row in df.iterrows():
        if row["distribution_type"] != "deterministic":
            df_subset = gdf_uittredepunten[gdf_uittredepunten["vak_id"] == row["vak_id"]]
            if df_subset.empty:
                continue
            m_values = df_subset["metrering"].to_numpy()

            # Hydra exceedance curve
            freqs = np.array([fv.probability_of_failure for fv in row.loc["fragility_values"]], dtype=float)
            levels = np.array([fv.x for fv in row.loc["fragility_values"]], dtype=float)

            # Sort for interpolation
            sort_idx = np.argsort(freqs)
            freqs = freqs[sort_idx]
            levels = levels[sort_idx]

            # Interpolate levels for standard frequencies
            interp_levels = np.interp(TARGET_FREQS, freqs, levels)

            # Store values for each frequency
            for freq, level in zip(TARGET_FREQS, interp_levels):
                hydra_curves[freq]["metrering"].extend(m_values)
                hydra_curves[freq]["level"].extend(np.full_like(m_values, level))

    return hydra_curves


def _plot_continuous_exceedance_lines(
        fig: Figure, hydra_curves: Dict[float, Dict[str, List[float]]]):

    # Blue gradient for lines
    line_colors = pc.sample_colorscale(
        colorscale="Jet", samplepoints=np.linspace(start=0.2, stop=0.9, num=len(TARGET_FREQS)))
    freq_color_map = {f: c for f, c in zip(TARGET_FREQS, line_colors)}

    for freq, data in hydra_curves.items():
        # Sort by metrering for continuous line plotting
        sort_idx = np.argsort(data["metrering"])
        m_sorted = np.array(data["metrering"])[sort_idx]
        level_sorted = np.array(data["level"])[sort_idx]
        fig.add_trace(
            Scatter(
                x=m_sorted, y=level_sorted, mode="lines", line=dict(color=freq_color_map[freq], width=2),
                name=f"1/{1/freq:,.0f}".replace(",", "."),  # mark thousands
                showlegend=True))

    return fig


def _plot_physical_values(fig: Figure, df: DataFrame) -> Figure:
    beta_colorscale = "RdYlGn" # Green-to-red scale (low beta = red, high beta = green)
    betas = df["beta"].to_numpy()
    fig.add_trace(
        Scatter(
            x=df["metrering"], y=df["physical_value"],
            mode="markers", name="Physical values", showlegend=True,
            marker=dict(
                symbol="circle", size=7, color=betas, colorscale=beta_colorscale, cmin=1, cmax=10,
                line=dict(width=0.5, color="black"),
                colorbar=dict(
                    title="β", xanchor="right", ticks="outside",
                    x=-0.05,  # Make space on the left side for y-axis
                )),
            customdata=df[["beta"]],
            hovertemplate=("metering: %{x}<br>" +
                           "buitenwaterstand: %{y:.2f}<br>" +
                           "beta: %{customdata:.3f}")))

    return fig


def _update_layout(fig: Figure) -> Figure:
    fig.update_layout(
        title="Buitenwaterstanden bij herhaaltijd en physical values uit system design points",
        xaxis=dict(title="Metrering [m]", showgrid=True, gridwidth=0.5, gridcolor="gray"),
        yaxis=dict(title="Buitenwaterstand [m+NAP]", showgrid=True, gridwidth=0.5, gridcolor="gray"),
        legend=dict(
            orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, title="Legenda",
            bgcolor="rgba(255,255,255,0.7)"),
        legend_traceorder="reversed", height=600, margin=dict(r=200))
    return fig


def river_waterlevel(geoprob_pipe: GeoProbPipe, export: bool = False):

    # Prepare base data
    df, gdf_uittredepunten, df_beta, df_input = _collect_data(geoprob_pipe=geoprob_pipe)

    # Collect Hydra lines (grouped per frequency)
    hydra_curves: Dict[float, Dict[str, List[float]]] = _collect_hydra_curves(
        df=df_input, gdf_uittredepunten=gdf_uittredepunten)

    # Plot one continuous line per exceedance frequency
    fig = Figure()
    fig = _plot_continuous_exceedance_lines(fig=fig, hydra_curves=hydra_curves)

    # Buitenwaterstand markers with β color scale
    df_filtered = df[df["variable"] == "buitenwaterstand"]
    df_filtered = df_filtered.merge(df_beta[["uittredepunt_id", "beta"]], on="uittredepunt_id", how="left")
    fig = _plot_physical_values(fig=fig, df=df_filtered)

    # Layout
    fig = _update_layout(fig=fig)

    # Export
    if export:
        export_dir = os.path.join(geoprob_pipe.visualizations.graphs.export_dir, "grafiek_physical_values")
        os.makedirs(export_dir, exist_ok=True)
        fig.write_html(os.path.join(export_dir, "river_waterlevel.html"), include_plotlyjs='cdn')

    return fig
