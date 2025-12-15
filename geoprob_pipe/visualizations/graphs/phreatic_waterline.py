from __future__ import annotations
import os
import plotly.graph_objects as go
import pandas as pd
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def phreatic_waterline(geoprob_pipe: GeoProbPipe, export: bool = False):
    # Prepare data
    df = geoprob_pipe.results.df_alphas_influence_factors_and_physical_values(
        system_only=True, filter_deterministic=False, filter_derived=False
    )
    df = df[["uittredepunt_id", "ondergrondscenario_id", "vak_id",
             "variable", "distribution_type", "physical_value"]]

    gdf_uittredepunten = geoprob_pipe.input_data.uittredepunten.gdf
    df = df.merge(
        gdf_uittredepunten[["uittredepunt_id", "metrering"]],
        on="uittredepunt_id", how="left"
    )

    # Determine scenario rank per uittredepunt_id
    # Assign "scenario_order" = 1, 2, 3, ... based on encounter order
    df["scenario_order"] = (
        df.groupby("uittredepunt_id")["ondergrondscenario_id"]
        .transform(lambda x: pd.factorize(x)[0] + 1)
    )

    scenario_orders = sorted(df["scenario_order"].unique())

    # Plotly setup
    fig = go.Figure()
    buttons = []

    colors = {
        "buitenwaterstand": "blue",
        "phi_exit": "green",
        "h_exit": "black",
        "top_zand": "brown"
    }
    symbols = {
        "buitenwaterstand": "square",
        "phi_exit": "x",
        "h_exit": "circle",
        "top_zand": "square"
    }
    names = {
        "buitenwaterstand": "Buitenwaterstand",
        "phi_exit": "Stijghoogte uittredepunt (phi_exit)",
        "h_exit": "Gehanteerde hoogte uittredepunt (h_exit)",
        "top_zand": "Bovenkant watervoerend pakket (top_zand)"
    }

    # Build one frame per scenario order
    for i, scen_order in enumerate(scenario_orders):
        df_case: pd.DataFrame = df[df["scenario_order"] == scen_order]

        # Add 4 variable traces per scenario_order
        for variable in ["buitenwaterstand", "phi_exit", "h_exit", "top_zand"]:
            df_var = df_case[df_case["variable"] == variable]
            dist_type = (str(df_var["distribution_type"].unique())
                         .strip("[]").strip("'"))
            fig.add_trace(go.Scatter(
                x=df_var['metrering'],
                y=df_var["physical_value"],
                mode='markers',
                name=f"{names[variable]} ({dist_type})",
                marker=dict(
                    symbol=symbols[variable],
                    size=5,
                    color=colors[variable]
                ),
                visible=(i == 0)
            ))

        # Button logic
        # Disappearance of title is a plotly bug
        total_traces = len(scenario_orders) * 4
        vis = [False] * total_traces
        vis[i*4:(i+1)*4] = [True]*4

        buttons.append(dict(
            label=f"Scenario {scen_order}",
            method="update",
            args=[
                {"visible": vis},
                {"title": f"Physical values t.o.v. NAP voor scenario {scen_order}"
                 + "<br><sup>Punten zijn per uittredepunt</sup>"}
            ]
        ))

    # Layout and controls
    fig.update_layout(
        title=f"Physical values t.o.v. NAP voor scenario {scenario_orders[0]}"
        + "<br><sup>Punten zijn per uittredepunt</sup>",
        updatemenus=[dict(
            active=0,
            buttons=buttons,
            direction="down",
            showactive=True,
            x=1.05, y=1.15
        )],
        xaxis=dict(
            title="Metrering",
            showgrid=True, gridwidth=0.5, gridcolor="gray",
        ),
        yaxis=dict(
            title="Hoogte [m+NAP]",
            showgrid=True, gridwidth=0.5, gridcolor="gray",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        height=600,
    )

    # Exports
    if export:
        export_dir = os.path.join(
            geoprob_pipe.visualizations.graphs.export_dir,
            "grafiek_physical_values"
        )
        os.makedirs(export_dir, exist_ok=True)

        # Export interactive HTML
        fig.write_html(
            os.path.join(export_dir, "phreatic_waterline.html"), include_plotlyjs='cdn')

        # Export one PNG per scenario_order
        if geoprob_pipe.software_requirements.chrome_is_installed:
            for scen_order in scenario_orders:
                df_case = df[df["scenario_order"] == scen_order]
                fig_case = go.Figure()
                for variable in ["buitenwaterstand", "phi_exit",
                                 "h_exit", "top_zand"]:
                    df_var = df_case[df_case["variable"] == variable]
                    fig_case.add_trace(go.Scatter(
                        x=df_var["metrering"],
                        y=df_var["physical_value"],
                        mode="markers",
                        name=names[variable],
                        marker=dict(
                            color=colors[variable],
                            symbol=symbols[variable],
                            size=5
                        )
                    ))
                fig_case.update_layout(
                    title=f"Phreatic waterline for Scenario {scen_order}",
                    xaxis_title="Metrering",
                    yaxis_title="Hoogte [m+NAP]",
                    showlegend=True,
                )
                fig_case.write_image(
                    os.path.join(
                        export_dir,
                        f"phreatic_waterline_scenario_{scen_order}.png"
                        ),
                    format="png", scale=5, width=1400
                )

    return fig
