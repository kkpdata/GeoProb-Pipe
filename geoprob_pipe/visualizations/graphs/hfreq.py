from __future__ import annotations
import os
import matplotlib.pyplot as plt
from typing import TYPE_CHECKING, List
import plotly.graph_objects as go
from datetime import datetime
from probabilistic_library import FragilityValue
from pydra_core.core.datamodels.frequency_line import FrequencyLine

if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def hfreq_graphs_per_location(geoprob_pipe: GeoProbPipe, export: bool = True) -> List[plt.Figure]:
    """ Grafiek van de overschrijdingsfrequentielijn van de waterstand per HydraNL uitvoerpunt. """

    # TODO Later Should Middel: Visualiseer WBN waterstand in hfreq-plot ter bewustzijn. 
    # TODO Later Nice Middel: Visualiseer physical design point value in hfreq-plot ter bewustzijn.

    export_dir = os.path.join(geoprob_pipe.visualizations.graphs.export_dir, "grafiek_hfreq")
    os.makedirs(export_dir, exist_ok=True)
    figures = []
    gdf_uittredepunten = geoprob_pipe.input_data.uittredepunten.gdf
    hydra_nl_names = geoprob_pipe.input_data.hydra_nl_data.gdf_locations['location_name'].values.tolist()

    for hydra_nl_name in hydra_nl_names:
        
        # Collect data for the graph
        fragility_values: List[FragilityValue] = geoprob_pipe.input_data.hrd_fragility_values(ref=hydra_nl_name)
        levels = [value.x for value in fragility_values]
        freqs = [value.probability_of_failure for value in fragility_values]
        uittredepunten = list(gdf_uittredepunten[gdf_uittredepunten['hrd_name'] == hydra_nl_name]['uittredepunt_id'])

        # Create the graph
        plt.ioff()
        fig = plt.figure(figsize=(8, 5))
        ax= fig.add_subplot(111)
        ax.plot(levels, freqs, marker='o', linestyle='-', color='blue',markersize=1)
        ax.set_xscale("linear")  # belasting vaak lineair
        ax.set_yscale("log")     # faalkans logaritmisch
        ax.set_xlabel("Waterstand (m+NAP)")
        ax.set_ylabel("Overschrijdingsfrequentie (log-schaal)")
        ax.set_title(f"HydraNL locatie: {hydra_nl_name}\n"
                     f"behorend bij uittredepunten: " + ", ".join([str(u) for u in uittredepunten]))
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
        self._add_dummy_physical_value_legend_marker()
        self._add_overschrijdingsfrequentielijnen()
        self._add_physical_values()
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

    def _add_dummy_physical_value_legend_marker(self):
        # Dummy legend marker
        self.fig.add_trace(go.Scatter(
            x=[-99], y=[1], mode='markers', name='Physical values', showlegend=True,
            marker=dict(color='LightSkyBlue', size=10, line=dict(color='black', width=1))))

    def _add_overschrijdingsfrequentielijnen(self):
        hydra_nl_names = self.geoprob_pipe.input_data.hydra_nl_data.gdf_locations['location_name'].values.tolist()
        hydra_nl_names.sort()
        for index, hydra_nl_name in enumerate(hydra_nl_names):

            # Collect data for the graph
            fragility_values = self.geoprob_pipe.input_data.hydra_nl_data.hrd_fragility_values(ref=hydra_nl_name)
            levels = [item.x for item in fragility_values]
            self.max_level = max(self.max_level, max(levels))
            self.min_level = min(self.min_level, min(levels))
            freqs = [item.probability_of_failure for item in fragility_values]
            self.max_p = max(self.max_p, max(freqs))
            self.min_p = min(self.min_p, min(freqs))
            gdf_uittredepunten = self.geoprob_pipe.input_data.uittredepunten.gdf
            uittredepunten = list(
                gdf_uittredepunten[gdf_uittredepunten['hrd_name'] == hydra_nl_name]['uittredepunt_id'])

            # Only first overschrijdingsfrequentielijn should be visible at first
            visible = 'legendonly'
            if index == 0:
                visible = True

            # Add lines
            legend_name = (f"{hydra_nl_name}<br>"
                           f"uittredepunten: {', '.join([str(u) for u in uittredepunten])}")
            self.fig.add_trace(go.Scatter(
                x=levels,
                y=freqs,
                mode='lines',
                name=legend_name,
                legendgroup=legend_name,
                visible=visible,
                line=dict(dash='dash', color='blue', width=1.5),
                showlegend=True))

    def _add_physical_values(self):
        hydra_nl_names = self.geoprob_pipe.input_data.hydra_nl_data.gdf_locations['location_name'].values.tolist()
        hydra_nl_names.sort()
        for index, hydra_nl_name in enumerate(hydra_nl_names):

            # Collect data for the graph
            gdf_uittredepunten = self.geoprob_pipe.input_data.uittredepunten.gdf
            uittredepunten = list(
                gdf_uittredepunten[gdf_uittredepunten['hrd_name'] == hydra_nl_name]['uittredepunt_id'])

            # Only first overschrijdingsfrequentielijn should be visible at first
            visible = 'legendonly'
            if index == 0:
                visible = True

            # Get physical values
            legend_name = (f"{hydra_nl_name}<br>"
                           f"uittredepunten: {', '.join([str(u) for u in uittredepunten])}")
            df = self.geoprob_pipe.results.df_alphas_influence_factors_and_physical_values(
                filter_deterministic=False, filter_derived=True)
            df = df[df['variable'] == 'buitenwaterstand']
            df = df[df['uittredepunt_id'].isin(uittredepunten)]
            levels = df['physical_value'].values
            self.max_level = max(self.max_level, levels.max())
            self.min_level = min(self.min_level, levels.min())
            freq_line2: FrequencyLine = self.geoprob_pipe.input_data.hydra_nl_data.hrd_frequency_line(ref=hydra_nl_name)
            frequencies = [freq_line2.interpolate_level(level) for level in levels]
            self.max_p = max(self.max_p, max(frequencies))
            self.min_p = min(self.min_p, min(frequencies))

            # Add markers
            self.fig.add_trace(go.Scatter(
                x=levels,
                y=frequencies,
                mode='markers',
                visible=visible,
                marker=dict(color='LightSkyBlue', size=10, line=dict(color='black', width=1)),
                showlegend=False,
                legendgroup=legend_name))

    def _yticks(self):
        min_range = int(f"{self.min_p:.0e}".split("e")[1])
        e_values = list(range(0, min_range - 15, -1))
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
                tickformat=".0e",
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
                ),
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
        self.fig.write_html(os.path.join(export_dir, f"{timestamp_str}hfreq.html"), include_plotlyjs='cdn')
        if self.geoprob_pipe.software_requirements.chrome_is_installed:
            self.fig.write_image(os.path.join(export_dir, f"{timestamp_str}hfreq.png"), format="png")
