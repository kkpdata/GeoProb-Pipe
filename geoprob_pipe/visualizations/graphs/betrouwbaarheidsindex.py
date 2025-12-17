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

    # # Oude categorie grenzen en kleuren
    # cg = geoprob_pipe.input_data.traject_normering.beta_categorie_grenzen
    # colors = ["rgba(0,128,0,0.4)", "rgba(144,238,144,0.4)",
    #           "rgba(255,255,0,0.4)", "rgba(255,165,0,0.4)",
    #           "rgba(255,0,0,0.4)", "rgba(128,0,128,0.4)"]
    # labels = ["β<sub>eis;sig;dsn / 30</sub>", "β<sub>eis;sig;dsn</sub>",
    #           "β<sub>eis;ond;dsn</sub>",
    #           "β<sub>eis;ond</sub>", "β<sub>eis;ond * 30</sub>", ""]

    cg = geoprob_pipe.input_data.traject_normering.riskeer_categorie_grenzen
    colors = ["rgba(30,141,41,0.6)", "rgba(146,206,90,0.6)",
              "rgba(198,226,176,0.6)", "rgba(255,255,0,0.6)",
              "rgba(254,165,3,0.6)", "rgba(255,0,0,0.6)",
              "rgba(177,33,38,0.6)"]
    labels = ["+III", "+II", "+I", "0", "-I", "-II", "-III"]

    if "metrering" in df_for_graph.columns:
        x_line = np.linspace(df_for_graph['metrering'].min()-10,
                             df_for_graph['metrering'].max()+10)
    else:
        x_line = np.linspace(df_for_graph['m_start'].min()-10,
                             df_for_graph['m_end'].max()+10)

    fig.add_annotation(
        x=0.5, y=np.log10(2.1), text="Vak ID:", showarrow=False, xanchor="left", yanchor="bottom",
        font=dict(color="black"))
    i = 1
    for _, vak in geoprob_pipe.input_data.vakken.gdf.iterrows():
        fig.add_vline(x=vak["m_start"], line_color="black", line_width=1)
        fig.add_vline(x=vak["m_end"], line_color="black", line_width=1)
        fig.add_annotation(
            x=(vak["m_start"] + vak["m_end"]) / 2, y=np.log10(2),
            text=f"{i}",
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
            x=x_line, y=[cg[grens][0]] * len(x_line), name=grens, mode="lines", line=dict(color="black", width=0.5),
            hoverinfo="skip", showlegend=False,))

        # Bovenste lijn (onzichtbaar, zorgt voor fill)
        fig.add_trace(go.Scatter(
            x=x_line, y=[cg[grens][1]] * len(x_line), name=grens, mode="lines",
            line=dict(width=0),        # geen bovenrand zichtbaar
            fill="tonexty",
            fillcolor=colors[i % len(colors)],  # kleur uit lijst
            hoverinfo="skip", showlegend=False))

        # Labels bij de ondergrens
        fig.add_annotation(
            x=x_line.max(),
            y=(np.log10(cg[grens][0]) + np.log10(cg[grens][1])) / 2,
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
    gdf_uittredepunten = geoprob_pipe.input_data.uittredepunten.gdf
    df_results_combined = geoprob_pipe.results.df_beta_scenarios
    df_for_graph = merge(
        left=df_results_combined[["uittredepunt_id", "beta", "converged"]],
        right=gdf_uittredepunten[["uittredepunt_id", "metrering"]],
        on="uittredepunt_id",
        how="left"
    )

    # Plot data
    fig = go.Figure()
    # Background
    fig = _background_graph(geoprob_pipe, fig, df_for_graph)
    colors = ["black" if b else "blue" for b in df_for_graph["converged"]]
    fig.add_trace(
        go.Scatter(
            x=df_for_graph['metrering'],
            y=df_for_graph["beta"],
            mode='markers',
            marker=dict(symbol='diamond', size=3, color=colors),
            name='Beta scenarios',
            showlegend=True
        )
    )

    # Layout
    fig.update_layout(
        title="Betrouwbaarheidsindex STPH per scenarioberekening",
        xaxis=dict(title="Metrering",
                   type='linear',
                   range=[0,
                          df_for_graph['metrering'].max()+10],
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
    gdf_uittredepunten_m = geoprob_pipe.input_data.uittredepunten.gdf
    df_results_uittredepunten = geoprob_pipe.results.df_beta_uittredepunten
    df_for_graph = merge(
        left=df_results_uittredepunten[["uittredepunt_id", "beta"]],
        right=gdf_uittredepunten_m[["uittredepunt_id", "metrering"]],
        on="uittredepunt_id",
        how="left"
    )
    # Plot data
    fig = go.Figure()
    # Background
    fig = _background_graph(geoprob_pipe, fig, df_for_graph)

    fig.add_trace(
        go.Scatter(
            x=df_for_graph['metrering'],
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
                          df_for_graph['metrering'].max()+10],
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
    gdf_vakken = geoprob_pipe.input_data.vakken.gdf
    df_results_vakken = geoprob_pipe.results.df_beta_vakken
    df_results_vakken = df_results_vakken.rename(columns={"vak_id": "id"})
    df_for_graph = merge(
        left=df_results_vakken[["id", "beta"]],
        right=gdf_vakken[["id", "m_start", "m_end"]],
        on="id",
        how="left"
    )

    # Plot data
    fig = go.Figure()
    # Background
    fig = _background_graph(geoprob_pipe, fig, df_for_graph)

    for _, row in df_for_graph.iterrows():
        fig.add_shape(type="line",
                      x0=row["m_start"], x1=row["m_end"],
                      y0=row["beta"], y1=row["beta"],
                      line=dict(color="black", width=2.5))

    # Layout
    fig.update_layout(
        title="Betrouwbaarheidsindex STPH per vak",
        xaxis=dict(title="Metrering",
                   type='linear',
                   range=[0,
                          df_for_graph['m_end'].max()+10],
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

        self.gdf_uittredepunten = self.geoprob_pipe.input_data.uittredepunten.gdf
        self.gdf_vakken = self.geoprob_pipe.input_data.vakken.gdf
        self.m_start = self.gdf_vakken['m_start'].min()-10
        self.m_end = self.gdf_vakken['m_end'].max()+10

        self._add_backgrond()
        self._add_beta_per_vak()
        self._add_beta_per_scenario()
        self._add_beta_per_uittredepunt()
        self._update_layout()
        self._optionally_export(export=export)

    def _add_beta_per_vak(self):
        df_results_vakken = self.geoprob_pipe.results.df_beta_vakken
        df_results_vakken = df_results_vakken.rename(columns={"vak_id": "id"})
        df_for_graph = merge(
            left=df_results_vakken[["id", "beta"]],
            right=self.gdf_vakken[["id", "m_start", "m_end"]],
            on="id",
            how="left"
        )
        first = True
        for _, row in df_for_graph.iterrows():
            self.fig.add_trace(go.Scatter(
                x=[row["m_start"], row["m_end"]],
                y=[row["beta"], row["beta"]],
                mode="lines",
                line=dict(color="black", width=2.5),
                name="Beta Vakken",
                legendgroup="Beta vakken",
                showlegend=first
            ))
            first = False

    def _add_beta_per_scenario(self):
        df_results_combined = self.geoprob_pipe.results.df_beta_scenarios
        df_for_graph = merge(
            left=df_results_combined[["uittredepunt_id", "beta", "converged"]],
            right=self.gdf_uittredepunten[["uittredepunt_id", "metrering"]],
            on="uittredepunt_id",
            how="left"
        )

        for value, color, name in [(True, "black", 'Beta scenarios'),
                                   (False, "blue", "Unconverged Beta scenarios")]:
            mask = df_for_graph["converged"] == value
            self.fig.add_trace(
                go.Scatter(
                    x=df_for_graph.loc[mask, 'metrering'],
                    y=df_for_graph.loc[mask, "beta"],
                    mode='markers',
                    marker=dict(symbol='diamond', size=7,
                                color=color,
                                line=dict(color="white", width=1)),
                    name=name,
                    showlegend=True
                )
            )

    def _add_beta_per_uittredepunt(self):
        df_results_uittredepunten = (self.geoprob_pipe.results
                                     .df_beta_uittredepunten)
        df_for_graph = merge(
            left=df_results_uittredepunten[["uittredepunt_id", "beta"]],
            right=self.gdf_uittredepunten[["uittredepunt_id", "metrering"]],
            on="uittredepunt_id",
            how="left"
        )
        beta_min = 2
        beta_max = 20
        mask_low = df_for_graph["beta"] < beta_min
        mask_high = df_for_graph["beta"] > beta_max
        mask_in = ~(mask_low | mask_high)
        # In range
        self.fig.add_trace(
            go.Scatter(
                x=df_for_graph.loc[mask_in, 'metrering'],
                y=df_for_graph.loc[mask_in, "beta"],
                mode='markers',
                marker=dict(symbol='circle', size=7, color='black'),
                name='Beta uittredepunten',
                customdata=df_for_graph.loc[mask_in, ["beta", "metrering"]],
                hovertemplate=("Beta: %{customdata[0]:.3f}<br>" +
                               "Metrering: %{customdata[1]}"),
                showlegend=True
            )
        )
        # Above range
        self.fig.add_trace(
            go.Scatter(
                x=df_for_graph.loc[mask_high, 'metrering'],
                y=[beta_max-0.1] * mask_high.sum(),
                mode='markers',
                marker=dict(symbol='triangle-up', size=7, color='black'),
                name='Beta uittredepunten above range',
                customdata=df_for_graph.loc[mask_high, ["beta", "metrering"]],
                hovertemplate=("Beta: %{customdata[0]:.3f}<br>" +
                               "Metrering: %{customdata[1]}"),
                showlegend=True
            )
        )
        # Below range
        self.fig.add_trace(
            go.Scatter(
                x=df_for_graph.loc[mask_low, 'metrering'],
                y=[beta_min+0.1] * mask_low.sum(),
                mode='markers',
                marker=dict(symbol='triangle-down', size=7, color='black'),
                name='Beta uittredepunten below range',
                customdata=df_for_graph.loc[mask_low, ["beta", "metrering"]],
                hovertemplate=("Beta: %{customdata[0]:.3f}<br>" +
                               "Metrering: %{customdata[1]}"),
                showlegend=True
            )
        )

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

        cg = (self.geoprob_pipe.input_data.traject_normering
              .riskeer_categorie_grenzen)
        colors = ["rgba(30,141,41,0.6)", "rgba(146,206,90,0.6)",
                  "rgba(198,226,176,0.6)", "rgba(255,255,0,0.6)",
                  "rgba(254,165,3,0.6)", "rgba(255,0,0,0.6)",
                  "rgba(177,33,38,0.6)"]
        labels = ["+III", "+II", "+I", "0", "-I", "-II", "-III"]

        x_line = np.linspace(self.m_start, self.m_end)

        self.fig.add_annotation(x=0.5,
                                y=np.log10(2.1),
                                text="Vak ID:",
                                showarrow=False,
                                xanchor="left",
                                yanchor="bottom",
                                font=dict(color="black")
                                )
        i = 1

        for _, vak in self.gdf_vakken.iterrows():
            self.fig.add_vline(x=vak["m_start"], line_color="black",
                               line_width=1)
            self.fig.add_vline(x=vak["m_end"], line_color="black",
                               line_width=1)
            self.fig.add_annotation(
                x=(vak["m_start"] + vak["m_end"]) / 2, y=np.log10(2),
                text=f"{i}",
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
                y=(np.log10(cg[grens][0]) + np.log10(cg[grens][1])) / 2,
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
