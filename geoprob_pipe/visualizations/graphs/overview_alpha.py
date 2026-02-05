from __future__ import annotations
import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pandas import merge
from geoprob_pipe.calculations.systems.mappers.initial_input_mapper import INITIAL_INPUT_MAPPER
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def overview_alpha(geoprob_pipe: GeoProbPipe, export: bool = False):
    # Get data for graphing
    df = geoprob_pipe.results.df_alphas_influence_factors_and_physical_values(
        system_only=True, filter_deterministic=False, filter_derived=False
    )
    df = df[["uittredepunt_id", "ondergrondscenario_id", "vak_id",
             "variable", "distribution_type", "physical_value"]]

    gdf_uittredepunten = geoprob_pipe.input_data.uittredepunten.gdf
    df = merge(df, gdf_uittredepunten[["uittredepunt_id", "metrering"]],
               on="uittredepunt_id", how="left")

    # Determine scenario order per uittredepunt_id
    df["scenario_order"] = (
        df.groupby("uittredepunt_id")["ondergrondscenario_id"]
        .transform(lambda x: pd.factorize(x)[0] + 1)
    )
    scenario_orders = sorted(df["scenario_order"].unique())

    # List of all alphas that can be shown
    parameters: list[str] = list(df["variable"].unique())
    # Add distribution type
    dist_types = {}
    for param in parameters:
        dist_type = df.loc[
            df["variable"] == param, "distribution_type"].unique()[0]
        dist_types.update({param: dist_type})
    # Add units
    unit_lookup = {item["name"]: item["unit"] for item in INITIAL_INPUT_MAPPER}
    param_units = {}
    for param in parameters:
        try:
            param_units.update({param: str(unit_lookup[param]).strip("[]")})
        except KeyError:
            param_units.update({param: "?"})

    # Add parameter units missing in DUMMY_INPUT by hand.
    param_units.update({
        "L_kwelweg": "m",
        "L_voorland": "m",
        "W_voorland": "s/m",
        "buitenwaterstand_gemiddeld": "m+NAP",
        "d_deklaag": "m",
        "dh_c": "m",
        "dh_red": "m",
        "dphi_c_u": "m+NAP",
        "h_exit": "m+NAP",
        "i_exit": "-",
        "k_wvp": "m/dag",
        "lambda_voorland": "m",
        "phi_exit": "m+NAP",
        "phi_exit_gemiddeld": "m+NAP",
        "r_exit": "-",
        "z_combin": "-",
        "z_h": "-",
        "z_p": "-",
        "z_u": "-"
    })

    # Create subplots
    fig = make_subplots(
        rows=len(parameters),
        cols=1,
        shared_xaxes=False,
        subplot_titles=parameters
    )

    # Add a button for each ondergrondscenario
    buttons = []

    # Add scatter plot per scenario
    for i, scen_order in enumerate(scenario_orders):
        df_case = df[df["scenario_order"] == scen_order]

        for row_idx, param in enumerate(parameters, start=1):
            df_param = df_case[df_case["variable"] == param]
            fig.add_trace(
                go.Scatter(
                    x=df_param["metrering"],
                    y=df_param["physical_value"],
                    mode="markers",
                    marker=dict(color="black", symbol="x", size=5),
                    name=param,
                    visible=(i == 0)
                ),
                row=row_idx, col=1
            )
            fig.update_xaxes(showgrid=True, tickangle=90,
                             row=row_idx, col=1)
            fig.update_yaxes(showgrid=True,
                             title_text=f"{param} [{param_units[param]}]"
                             + f"<br>({dist_types[param]})",
                             row=row_idx, col=1)

        total_traces = len(scenario_orders) * len(parameters)

        # Determine which scenario is visible
        vis = [False] * total_traces
        vis[i*len(parameters):(i+1)*len(parameters)] = [True] * len(parameters)

        buttons.append(dict(
            label=f"Scenario {scen_order}",
            method="update",
            args=[
                {"visible": vis},
                {"title": f"Overview of parameters for Scenario {scen_order}"}
            ]
        ))

    # Layout and button
    fig.update_layout(
        height=300*len(parameters),
        showlegend=False,
        title=f"Overview of parameters for Scenario {scenario_orders[0]}",
        updatemenus=[dict(
            active=0,
            buttons=buttons,
            direction="down",
            showactive=True,
            x=1.05, y=1.01
        )],
    )

    # Export
    if export:
        export_dir = os.path.join(
            geoprob_pipe.visualizations.graphs.export_dir,
            "grafiek_physical_values"
        )
        os.makedirs(export_dir, exist_ok=True)

        fig.write_html(
            os.path.join(export_dir, "overview_alphas.html"),
            include_plotlyjs='cdn'
        )

        for scen_order in scenario_orders:
            df_case = df[df["scenario_order"] == scen_order]
            fig_case = make_subplots(
                rows=len(parameters), cols=1,
                shared_xaxes=False,
                subplot_titles=parameters
            )
            for row_idx, param in enumerate(parameters, start=1):
                df_param = df_case[df_case["variable"] == param]
                fig_case.add_trace(
                    go.Scatter(
                        x=df_param["metrering"],
                        y=df_param["physical_value"],
                        mode="markers",
                        marker=dict(color="black", symbol="x", size=5),
                        name=param
                    ),
                    row=row_idx, col=1
                )
                fig_case.update_xaxes(showgrid=True, tickangle=90,
                                      row=row_idx, col=1)
                fig_case.update_yaxes(showgrid=True,
                                      title_text=f"{param} [{param_units[param]}]"
                                      + f"<br>({dist_types[param]})",
                                      row=row_idx, col=1)

            fig_case.update_layout(
                height=300*len(parameters),
                showlegend=False,
                title=f"Overview of parameters for Scenario {scen_order}"
            )

    return fig
