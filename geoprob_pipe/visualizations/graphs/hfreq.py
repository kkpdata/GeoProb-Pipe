from __future__ import annotations
import os
import matplotlib.pyplot as plt
from typing import TYPE_CHECKING, List
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def hfreq_graphs_per_location(geoprob_pipe: GeoProbPipe, export: bool = True) -> List[plt.Figure]:
    """ Grafiek van de overschrijdingsfrequentielijn van de waterstand per HydraNL uitvoerpunt. """

    # TODO Later Should Middel: Visualiseer WBN waterstand in hfreq-plot ter bewustzijn. 
    # TODO Later Nice Middel: Visualiseer physical design point value in hfreq-plot ter bewustzijn.

    export_dir = os.path.join(geoprob_pipe.visualizations.graphs.export_dir, "grafiek_hfreq")
    os.makedirs(export_dir, exist_ok=True)
    figures = []
    df_uittredepunten = geoprob_pipe.input_data.uittredepunten.df
    for hydra_nl_name in geoprob_pipe.input_data.overschrijdingsfrequentielijnen.keys():
        
        # Collect data for the graph
        hfreq = geoprob_pipe.input_data.overschrijdingsfrequentielijnen[hydra_nl_name]
        levels = hfreq.overschrijdingsfrequentielijn.level
        freq =  hfreq.overschrijdingsfrequentielijn.exceedance_frequency
        uittredepunten = list(df_uittredepunten[df_uittredepunten['hydra_locatie_id'] == hydra_nl_name]['uittredepunt_id'])

        # Create the graph
        plt.ioff()
        fig = plt.figure(figsize=(8, 5))
        ax= fig.add_subplot(111)
        ax.plot(levels, freq, marker='o', linestyle='-', color='blue',markersize=1)
        ax.set_xscale("linear")  # belasting vaak lineair
        ax.set_yscale("log")     # faalkans logaritmisch
        ax.set_xlabel("Waterstand (m+NAP)")
        ax.set_ylabel("Overschrijdingsfrequentie (log-schaal)")
        ax.set_title("HydraNL locatie: " + hydra_nl_name + "\nbehorend bij uittredepunten: " + ", ".join([str(u) for u in uittredepunten]))
        ax.grid(True, which="both", linestyle='--', linewidth=0.5)
        fig.tight_layout()
        figures.append(fig)

        # Export or not?
        export_path = os.path.join(export_dir, f"{hydra_nl_name}_hfreq.png")
        if export:
            plt.savefig(export_path)
            plt.close(fig)

    return figures


