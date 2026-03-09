from __future__ import annotations
from pandas import DataFrame, merge
import numpy as np
import os
from datetime import datetime
import plotly.graph_objects as go
from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def _add_beta_per_uittredepunt_points(
        self, df_for_graph: DataFrame, mask,
        name: str, color: str, value: bool
        ):
    """ Visualization of beta of uittredepunten.

    :param self: GraphBetaValuesSingleInteractive-object
    :param df_for_graph: Data to plot
    :param mask: Boolean Series for which uittredepunten to plot in graph. Either converged of unconverged points.
    :param name: Marker name
    :param color: Marker color
    :param value: Requested option: converged or not converged
    """

    self.fig.add_trace(
        go.Scatter(
            x=df_for_graph.loc[mask, "metrering"],
            y=df_for_graph.loc[mask, "beta"],
            mode='markers', marker=dict(symbol='circle', size=7, color=color),
            name=name,
            customdata=df_for_graph.loc[mask, ["uittredepunt_id", "beta", "metrering"]],
            hovertemplate=("ID: %{customdata[0]}<br>" +
                           "Beta: %{customdata[1]:.3f}<br>" +
                           "Metrering: %{customdata[2]}"),
            legendgroup="Beta uittredepunten", showlegend=value))


def _add_beta_per_uittredepunt_indication_above_plotting_range(
        self, df_for_graph: DataFrame, mask, name: str, color: str, value: bool):
    """ Indication to user that there are Beta results plotted outside
    the plotting range. In this case above range.
    """

    self.fig.add_trace(
        go.Scatter(
            x=df_for_graph.loc[mask, 'metrering'],
            y=[self.beta_max - 0.1] * mask.sum(),
            mode='markers',
            marker=dict(symbol='triangle-up', size=7, color=color),
            name=name + " above plotted range",
            customdata=df_for_graph.loc[mask, ["uittredepunt_id", "beta", "metrering"]],
            hovertemplate=("ID: %{customdata[0]}<br>" +
                           "Beta: %{customdata[1]:.3f}<br>" +
                           "Metrering: %{customdata[2]}"),
            legendgroup="Beta uittredepunten",
            showlegend=value
        )
    )


def _add_beta_per_uittredepunt_indication_below_plotting_range(
        self, df_for_graph: DataFrame, mask, name: str, color: str, value: bool):
    """ Indication to user that there are Beta results plotted outside
    the plotting range. In this case below range.
    """

    self.fig.add_trace(
        go.Scatter(
            x=df_for_graph.loc[mask, 'metrering'],
            y=[self.beta_min + 0.1] * mask.sum(),
            mode='markers',
            marker=dict(symbol='triangle-down', size=7, color=color),
            name=name + " below plotted range",
            customdata=df_for_graph.loc[mask, ["uittredepunt_id", "beta", "metrering"]],
            hovertemplate=("ID: %{customdata[0]}<br>" +
                           "Beta: %{customdata[1]:.3f}<br>" +
                           "Metrering: %{customdata[2]}"),
            legendgroup="Beta uittredepunten",
            showlegend=value
        )
    )


