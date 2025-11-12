from __future__ import annotations
from typing import TYPE_CHECKING
from plotly.graph_objects import Figure, Scatter
import os
from pandas import merge
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def physical_values_buitenwaterstand_and_top_zand(geoprob_pipe: GeoProbPipe, export: bool = False) -> Figure:

    # Get data for graphing
    df = geoprob_pipe.results.df_alphas_influence_factors_and_physical_values(
        system_only=True, filter_deterministic=False, filter_derived=True)
    df = df[["uittredepunt_id", "ondergrondscenario_id", "vak_id", "variable", "distribution_type", "physical_value"]]

    # Attach measure
    gdf_uittredepunten = geoprob_pipe.input_data.uittredepunten.gdf
    df = merge(
        left=df,
        right=gdf_uittredepunten[["uittredepunt_id", "metrering"]],
        on="uittredepunt_id",
        how="left")

    fig = Figure()

    df_filtered = df[df['variable'] == "buitenwaterstand"]
    fig.add_trace(
        Scatter(
            x=df_filtered['metrering'],
            y=df_filtered["physical_value"],
            name="Buitenwaterstand",
            mode='markers',
            marker=dict(symbol='circle', size=5, color='blue')))
    df_filtered = df[df['variable'] == "top_zand"]
    fig.add_trace(
        Scatter(
            x=df_filtered['metrering'],
            y=df_filtered["physical_value"],
            mode='markers',
            name="Top zand",
            marker=dict(symbol='circle', size=5, color='brown')))

    fig.update_layout(
        xaxis=dict(
            title=f"Metrering", type='linear', range=[df['metrering'].min()-10, df['metrering'].max()+10],
            showgrid=True, gridwidth=0.5, gridcolor="gray"),
        yaxis=dict(
            title=f"Buitenwaterstand en top zand [m+NAP]", showgrid=True, gridwidth=0.5, gridcolor="gray",
            minor=dict(showgrid=True, dtick=1))
    )

    if export:
        export_dir = geoprob_pipe.visualizations.graphs.export_dir
        os.makedirs(export_dir, exist_ok=True)
        fig.write_html(
            os.path.join(export_dir, f"physical_values_buitenwaterstand_and_top_zand.html"),
            include_plotlyjs='cdn')
        if geoprob_pipe.software_requirements.chrome_is_installed:
            fig.write_image(
                os.path.join(export_dir, f"physical_values_buitenwaterstand_and_top_zand.png"), format="png")

    return fig
