from __future__ import annotations
import os
import numpy as np
import pandas as pd
import plotly.colors as pc
from plotly.graph_objects import Figure, Scatter
from typing import TYPE_CHECKING

from geoprob_pipe.questionnaire.parameter_input.expand_input_tables import run_expand_input_tables

if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def river_waterlevel(geoprob_pipe: GeoProbPipe, export: bool = False):
    # Prepare base data
    df = geoprob_pipe.results.df_alphas_influence_factors_and_physical_values(
        system_only=True, filter_deterministic=False, filter_derived=False
    )

    df = df[[
        "uittredepunt_id", "ondergrondscenario_id", "vak_id",
        "variable", "distribution_type", "physical_value"
    ]]

    gdf_uittredepunten = geoprob_pipe.input_data.uittredepunten.gdf
    df = df.merge(
        gdf_uittredepunten[["uittredepunt_id", "metrering", "hrd_name"]],
        on="uittredepunt_id", how="left"
    )
    df_beta = geoprob_pipe.results.df_beta_uittredepunten

    # Target exceedance frequencies
    target_freqs = np.array([
        0.1, 0.033333333, 0.01, 0.003333333,
        0.001, 0.000333333, 0.0001, 3.33333E-05,
        0.00001, 3.33333E-06
    ])

    # Blue gradient for lines
    line_colors = pc.sample_colorscale(
        "Blues", np.linspace(0.2, 0.9, len(target_freqs))
        )
    freq_color_map = {f: c for f, c in zip(target_freqs, line_colors)}

    # Figure
    fig = Figure()

    # Prepare storage for Hydra curves per frequency
    hydra_curves = {freq: {"metrering": [], "level": []}
                    for freq in target_freqs}

    # Add Hydra lines (grouped per frequency)
    df_input: pd.DataFrame = run_expand_input_tables(
        geoprob_pipe.input_data.app_settings.geopackage_filepath,
        add_frag_ref=True
        )
    df_input = df_input[df_input["parameter_name"] == "buitenwaterstand"]
    df_input = pd.concat([df_input.drop(columns=['parameter_input']),
                          df_input['parameter_input'].apply(pd.Series)],
                         axis=1)

    for _, row in df_input.iterrows():
        df_subset = gdf_uittredepunten[
            gdf_uittredepunten["vak_id"] == row["vak_id"]
            ]
        if df_subset.empty:
            continue

        m_values = df_subset["metrering"].to_numpy()

        # Hydra exceedance curve
        freqs = np.array(
            [fv.probability_of_failure for fv in row.loc["fragility_values"]],
            dtype=float
            )
        levels = np.array(
            [fv.x for fv in row.loc["fragility_values"]],
            dtype=float
            )

        # Sort for interpolation
        sort_idx = np.argsort(freqs)
        freqs = freqs[sort_idx]
        levels = levels[sort_idx]

        # Interpolate levels for standard frequencies
        interp_levels = np.interp(target_freqs, freqs, levels)

        # Store values for each frequency
        for freq, level in zip(target_freqs, interp_levels):
            hydra_curves[freq]["metrering"].extend(m_values)
            hydra_curves[freq]["level"].extend(np.full_like(m_values, level))

    # Plot one continuous line per exceedance frequency
    for freq, data in hydra_curves.items():
        # Sort by metrering for continuous line plotting
        sort_idx = np.argsort(data["metrering"])
        m_sorted = np.array(data["metrering"])[sort_idx]
        level_sorted = np.array(data["level"])[sort_idx]

        fig.add_trace(
            Scatter(
                x=m_sorted,
                y=level_sorted,
                mode="lines",
                line=dict(color=freq_color_map[freq], width=2),
                name=f"1/{1/freq:,.0f}".replace(",", "."),  # mark thousands
                showlegend=True,
            )
        )

    # Buitenwaterstand markers with β color scale
    df_filtered = df[df["variable"] == "buitenwaterstand"].merge(
        df_beta[["uittredepunt_id", "beta"]],
        on="uittredepunt_id", how="left"
    )

    betas = df_filtered["beta"].to_numpy()

    # Green-to-red scale (low beta = red, high beta = green)
    beta_colorscale = "RdYlGn"
    fig.add_trace(
        Scatter(
            x=df_filtered["metrering"],
            y=df_filtered["physical_value"],
            mode="markers",
            name="Buitenwaterstand",
            marker=dict(
                symbol="circle",
                size=7,
                color=betas,
                colorscale=beta_colorscale,
                cmin=1,
                cmax=10,
                colorbar=dict(
                    title="β",
                    xanchor="right",
                    x=-0.05,  # Make space on the left side for y-axis
                    ticks="outside",
                ),
                line=dict(width=0.5, color="black"),
            ),
            showlegend=True
        )
    )

    # Layout
    fig.update_layout(
        title="Buitenwaterstanden bij herhaaltijd en system design points",
        xaxis=dict(title="Metrering", showgrid=True,
                   gridwidth=0.5, gridcolor="gray"),
        yaxis=dict(title="Hoogte [m+NAP]", showgrid=True,
                   gridwidth=0.5, gridcolor="gray"),
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            title="Overschrijdingsfrequentie",
            bgcolor="rgba(255,255,255,0.7)"
        ),
        height=600,
        margin=dict(r=200),
    )

    # Export
    if export:
        export_dir = os.path.join(
            geoprob_pipe.visualizations.graphs.export_dir,
            "grafiek_physical_values"
        )
        os.makedirs(export_dir, exist_ok=True)

        fig.write_html(os.path.join(export_dir, "river_waterlevel.html"),
                       include_plotlyjs='cdn')
        fig.write_image(os.path.join(export_dir, "river_waterlevel.png"),
                        format="png", scale=5, width=1400, height=800)

    return fig