class GraphBetaValuesSingleInteractive:

    def __init__(self, geoprob_pipe: GeoProbPipe, export: bool = True):

        # Logic
        self.geoprob_pipe = geoprob_pipe
        self.fig = go.Figure()

        self.gdf_uittredepunten = self.geoprob_pipe.input_data.uittredepunten.gdf
        self.gdf_vakken = self.geoprob_pipe.input_data.vakken.gdf
        self.m_start = self.gdf_vakken['m_start'].min()-10
        self.m_end = self.gdf_vakken['m_end'].max()+10

        self.beta_min = 2
        self.beta_max = 20

        self._add_backgrond()
        self._add_beta_per_traject()
        self._add_beta_per_vak()
        self._add_beta_per_scenario()
        self._add_beta_per_uittredepunt()
        self._update_layout()
        self._optionally_export(export=export)

    def _add_backgrond(self):
        # Oude categorie grenzen
        # cg = (self.geoprob_pipe.input_data.traject_normering
        #       .beta_categorie_grenzen)
        # colors = ["rgba(0,128,0,0.4)", "rgba(144,238,144,0.4)",
        #           "rgba(255,255,0,0.4)", "rgba(255,165,0,0.4)",
        #           "rgba(255,0,0,0.4)", "rgba(128,0,128,0.4)"]

        # labels = ["β<sub>eis;sig;dsn / 30</sub>", "β<sub>eis;sig;dsn</sub>",
        #           "β<sub>eis;ond;dsn</sub>", "β<sub>eis;ond</sub>",
        #           "β<sub>eis;ond * 30</sub>", ""]

        cg = self.geoprob_pipe.input_data.traject_normering.riskeer_categorie_grenzen
        colors = ["rgba(30,141,41,0.6)", "rgba(146,206,90,0.6)",
                  "rgba(198,226,176,0.6)", "rgba(255,255,0,0.6)",
                  "rgba(254,165,3,0.6)", "rgba(255,0,0,0.6)",
                  "rgba(177,33,38,0.6)"]
        labels = ["+III", "+II", "+I", "0", "-I", "-II", "-III"]

        x_line = np.linspace(self.m_start, self.m_end)
        self.annotation_vak = []
        self.annotation_vak.append(dict(x=0.5,
                                        y=np.log10(2.1),
                                        text="Vak ID:",
                                        showarrow=False,
                                        xanchor="left",
                                        yanchor="bottom",
                                        font=dict(color="black")
                                        ))
        self.vak_lines = []
        for _, vak in self.gdf_vakken.iterrows():
            self.vak_lines.append(dict(
                x0=vak["m_start"], x1=vak["m_start"],
                y0=0, y1=1,
                xref="x", yref="paper",
                line=dict(color="black", width=1)
                ))
            self.vak_lines.append(dict(
                x0=vak["m_end"], x1=vak["m_end"],
                y0=0, y1=1,
                xref="x", yref="paper",
                line=dict(color="black", width=1)
                ))
            self.annotation_vak.append(dict(
                x=(vak["m_start"] + vak["m_end"]) / 2, y=np.log10(2),
                text=vak["id"],
                showarrow=False,
                xanchor="center",
                yanchor="bottom",
                font=dict(color="black")
                ))
        self.annotation_label = []
        for i, grens in enumerate(cg):

            if cg[grens][0] <= 0:
                cg[grens][0] = np.log10(2)

            # Onderste lijn (zichtbaar)
            self.fig.add_trace(
                go.Scatter(
                    x=x_line,
                    y=[cg[grens][0]] * len(x_line),
                    name=grens,
                    mode="lines",
                    line=dict(color="black", width=0.5),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

            # Bovenste lijn (onzichtbaar, zorgt voor fill)
            self.fig.add_trace(go.Scatter(
                x=x_line,
                y=[cg[grens][1]] * len(x_line),
                name=grens,
                mode="lines",
                line=dict(width=0),        # geen bovenrand zichtbaar
                fill="tonexty",
                fillcolor=colors[i % len(colors)],  # kleur uit lijst
                hoverinfo="skip",
                showlegend=False,
            ))

            # Labels bij de ondergrens
            self.annotation_label.append(dict(
                x=x_line.max(),
                y=(np.log10(cg[grens][0]) + np.log10(cg[grens][1])) / 2,
                text=labels[i % len(labels)],
                showarrow=False,
                xanchor="left",
                yanchor="middle",
                font=dict(color="black", size=10),
                align="right"
            ))

    def _add_beta_per_traject(self):
        # TODO Update met df_beta_traject_aanpassing
        beta_traject = cast(
            float, self.geoprob_pipe.results.df_beta_traject[
                "lower_bound_beta"][0]
            )
        self.fig.add_trace(go.Scatter(
            x=[self.m_start, self.m_end],
            y=[beta_traject, beta_traject],
            mode="lines",
            line=dict(color="black", width=2.5),
            name="Beta Traject",
            showlegend=True
        ))

    def _add_beta_per_scenario(self):
        df_beta_scenarios_final = self.geoprob_pipe.results.df_beta_scenarios_final
        df_for_graph = merge(
            left=df_beta_scenarios_final[[
                "uittredepunt_id", "beta", "converged", "method_used", "flow_chart_number", "advise"]],
            right=self.gdf_uittredepunten[["uittredepunt_id", "metrering"]],
            on="uittredepunt_id", how="left")
        df_for_graph["converged_alt"] = df_for_graph["flow_chart_number"] != 5

        for value, color, name in [(True, "black", 'Beta scenarios'),
                                   (False, "blue", "Verder rekenen geadviseerd (scenarios)")]:
            mask = df_for_graph["converged_alt"] == value
            mask_low = df_for_graph["beta"] < self.beta_min
            mask_high = df_for_graph["beta"] > self.beta_max

            # In range
            self.fig.add_trace(
                go.Scatter(
                    x=df_for_graph.loc[mask, 'metrering'], y=df_for_graph.loc[mask, "beta"], mode='markers',
                    marker=dict(symbol='diamond', size=7, color=color, line=dict(color="white", width=1)),
                    legendgroup="Beta scenarios", showlegend=value, name=name,
                    customdata=df_for_graph.loc[mask, [
                        "uittredepunt_id", "beta", "metrering", "method_used", "converged", "advise"]],
                    hovertemplate=(
                        "ID: %{customdata[0]}<br>"
                        "Beta: %{customdata[1]:.3f}<br>"
                        "Metrering: %{customdata[2]}<br>"
                        "Methode: %{customdata[3]}<br>"
                        "Converged: %{customdata[4]}<br>"
                        "Advies: %{customdata[5]}")))

            # Above range
            mask_combi = mask & mask_high
            self.fig.add_trace(
                go.Scatter(
                    x=df_for_graph.loc[mask_combi, 'metrering'], y=[self.beta_max-0.1] * mask_combi.sum(),
                    mode='markers',
                    marker=dict(symbol='triangle-up', size=7, color=color, line=dict(color="white", width=1)),
                    legendgroup="Beta scenarios", showlegend=value, name=name + " above plotted range",
                    customdata=df_for_graph.loc[mask_combi, ["uittredepunt_id", "beta", "metrering"]],
                    hovertemplate="ID: %{customdata[0]}<br>"
                                  "Beta: %{customdata[1]:.3f}<br>"
                                  "Metrering: %{customdata[2]}"))

            # Below range
            mask_combi = mask & mask_low
            self.fig.add_trace(
                go.Scatter(
                    x=df_for_graph.loc[mask_combi, 'metrering'], y=[self.beta_min+0.1] * mask_combi.sum(),
                    mode='markers', name=name + " below plotted range",
                    marker=dict(symbol='triangle-down', size=7, color=color, line=dict(color="white", width=1)),
                    legendgroup="Beta scenarios", showlegend=value,
                    customdata=df_for_graph.loc[mask_combi, ["uittredepunt_id", "beta", "metrering"]],
                    hovertemplate=("ID: %{customdata[0]}<br>" +
                                   "Beta: %{customdata[1]:.3f}<br>" +
                                   "Metrering: %{customdata[2]}")))

    def _add_beta_per_uittredepunt(self):

        # Gather results to plot
        df_results_uittredepunten = self.geoprob_pipe.results.df_beta_uittredepunten
        df_for_graph: DataFrame = merge(
            left=df_results_uittredepunten[["uittredepunt_id", "beta", "converged", "flow_chart_number", "advise"]],
            right=self.gdf_uittredepunten[["uittredepunt_id", "metrering"]],
            on="uittredepunt_id",
            how="left"
        )
        df_for_graph["converged_alt"] = df_for_graph["flow_chart_number"] != 11

        # Plot converged and 'Verder rekenen geadviseerd' values
        for value, color, name in [
            (True, "black", "Beta uittredepunt"),
            (False, "blue", "Verder rekenen geadviseerd (uittredepunten)")
        ]:

            mask = df_for_graph["converged_alt"] == value
            _add_beta_per_uittredepunt_points(
                self=self, df_for_graph=df_for_graph, mask=mask, name=name, color=color, value=value)

            mask_high = df_for_graph["beta"] > self.beta_max
            _add_beta_per_uittredepunt_indication_above_plotting_range(
                self=self, df_for_graph=df_for_graph, mask=mask & mask_high, name=name, color=color, value=value)

            mask_low = df_for_graph["beta"] < self.beta_min
            _add_beta_per_uittredepunt_indication_below_plotting_range(
                self=self, df_for_graph=df_for_graph, mask=mask & mask_low, name=name, color=color, value=value)

    def _add_beta_per_vak(self):

        # Gather data
        df_results_vakken = self.geoprob_pipe.results.df_beta_vakken_new
        df_results_vakken = df_results_vakken.rename(columns={"vak_id": "id"})
        df_for_graph = merge(
            left=df_results_vakken[["id", "beta", "advise"]],
            right=self.gdf_vakken[["id", "m_start", "m_end"]],
            on="id", how="left")
        first = True

        # Iterate and plot
        for value, color, name in [(True, "black", "Beta vakken"),
                                   (False, "blue", "Verder rekenen geadviseerd (vakken)")]:

            # Plotting vak lines
            mask = (df_for_graph["advise"] == "-") == value
            mask_low = df_for_graph["beta"] < self.beta_min
            mask_high = df_for_graph["beta"] > self.beta_max
            for _, row in df_for_graph.loc[mask].iterrows():
                self.fig.add_trace(go.Scatter(
                    x=[row["m_start"], row["m_end"]], y=[row["beta"], row["beta"]],
                    mode="lines", line=dict(color=color, width=2.5), name=name, legendgroup="Beta vakken",
                    showlegend=first & value, customdata=[[row["id"], row["beta"]]] * 2,
                    hovertemplate="ID: %{customdata[0]}<br>" +
                                  "Beta: %{customdata[1]:.3f}"))
                first = False

            # Above range
            mask_combi = mask & mask_high
            first = True
            for _, row in df_for_graph.loc[mask_combi].iterrows():
                self.fig.add_trace(go.Scatter(
                    x=[(row["m_start"] + row["m_end"]) / 2],
                    y=[self.beta_max-0.1],
                    mode="markers",
                    marker=dict(color=color, symbol="triangle-up", size=9),
                    name=name + " above plotted range",
                    customdata=[[row["id"], row["beta"]]],
                    hovertemplate=("ID: %{customdata[0]}<br>" +
                                   "Beta: %{customdata[1]:.3f}<br>"),
                    legendgroup="Beta vakken",
                    showlegend=first & value
                ))
                first = False

            # Below range
            mask_combi = mask & mask_low
            first = True
            for _, row in df_for_graph.loc[mask_combi].iterrows():
                self.fig.add_trace(go.Scatter(
                    x=[(row["m_start"] + row["m_end"]) / 2], y=[self.beta_min+0.1],
                    mode="markers", marker=dict(color=color, symbol="triangle-down", size=9),
                    name=name + " below plotted range",
                    customdata=[[row["id"], row["beta"]]],
                    hovertemplate="ID: %{customdata[0]}<br>" +
                                  "Beta: %{customdata[1]:.3f}<br>",
                    legendgroup="Beta vakken", showlegend=first & value
                ))
                first = False

    def _update_layout(self):
        self.fig.add_trace(go.Scatter(
            x=[0], y=[0], name="Verder rekenen geadviseerd", showlegend=True,
            mode="markers", marker=dict(color="blue", symbol="square")))
        annotation = self.annotation_vak + self.annotation_label
        self.fig.update_layout(
            title="Betrouwbaarheidsindex STPH",
            xaxis=dict(title="Metrering",
                       type='linear',
                       range=[0, self.m_end],
                       showgrid=True,
                       gridwidth=0.5,
                       gridcolor="gray"
                       ),
            yaxis=dict(title="Betrouwbaarheidsindex β [-]",
                       type='log',
                       range=[np.log10(2), np.log10(20)],
                       showgrid=True,
                       gridwidth=0.5,
                       gridcolor="gray",
                       tickmode="array",
                       tickvals=[2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20],
                       ticktext=[2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20]
                       ),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
                ),
            annotations=annotation,
            shapes=self.vak_lines
            )
        # Toggles for annotations
        self.fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="right",
                    buttons=[
                        dict(
                            label="Show annotations",
                            method="relayout",
                            args=["annotations",
                                  self.annotation_vak + self.annotation_label]
                        ),
                        dict(
                            label="Hide annotations",
                            method="relayout",
                            args=["annotations", self.annotation_label]
                        ),
                        dict(
                            label="Show vlines",
                            method="relayout",
                            args=["shapes", self.vak_lines]
                        ),
                        dict(
                            label="Hide vlines",
                            method="relayout",
                            args=["shapes", []]
                        )
                    ],
                    x=0.5,
                    y=1.15,
                    xanchor="center"
                )
            ]
        )

    def _optionally_export(self, export: bool = False, add_timestamp: bool = False):
        if not export:
            return
        os.makedirs(self.geoprob_pipe.visualizations.graphs.export_dir, exist_ok=True)
        timestamp_str = ""
        if add_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
            timestamp_str = f"{timestamp}_"
        self.fig.write_html(os.path.join(
            self.geoprob_pipe.visualizations.graphs.export_dir, f"{timestamp_str}betrouwbaarheidsindex.html"
            ), include_plotlyjs='cdn')