class GraphHFreqSingleInteractive:

    def __init__(self, geoprob_pipe: GeoProbPipe, export: bool = False):

        # Helper parameters
        self.max_level: float = -999
        self.min_level: float = 999
        self.max_p: float = 0.0
        self.min_p: float = 1.0

        # Logic
        self.geoprob_pipe = geoprob_pipe
        self.fig = go.Figure()
        self._add_ondergrens()
        self._add_signaleringswaarde()
        self._add_overschrijdingsfrequentielijnen()
        self._update_layout()
        self._optionally_export(export=export)

    def _add_ondergrens(self):
        ondergrens = 1 / self.geoprob_pipe.input_data.traject_normering.ondergrens
        self.fig.add_trace(go.Scatter(
            x=[-100, 999],
            y=[ondergrens, ondergrens],
            mode='lines',
            name=f"Ondergrens (1/{self.geoprob_pipe.input_data.traject_normering.ondergrens:,} jaren)",
            line=dict(color='black', width=3),
            showlegend=True,
        ))

    def _add_signaleringswaarde(self):
        signaleringswaarde = 1 / self.geoprob_pipe.input_data.traject_normering.signaleringswaarde
        self.fig.add_trace(go.Scatter(
            x=[-100, 999],
            y=[signaleringswaarde, signaleringswaarde],
            mode='lines',
            name=f"Signaleringswaarde (1/{self.geoprob_pipe.input_data.traject_normering.signaleringswaarde:,} jaren)",
            line=dict(dash='dash', color='black', width=3),
            showlegend=True,
        ))

    def _add_overschrijdingsfrequentielijnen(self):
        for index, hydra_nl_name in enumerate(self.geoprob_pipe.input_data.overschrijdingsfrequentielijnen.keys()):

            # Collect data for the graph
            hfreq = self.geoprob_pipe.input_data.overschrijdingsfrequentielijnen[hydra_nl_name]
            levels: np.ndarray = hfreq.overschrijdingsfrequentielijn.level
            self.max_level = max(self.max_level, levels.max())
            self.min_level = min(self.min_level, levels.min())
            freq = hfreq.overschrijdingsfrequentielijn.exceedance_frequency
            self.max_p = max(self.max_p, freq.max())
            self.min_p = min(self.min_p, freq.min())
            df_uittredepunten = self.geoprob_pipe.input_data.uittredepunten.df
            uittredepunten = list(
                df_uittredepunten[df_uittredepunten['hydra_locatie_id'] == hydra_nl_name]['uittredepunt_id'])

            # Only first overschrijdingsfrequentielijn should be visible at first
            visible = 'legendonly'
            if index == 0:
                visible = True

            # Add lines
            self.fig.add_trace(go.Scatter(
                x=levels,
                y=freq,
                mode='lines',
                name=f"{hydra_nl_name}<br>"
                     f"uittredepunten: {', '.join([str(u) for u in uittredepunten])}",
                visible=visible,
                line=dict(dash='dash', color='blue', width=1.5),
                showlegend=True,
            ))

    def _yticks(self):
        min_range = int(f"{self.min_p:.0e}".split("e")[1])
        e_values = list(range(0, min_range - 1, -1))
        y_ticks = [10 ** e_value for e_value in e_values]
        y_ticks_text = [f"10<sup>{e_value}</sup>" for e_value in e_values]
        return y_ticks, y_ticks_text

    def _update_layout(self):
        length_range_xaxis = self.max_level - self.min_level
        xaxis_add = length_range_xaxis * 0.05
        y_ticks, y_ticks_text = self._yticks()
        self.fig.update_layout(
            title=f"<b>Overschrijdingsfrequentielijnen voor alle HydraNL locaties</b><br>"
                  f"<sup>Traject {self.geoprob_pipe.input_data.traject_normering.traject_id}</sup>",
            xaxis=dict(
                title=f"Waterstand (m+NAP)",
                type='linear',
                showgrid=True,
                gridwidth=0.5,
                gridcolor="gray",
                range=[self.min_level - xaxis_add, self.max_level + xaxis_add],
            ),
            yaxis=dict(
                title=f"Overschrijdingsfrequentie (log-schaal)",
                type='log',
                showgrid=True,
                tickformat=".0e",  # TODO: Not satisfied about gridlines and ticks
                gridwidth=1.0,
                tickvals=y_ticks,
                ticktext=y_ticks_text,
                tickmode='array',
                gridcolor="gray",
                minor=dict(
                    showgrid=True,
                    dtick="D1",
                    gridwidth=0.5,
                    gridcolor='rgb(199, 197, 193)',
                )
            )
        )

    def _optionally_export(self, export: bool = False, add_timestamp: bool = False):
        if not export:
            return
        export_dir = os.path.join(self.geoprob_pipe.visualizations.graphs.export_dir, "grafiek_hfreq")
        os.makedirs(export_dir, exist_ok=True)
        timestamp_str = ""
        if add_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
            timestamp_str = f"{timestamp}_"
        self.fig.write_html(os.path.join(export_dir, f"{timestamp_str}hfreq.html"))
        self.fig.write_image(os.path.join(export_dir, f"{timestamp_str}hfreq.png"), format="png")
