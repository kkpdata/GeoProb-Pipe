from __future__ import annotations
from typing import TYPE_CHECKING
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from pandas import merge
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def overview_alpha(geoprob_pipe: GeoProbPipe, export: bool = False):
    # Get data for graphing
    df = geoprob_pipe.results.df_alphas_influence_factors_and_physical_values(
        system_only=False, filter_deterministic=False, filter_derived=False)
    df = df[["uittredepunt_id", "ondergrondscenario_id", "vak_id",
             "variable", "distribution_type", "physical_value"]]

    # Attach measure
    df_uittredepunten = geoprob_pipe.input_data.uittredepunten.df
    df = merge(
        left=df,
        right=df_uittredepunten[["uittredepunt_id", "M_value"]],
        on="uittredepunt_id",
        how="left")

    parameters = ["D_wvp",
                  "L_kwelweg",
                  "L_voorland",
                  "W_voorland",
                  "buitenwaterstand",
                  "c_achterland",
                  "c_voorland",
                  "d70",
                  "d_deklaag",
                  "dh_c",
                  "dh_red",
                  "dphi_c_u",
                  "gamma_sat_deklaag",
                  "h_exit",
                  "i_c_h",
                  "i_exit",
                  "kD_wvp",
                  "lambda_voorland",
                  "lengte_voorland",
                  "modelfactor_h",
                  "modelfactor_p",
                  "modelfactor_u",
                  "phi_exit",
                  "r_exit",
                  "top_zand",
                  "z_h",
                  "z_p",
                  "z_u"
                  ]

    fig = make_subplots(rows=len(parameters), cols=1,
                        shared_xaxes=False,
                        subplot_titles=parameters)

    for i, inp in enumerate(parameters):
        data = df[df["variable"] == f"{inp}"]
        fig.add_trace(
            go.Scatter(
                x=data['M_value'],
                y=data['physical_value'],
                mode='markers',
                marker=dict(color='black',
                            symbol='x', size=5),
                name=inp
            ),
            row=i+1, col=1
        )
        fig.update_xaxes(showgrid=True, tickangle=90, row=i+1, col=1)
        fig.update_yaxes(showgrid=True, title_text=inp, row=i+1, col=1)

    fig.update_layout(
        height=300*len(parameters),
        showlegend=False,
        title_text="Overview of parameters",
    )
    if export:
        export_dir = os.path.join(
            geoprob_pipe.visualizations.graphs.export_dir,
            "grafiek_physical_values"
            )
        os.makedirs(export_dir, exist_ok=True)
        fig.write_html(
            os.path.join(export_dir, "overview_alphas.html"),
            include_plotlyjs='cdn')
        if geoprob_pipe.software_requirements.chrome_is_installed:
            fig.write_image(
                os.path.join(export_dir, "overview_alpha.png"),
                format="png"
                )
    return fig
