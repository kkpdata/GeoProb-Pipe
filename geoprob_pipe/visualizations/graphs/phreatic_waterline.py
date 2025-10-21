from __future__ import annotations
from typing import TYPE_CHECKING
from plotly.graph_objects import Figure, Scatter
from pandas import merge
import os
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def phreatic_waterline(geoprob_pipe: GeoProbPipe, export: bool = False):

    # Get data for graphing
    df = geoprob_pipe.results.df_alphas_influence_factors_and_physical_values(
        system_only=True, filter_deterministic=False, filter_derived=False)
    df = df[["uittredepunt_id", "ondergrondscenario_id", "vak_id",
             "variable", "distribution_type", "physical_value"]]

    # Attach measure
    df_uittredepunten = geoprob_pipe.input_data.uittredepunten.df
    df = merge(
        left=df,
        right=df_uittredepunten[["uittredepunt_id", "M_value"]],
        on="uittredepunt_id",
        how="left")

    fig = Figure()

    # Add scatterplots for the selected variables
    df_filtered = df[df['variable'] == "buitenwaterstand"]
    fig.add_trace(
        Scatter(
            x=df_filtered['M_value'],
            y=df_filtered["physical_value"],
            name="Buitenwaterstand",
            mode='markers',
            marker=dict(symbol='square', size=5, color='blue')))

    df_filtered = df[df['variable'] == "phi_exit"]
    fig.add_trace(
        Scatter(
            x=df_filtered['M_value'],
            y=df_filtered["physical_value"],
            mode='markers',
            name="Stijghoogte",
            marker=dict(symbol='x', size=5, color='blue')))

    df_filtered = df[df['variable'] == "h_exit"]
    fig.add_trace(
        Scatter(
            x=df_filtered['M_value'],
            y=df_filtered["physical_value"],
            mode='markers',
            name="Hoogte uitredepunt",  # Of iets anders
            marker=dict(symbol='circle', size=5, color='black')))

    df_filtered = df[df['variable'] == "top_zand"]
    fig.add_trace(
        Scatter(
            x=df_filtered['M_value'],
            y=df_filtered["physical_value"],
            mode='markers',
            name="Top zand",
            marker=dict(symbol='square', size=5, color='brown')))

    fig.update_layout(
        xaxis=dict(
            title="Metrering",
            type='linear',
            range=[df['M_value'].min()-10,
                   df['M_value'].max()+10],
            showgrid=True,
            gridwidth=0.5, gridcolor="gray"),
        yaxis=dict(
            title="Hoogte [m+NAP]",
            showgrid=True, gridwidth=0.5, gridcolor="gray",
            minor=dict(showgrid=True, dtick=1))
    )
    
    if export:
        export_dir = os.path.join(
            geoprob_pipe.visualizations.graphs.export_dir,
            "grafiek_physical_values"
            )
        os.makedirs(export_dir, exist_ok=True)
        fig.write_html(
            os.path.join(export_dir, "phreatic_waterline.html"),
            include_plotlyjs='cdn')
        if geoprob_pipe.software_requirements.chrome_is_installed:
            fig.write_image(
                os.path.join(export_dir, "phreatic_waterline.png"),
                format="png"
                )

    return fig
