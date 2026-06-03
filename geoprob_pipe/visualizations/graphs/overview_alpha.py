from __future__ import annotations

import os
from typing import TYPE_CHECKING

import plotly.graph_objects as go
from pandas import merge
from plotly.subplots import make_subplots
from plotly.graph_objects import Figure


from geoprob_pipe.calculations.systems.mappers.initial_input import (
    INITIAL_INPUT_MAPPER,
)
from geoprob_pipe.cmd_app.utils.misc import get_geohydrological_model

if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


class OverviewAlpha:
    def __init__(self, geoprob_pipe: GeoProbPipe, export: bool = False):
        """
        Verzameling plots van alle alpha's van de vreschillende parameters.

        :param geoprob_pipe: Hoofdopbject van de applicatie.
        :param export: of de plot als html geëxporteerd moet worden, defaults to False
        :return: plotly figuur
        """
        self.geoprob_pipe = geoprob_pipe
        self.export = export
        self.model_string = get_geohydrological_model(
            app_settings=self.geoprob_pipe.input_data.app_settings
        )
        self.initial_input_mapper = INITIAL_INPUT_MAPPER[self.model_string][
            "input"
        ]

        self._collect_data()
        self.fig = self._create_plot()
        self._export()

    def _collect_data(self):
        """
        Verzamelen de data voor de alphas en metrering en voeg de distributies
        en eenheden toe.

        :return: _description_
        """
        # Get data for graphing
        df_alpha = self.geoprob_pipe.results.df_alphas_influence_factors_and_physical_values(
            filter_deterministic=False, filter_derived=False
        )
        df_alpha = df_alpha[
            [
                "uittredepunt_id",
                "ondergrondscenario_id",
                "vak_id",
                "variable",
                "distribution_type",
                "physical_value",
            ]
        ]

        gdf_uittredepunten = self.geoprob_pipe.input_data.uittredepunten.gdf
        self.df_alpha = merge(
            df_alpha,
            gdf_uittredepunten[["uittredepunt_id", "metrering"]],
            on="uittredepunt_id",
            how="left",
        )

        # List of all alphas that can be shown
        self.parameters: list[str] = list(df_alpha["variable"].unique())

        # List of scenarios
        self.scenarios = df_alpha["ondergrondscenario_id"].unique()

        # Add distribution type
        self.dist_types = {}
        for param in self.parameters:
            dist_type = df_alpha.loc[
                df_alpha["variable"] == param, "distribution_type"
            ].unique()[0]
            self.dist_types.update({param: dist_type})

        # Add units
        unit_lookup = {
            item["name"]: item["unit"] for item in self.initial_input_mapper
        }
        self.param_units = {}

        for param in self.parameters:
            try:
                self.param_units.update(
                    {param: str(unit_lookup[param]).strip("[]")}
                )
            except KeyError:
                self.param_units.update({param: "?"})

        # Add parameter units missing in DUMMY_INPUT by hand.
        self.param_units.update(
            {
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
                "z_u": "-",
            }
        )

    def _create_plot(self) -> Figure:
        # Create subplots
        fig = make_subplots(
            rows=len(self.parameters),
            cols=1,
            shared_xaxes=False,
            subplot_titles=self.parameters,
        )

        # Add a button for each ondergrondscenario
        buttons = []

        # Add scatter plot per scenario
        for i, scenario in enumerate(self.scenarios):
            df_case = self.df_alpha[
                self.df_alpha["ondergrondscenario_id"] == scenario
            ]

            for row_idx, param in enumerate(self.parameters, start=1):
                df_param = df_case[df_case["variable"] == param]
                fig.add_trace(
                    go.Scatter(
                        x=df_param["metrering"],
                        y=df_param["physical_value"],
                        mode="markers",
                        marker=dict(color="black", symbol="x", size=5),
                        name=param,
                        visible=(i == 0),
                    ),
                    row=row_idx,
                    col=1,
                )
                fig.update_xaxes(
                    showgrid=True, tickangle=90, row=row_idx, col=1
                )
                fig.update_yaxes(
                    showgrid=True,
                    title_text=f"{param} [{self.param_units[param]}]"
                    + f"<br>({self.dist_types[param]})",
                    row=row_idx,
                    col=1,
                )

            total_traces = len(self.scenarios) * len(self.parameters)

            # Determine which scenario is visible
            vis = [False] * total_traces
            vis[i * len(self.parameters) : (i + 1) * len(self.parameters)] = [
                True
            ] * len(self.parameters)

            buttons.append(
                dict(
                    label=f"{scenario}",
                    method="update",
                    args=[
                        {"visible": vis},
                        {
                            "title": f"Overview of parameters for Scenario {scenario}"
                        },
                    ],
                )
            )

        # Layout and button
        fig.update_layout(
            height=300 * len(self.parameters),
            showlegend=False,
            title=f"Overview of parameters for Scenario {self.scenarios[0]}",
            updatemenus=[
                dict(
                    active=0,
                    buttons=buttons,
                    direction="down",
                    showactive=True,
                    x=1.05,
                    y=1.01,
                )
            ],
        )
        return fig

    def _export(self):
        if self.export:
            export_dir = os.path.join(
                self.geoprob_pipe.visualizations.graphs.export_dir,
                "grafiek_physical_values",
            )
            
            os.makedirs(export_dir, exist_ok=True)

            self.fig.write_html(
                os.path.join(export_dir, "overview_alphas.html"),
                include_plotlyjs="cdn",
            )

            # for scenario in self.scenarios:
            #     df_case = self.df_alpha[
            #         self.df_alpha["ondergrondscenario_id"] == scenario
            #     ]
            #     fig_case = make_subplots(
            #         rows=len(self.parameters),
            #         cols=1,
            #         shared_xaxes=False,
            #         subplot_titles=self.parameters,
            #     )

            #     for row_idx, param in enumerate(self.parameters, start=1):
            #         df_param = df_case[df_case["variable"] == param]
            #         fig_case.add_trace(
            #             go.Scatter(
            #                 x=df_param["metrering"],
            #                 y=df_param["physical_value"],
            #                 mode="markers",
            #                 marker=dict(color="black", symbol="x", size=5),
            #                 name=param,
            #             ),
            #             row=row_idx,
            #             col=1,
            #         )
            #         fig_case.update_xaxes(
            #             showgrid=True, tickangle=90, row=row_idx, col=1
            #         )
            #         fig_case.update_yaxes(
            #             showgrid=True,
            #             title_text=f"{param} [{self.param_units[param]}]"
            #             + f"<br>({self.dist_types[param]})",
            #             row=row_idx,
            #             col=1,
            #         )

            #     fig_case.update_layout(
            #         height=300 * len(self.parameters),
            #         showlegend=False,
            #         title=f"Overview of parameters for Scenario {self.scenarios[0]}",
            #     )


