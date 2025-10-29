from __future__ import annotations
import pandas as pd
from pandas import merge
import numpy as np
import os
from datetime import datetime
import plotly.graph_objects as go
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def _background_graph(
        geoprob_pipe: GeoProbPipe,
        fig: go.Figure,
        df_for_graph: pd.DataFrame
        ) -> go.Figure:
    # Categorie kleuren
    cg = geoprob_pipe.input_data.traject_normering.beta_categorie_grenzen
    colors = ["rgba(0,128,0,0.4)", "rgba(144,238,144,0.4)",
              "rgba(255,255,0,0.4)", "rgba(255,165,0,0.4)",
              "rgba(255,0,0,0.4)", "rgba(128,0,128,0.4)"]
    labels = ["β<sub>eis;sig;dsn / 30</sub>", "β<sub>eis;sig;dsn</sub>",
              "β<sub>eis;ond;dsn</sub>",
              "β<sub>eis;ond</sub>", "β<sub>eis;ond * 30</sub>", ""]

    if "M_value" in df_for_graph.columns:
        x_line = np.linspace(df_for_graph['M_value'].min()-10,
                             df_for_graph['M_value'].max()+10)
    else:
        x_line = np.linspace(df_for_graph['M_van'].min()-10,
                             df_for_graph['M_tot'].max()+10)

    i = 1
    for vak in geoprob_pipe.input_data.vakken:
        fig.add_vline(x=vak.M_van, line_color="black", line_width=1)
        fig.add_vline(x=vak.M_tot, line_color="black", line_width=1)
        fig.add_annotation(
            x=(vak.M_van + vak.M_tot) / 2, y=np.log10(2),
            text=(f"Vak: {i}"),
            showarrow=False,
            xanchor="center",
            yanchor="bottom",
            font=dict(color="black"))
        i += 1

    for i, grens in enumerate(cg):

        if cg[grens][0] <= 0:
            cg[grens][0] = np.log10(2)

        # Onderste lijn (zichtbaar)
        fig.add_trace(go.Scatter(
            x=x_line,
            y=[cg[grens][0]] * len(x_line),
            name=grens,
            mode="lines",
            line=dict(color="black", width=0.5),
            hoverinfo="skip",
            showlegend=False,
        ))

        # Bovenste lijn (onzichtbaar, zorgt voor fill)
        fig.add_trace(go.Scatter(
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
        fig.add_annotation(
            x=x_line.max(),
            y=np.log10(cg[grens][0]),
            text=labels[i % len(labels)],
            showarrow=False,
            xanchor="left",
            yanchor="middle",
            font=dict(color="black", size=10),
            align="right"
        )

    return fig


def beta_scenarios_graph(
        geoprob_pipe: GeoProbPipe,
        export: bool = True
        ) -> go.Figure:
    """ Grafiek van de betrouwbaarheidsindex per scenario over de
    gecombineerde uitvoer (uplift/heave/piping). Over de x-as uitgezet
    tegen de dijkpaal nummering. Op de achtergrond zijn de
    categoriegrenzen weergegeven. """

    # Collect data
    df_uittredepunten = geoprob_pipe.input_data.uittredepunten.df
    df_results_combined = geoprob_pipe.results.df_beta_scenarios
    df_for_graph = merge(
        left=df_results_combined[["uittredepunt_id", "beta"]],
        right=df_uittredepunten[["uittredepunt_id", "M_value"]],
        on="uittredepunt_id",
        how="left"
    )

    # Plot data
    fig = go.Figure()
    # Background
    fig = _background_graph(geoprob_pipe, fig, df_for_graph)

    fig.add_trace(
        go.Scatter(
            x=df_for_graph['M_value'],
            y=df_for_graph["beta"],
            mode='markers',
            marker=dict(symbol='diamond', size=3, color='black'),
            name='Beta scenarios',
            showlegend=True
        )
    )

    # Layout
    fig.update_layout(
        title="Betrouwbaarheidsindex STPH scenarioberekeningen",
        xaxis=dict(title="Metrering",
                   type='linear',
                   range=[0,
                          df_for_graph['M_value'].max()+10],
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
        showlegend=False,
        )

    # Export
    if export:
        export_dir = os.path.join(
            geoprob_pipe.visualizations.graphs.export_dir,
            "grafiek_betrouwbaarheidsindex"
            )
        os.makedirs(export_dir, exist_ok=True)
        if geoprob_pipe.software_requirements.chrome_is_installed:
            fig.write_image(os.path.join(export_dir,
                                         "beta_scenarios.png"),
                            scale=5, width=1400, format="png",)

    return fig


def beta_uittredepunten_graph(
        geoprob_pipe: GeoProbPipe,
        export: bool = True
        ) -> go.Figure:
    """ Grafiek van de betrouwbaarheidsindex per uittredepunt over
    de gecombineerde uitvoer (uplift/heave/piping). Over de x-as
    uitgezet tegen de dijkpaal nummering. Op de achtergrond zijn de
    categoriegrenzen weergegeven. """

    # Collect data
    df_uittredepunten_m = geoprob_pipe.input_data.uittredepunten.df
    df_results_uittredepunten = geoprob_pipe.results.df_beta_uittredepunten
    df_for_graph = merge(
        left=df_results_uittredepunten[["uittredepunt_id", "beta"]],
        right=df_uittredepunten_m[["uittredepunt_id", "M_value"]],
        on="uittredepunt_id",
        how="left"
    )
    # Plot data
    fig = go.Figure()
    # Background
    fig = _background_graph(geoprob_pipe, fig, df_for_graph)

    fig.add_trace(
        go.Scatter(
            x=df_for_graph['M_value'],
            y=df_for_graph["beta"],
            mode='markers',
            marker=dict(symbol='circle', size=3, color='black'),
            name='Beta Uittredepunten',
            showlegend=True
        )
    )

    # Layout
    fig.update_layout(
        title="Betrouwbaarheidsindex STPH per uittredepunt",
        xaxis=dict(title="Metrering",
                   type='linear',
                   range=[0,
                          df_for_graph['M_value'].max()+10],
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
        showlegend=False,
        )

    # Export
    if export:
        export_dir = os.path.join(
            geoprob_pipe.visualizations.graphs.export_dir,
            "grafiek_betrouwbaarheidsindex"
            )
        os.makedirs(export_dir, exist_ok=True)
        if geoprob_pipe.software_requirements.chrome_is_installed:
            fig.write_image(os.path.join(export_dir,
                                         "beta_uittredepunten.png"),
                            format="png", width=1400, scale=5)

    return fig


def beta_vakken_graph(
        geoprob_pipe: GeoProbPipe,
        export: bool = True
        ) -> go.Figure:
    """ Grafiek van de betrouwbaarheidsindex per uittredepunt over de
    gecombineerde uitvoer (uplift/heave/piping). Over de x-as uitgezet
    tegen de dijkpaal nummering. Op de achtergrond zijn de
    categoriegrenzen weergegeven. """

    # Collect data
    df_vakken = geoprob_pipe.input_data.vakken.df
    df_results_vakken = geoprob_pipe.results.df_beta_vakken
    df_for_graph = merge(
        left=df_results_vakken[["vak_id", "beta"]],
        right=df_vakken[["vak_id", "M_van", "M_tot"]],
        on="vak_id",
        how="left"
    )

    # Plot data
    fig = go.Figure()
    # Background
    fig = _background_graph(geoprob_pipe, fig, df_for_graph)

    for index, row in df_for_graph.iterrows():
        fig.add_shape(type="line",
                      x0=row["M_van"], x1=row["M_tot"],
                      y0=row["beta"], y1=row["beta"],
                      line=dict(color="black", width=2.5))

    # Layout
    fig.update_layout(
        title="Betrouwbaarheidsindex STPH per vak",
        xaxis=dict(title="Metrering",
                   type='linear',
                   range=[0,
                          df_for_graph['M_tot'].max()+10],
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
                   )
        )

    # Export
    if export:
        export_dir = os.path.join(
            geoprob_pipe.visualizations.graphs.export_dir,
            "grafiek_betrouwbaarheidsindex"
            )
        os.makedirs(export_dir, exist_ok=True)
        if geoprob_pipe.software_requirements.chrome_is_installed:
            fig.write_image(os.path.join(export_dir, "beta_vakken.png"),
                            format="png", scale=5,  width=1400)

    return fig


class GraphBetaValuesSingleInteractive:

    def __init__(self, geoprob_pipe: GeoProbPipe, export: bool = True):

        # Logic
        self.geoprob_pipe = geoprob_pipe
        self.fig = go.Figure()

        df_uittredepunten = self.geoprob_pipe.input_data.uittredepunten.df
        self.M_van = df_uittredepunten['M_value'].min()-10
        self.M_tot = df_uittredepunten['M_value'].max()+10

        self._add_backgrond()
        self._add_beta_per_vak()
        self._add_beta_per_scenario()
        self._add_beta_per_uittredepunt()
        self._update_layout()
        self._optionally_export(export=export)

    def _add_beta_per_vak(self):
        df_vakken = self.geoprob_pipe.input_data.vakken.df
        df_results_vakken = self.geoprob_pipe.results.df_beta_vakken
        df_for_graph = merge(
            left=df_results_vakken[["vak_id", "beta"]],
            right=df_vakken[["vak_id", "M_van", "M_tot"]],
            on="vak_id",
            how="left"
        )

        for index, row in df_for_graph.iterrows():
            self.fig.add_shape(type="line",
                               x0=row["M_van"], x1=row["M_tot"],
                               y0=row["beta"], y1=row["beta"],
                               line=dict(color="grey", width=2.5),
                               )

    def _add_beta_per_scenario(self):

        df_uittredepunten = self.geoprob_pipe.input_data.uittredepunten.df
        df_results_combined = self.geoprob_pipe.results.df_beta_scenarios
        df_for_graph = merge(
            left=df_results_combined[["uittredepunt_id", "beta"]],
            right=df_uittredepunten[["uittredepunt_id", "M_value"]],
            on="uittredepunt_id",
            how="left"
        )

        self.fig.add_trace(
            go.Scatter(
                x=df_for_graph['M_value'],
                y=df_for_graph["beta"],
                mode='markers',
                marker=dict(symbol='diamond', size=5, color='black'),
                name='Beta Scenarios',
                showlegend=True
            )
        )

    def _add_beta_per_uittredepunt(self):

        df_uittredepunten_m = self.geoprob_pipe.input_data.uittredepunten.df
        df_results_uittredepunten = (self.geoprob_pipe.results
                                     .df_beta_uittredepunten)
        df_for_graph = merge(
            left=df_results_uittredepunten[["uittredepunt_id", "beta"]],
            right=df_uittredepunten_m[["uittredepunt_id", "M_value"]],
            on="uittredepunt_id",
            how="left"
        )

        self.fig.add_trace(
            go.Scatter(
                x=df_for_graph['M_value'],
                y=df_for_graph["beta"],
                mode='markers',
                marker=dict(symbol='circle', size=7, color='black'),
                name='Beta uitredepunten',
                showlegend=True
            )
        )

    def _add_backgrond(self):

        cg = (self.geoprob_pipe.input_data.traject_normering
              .beta_categorie_grenzen)
        colors = ["rgba(0,128,0,0.4)", "rgba(144,238,144,0.4)",
                  "rgba(255,255,0,0.4)", "rgba(255,165,0,0.4)",
                  "rgba(255,0,0,0.4)", "rgba(128,0,128,0.4)"]

        labels = ["β<sub>eis;sig;dsn / 30</sub>", "β<sub>eis;sig;dsn</sub>",
                  "β<sub>eis;ond;dsn</sub>", "β<sub>eis;ond</sub>",
                  "β<sub>eis;ond * 30</sub>", ""]

        x_line = np.linspace(self.M_van, self.M_tot)

        i = 1
        for vak in self.geoprob_pipe.input_data.vakken:
            self.fig.add_vline(x=vak.M_van, line_color="black", line_width=1)
            self.fig.add_vline(x=vak.M_tot, line_color="black", line_width=1)
            self.fig.add_annotation(
                x=(vak.M_van + vak.M_tot) / 2, y=np.log10(2),
                text=(f"Vak: {i}"),
                showarrow=False,
                xanchor="center",
                yanchor="bottom",
                font=dict(color="black")
                )
            i += 1

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
            self.fig.add_annotation(
                x=x_line.max(),
                y=np.log10(cg[grens][0]),
                text=labels[i % len(labels)],
                showarrow=False,
                xanchor="left",
                yanchor="middle",
                font=dict(color="black", size=10),
                align="right"
            )

    def _update_layout(self):

        self.fig.update_layout(
            title="Betrouwbaarheidsindex STPH",
            xaxis=dict(title="Metrering",
                       type='linear',
                       range=[0, self.M_tot],
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
                )
            )

    def _optionally_export(self,
                           export: bool = False,
                           add_timestamp: bool = False):
        if not export:
            return
        export_dir = os.path.join(
            self.geoprob_pipe.visualizations.graphs.export_dir,
            "grafiek_betrouwbaarheidsindex"
            )
        os.makedirs(export_dir, exist_ok=True)
        timestamp_str = ""
        if add_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
            timestamp_str = f"{timestamp}_"
        self.fig.write_html(os.path.join(
            export_dir, f"{timestamp_str}betrouwbaarheidsindex.html"
            ), include_plotlyjs='cdn')
        if self.geoprob_pipe.software_requirements.chrome_is_installed:
            self.fig.write_image(os.path.join(
                export_dir, f"{timestamp_str}betrouwbaarheidsindex.png"
                ), format="png", scale=5,  width=1400)
