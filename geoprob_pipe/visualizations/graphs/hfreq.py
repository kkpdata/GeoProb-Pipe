from __future__ import annotations
import os
# import matplotlib.pyplot as plt
from typing import TYPE_CHECKING, List
import plotly.graph_objects as go
from datetime import datetime
# from geopandas import GeoDataFrame, read_file
# from probabilistic_library import FragilityValue
import pydra_core as pydra
from pandas import Series, concat, DataFrame, read_sql
from geoprob_pipe.questionnaire.parameter_input.expand_input_tables import run_expand_input_tables
import sqlite3

if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


# Onderstaande grafiek is uitgefaseerd voor nu. De HTML werkt net zo goed. De PNG diende vooral voor mensen die niet
#   weten hoe een HTML werkt. Heb hem daarom uitgefaseerd omdat we anders twee grafieken moeten onderhouden.
# def hfreq_graphs_per_location(geoprob_pipe: GeoProbPipe, export: bool = True) -> List[plt.Figure]:
#     """ Grafiek van de overschrijdingsfrequentielijn van de waterstand per HydraNL uitvoerpunt. """
#
#     # TODO Later Should Middel: Visualiseer WBN waterstand in hfreq-plot ter bewustzijn.
#     # TODO Later Nice Middel: Visualiseer physical design point value in hfreq-plot ter bewustzijn.
#
#     export_dir = os.path.join(geoprob_pipe.visualizations.graphs.export_dir, "grafiek_hfreq")
#     os.makedirs(export_dir, exist_ok=True)
#     figures = []
#     gdf_uittredepunten = geoprob_pipe.input_data.uittredepunten.gdf
#     # hydra_nl_names = geoprob_pipe.input_data.hydra_nl_data.gdf_locations['location_name'].values.tolist()
#     gdf: GeoDataFrame = read_file(
#         geoprob_pipe.input_data.app_settings.geopackage_filepath, layer="uittredepunten")
#     hydra_nl_names = gdf['hrd_name'].unique().tolist()
#
#     for hydra_nl_name in hydra_nl_names:
#
#         # Collect data for the graph
#         fragility_values: List[FragilityValue] = geoprob_pipe.input_data.hydra_nl_data.hrd_fragility_values(
#             ref=hydra_nl_name)  # TODO: Other source
#         levels = [value.x for value in fragility_values]
#         freqs = [value.probability_of_failure for value in fragility_values]
#         uittredepunten = list(gdf_uittredepunten[gdf_uittredepunten['hrd_name'] == hydra_nl_name]['uittredepunt_id'])
#
#         # Create the graph
#         plt.ioff()
#         fig = plt.figure(figsize=(8, 5))
#         ax= fig.add_subplot(111)
#         ax.plot(levels, freqs, marker='o', linestyle='-', color='blue',markersize=1)
#         ax.set_xscale("linear")  # belasting vaak lineair
#         ax.set_yscale("log")     # faalkans logaritmisch
#         ax.set_xlabel("Waterstand (m+NAP)")
#         ax.set_ylabel("Overschrijdingsfrequentie (log-schaal)")
#         ax.set_title(f"HydraNL locatie: {hydra_nl_name}\n"
#                      f"behorend bij uittredepunten: " + ", ".join([str(u) for u in uittredepunten]))
#         ax.grid(True, which="both", linestyle='--', linewidth=0.5)
#         fig.tight_layout()
#         figures.append(fig)
#
#         # Export or not?
#         export_path = os.path.join(export_dir, f"{hydra_nl_name}_hfreq.png")
#         if export:
#             plt.savefig(export_path)
#             plt.close(fig)
#
#     return figures


class GraphHFreqSingleInteractive:

    def __init__(self, geoprob_pipe: GeoProbPipe, export: bool = False):

        # Check if there are fragility curves referenced:
        conn = sqlite3.connect(geoprob_pipe.input_data.app_settings.geopackage_filepath)
        df_parameter_invoer = read_sql("SELECT * FROM parameter_invoer;", conn)
        fragility_values_refs = df_parameter_invoer['fragility_values_ref'].unique()
        conn.close()
        if (fragility_values_refs.__len__() == 0 or
                (fragility_values_refs.__len__() == 1 and fragility_values_refs[0] == '')):
            return  # No graphs needed

        # Helper parameters
        self.max_level: float = -999
        self.min_level: float = 999
        self.max_p: float = 0.0
        self.min_p: float = 1.0

        # Class-wide used
        self.geoprob_pipe = geoprob_pipe
        self.df_parameter_input_expanded: DataFrame = run_expand_input_tables(
            geopackage_filepath=self.geoprob_pipe.input_data.app_settings.geopackage_filepath, add_frag_ref=True)
        self.df_fragility_ref_data: DataFrame = self._collect_fragility_ref_data()
        if self.df_fragility_ref_data.__len__() == 0:
            return  # No fragility values, then no graphs needed

        # Logic
        self.fig = go.Figure()
        self._add_ondergrens()
        self._add_signaleringswaarde()
        self._add_dummy_physical_value_legend_marker()
        self._add_overschrijdingsfrequentielijnen()
        self._add_physical_values()
        self._update_layout()
        self._optionally_export(export=export)

    def _collect_fragility_ref_data(self) -> DataFrame:

        # Transform parameter_input dictionary to columns (added columns will be: fragility_values and fragility_ref)
        df = self.df_parameter_input_expanded
        df = df[df["parameter_name"] == "buitenwaterstand"]
        df = concat([df.drop(columns=['parameter_input']), df['parameter_input'].apply(Series)], axis=1)
        # print(f"{df.__len__()=}")
        # print(f"{df.columns=}")
        # print(f"{df=}")

        # If fragility_values_ref not in columns, then there are no fragility values needed
        if "fragility_values_ref" not in df.columns:
            return DataFrame(
                data=[],
                columns=["uittredepunt_id", "fragility_values", "uittredepunt_ids_multiline", "frequency_line"]
            )

        # Group uittredepunt ids and fragility values
        df_result = (
            df.groupby('fragility_values_ref').agg({
                'uittredepunt_id': lambda x: ', '.join(map(str, x)),  # concatenate IDs
                'fragility_values': 'first'  # keep the first list (since all are equal per ref)
            }).reset_index())
        df_result = df_result.rename(columns={"uittredepunt_id": "uittredepunt_ids"})

        # Create multiline item for uittredepunten ids
        df_result['uittredepunt_ids_multiline'] = ""
        df_result['frequency_line'] = ""
        for index, row in df_result.iterrows():

            # Uittredepunt ids multiline
            arr = row['uittredepunt_ids'].split(", ")
            lines = [', '.join(arr[i:i + 5]) for i in range(0, len(arr), 5)]
            df_result.loc[index, 'uittredepunt_ids_multiline'] = '<br>'.join(lines)

            # Create frequency line
            fragility_values = df_result.loc[index, 'fragility_values']
            levels = [item.x for item in fragility_values]
            exceedance_frequencies = [item.probability_of_failure for item in fragility_values]
            # noinspection PyUnresolvedReferences
            df_result.loc[index, 'frequency_line'] = pydra.core.datamodels.frequency_line.FrequencyLine(
                level=levels, exceedance_frequency=exceedance_frequencies)

        return df_result

    def _collect_used_fragility_refs(self) -> List[str]:
        df = self.df_parameter_input_expanded
        df = df[df["parameter_name"] == "buitenwaterstand"]

        # Transform parameter_input dictionary to columns (added columns will be: fragility_values and fragility_ref)
        df = concat([df.drop(columns=['parameter_input']), df['parameter_input'].apply(Series)], axis=1)

        return df['fragility_values_ref'].unique()

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

    def _get_fragility_values_ref_data(self, ref: str):
        df = self.df_fragility_ref_data
        df = df[df['fragility_values_ref'] == ref]
        return (df['fragility_values'].iloc[0],
                df['frequency_line'].iloc[0],
                [int(item) for item in df['uittredepunt_ids'].iloc[0].replace(" ", "").split(",")],
                df['uittredepunt_ids_multiline'].iloc[0])

    def _add_overschrijdingsfrequentielijnen(self):

        for index, fragility_values_ref in enumerate(self.df_fragility_ref_data["fragility_values_ref"].unique()):

            # Collect data for the graph
            fragility_values, _, uittredepunten, uittredepunten_multiline = self._get_fragility_values_ref_data(
                ref=fragility_values_ref)
            levels = [item.x for item in fragility_values]
            self.max_level = max(self.max_level, max(levels))
            self.min_level = min(self.min_level, min(levels))
            freqs = [item.probability_of_failure for item in fragility_values]
            self.max_p = max(self.max_p, max(freqs))
            self.min_p = min(self.min_p, min(freqs))

            # Only first overschrijdingsfrequentielijn should be visible at first
            visible = 'legendonly'
            if index == 0:
                visible = True

            # Add lines
            legend_name = f"{fragility_values_ref}<br>uittredepunten: <br>{uittredepunten_multiline}"
            self.fig.add_trace(go.Scatter(
                x=levels, y=freqs, mode='lines', name=legend_name, legendgroup=legend_name, visible=visible,
                line=dict(dash='dash', color='blue', width=1.5), showlegend=True))

    def _add_physical_values(self):

        for index, fragility_values_ref in enumerate(self.df_fragility_ref_data["fragility_values_ref"].unique()):

            # Collect data for the graph
            _, freq_line, uittredepunten, uittredepunten_multiline = self._get_fragility_values_ref_data(
                ref=fragility_values_ref)

            # Only first overschrijdingsfrequentielijn should be visible at first
            visible = 'legendonly'
            if index == 0:
                visible = True

            # Get physical values
            legend_name = f"{fragility_values_ref}<br>uittredepunten: <br>{uittredepunten_multiline}"
            df = self.geoprob_pipe.results.df_alphas_influence_factors_and_physical_values(
                filter_deterministic=False, filter_derived=True)
            df = df[df['variable'] == 'buitenwaterstand']
            df = df[df['uittredepunt_id'].isin(uittredepunten)]

            # Scenario may have no uittredepunt connections, then no physical values need to be added
            if df.__len__() == 0:
                return

            levels = df['physical_value'].values
            self.max_level = max(self.max_level, levels.max())
            self.min_level = min(self.min_level, levels.min())
            frequencies = [freq_line.interpolate_level(level) for level in levels]
            self.max_p = max(self.max_p, max(frequencies))
            self.min_p = min(self.min_p, min(frequencies))

            # Add markers
            self.fig.add_trace(go.Scatter(
                x=levels, y=frequencies, mode='markers', visible=visible, showlegend=False, legendgroup=legend_name,
                marker=dict(color='LightSkyBlue', size=10, line=dict(color='black', width=1))))

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
                title=f"Waterstand (m+NAP)", type='linear', showgrid=True, gridwidth=0.5, gridcolor="gray",
                range=[self.min_level - xaxis_add, self.max_level + xaxis_add]),
            yaxis=dict(
                title=f"Overschrijdingsfrequentie (log-schaal)", type='log', showgrid=True, tickformat=".0e",
                gridwidth=1.0, tickvals=y_ticks, ticktext=y_ticks_text, tickmode='array', gridcolor="gray",
                minor=dict(
                    showgrid=True, dtick="D1", gridwidth=0.5, gridcolor='rgb(199, 197, 193)')))

    def _optionally_export(self, export: bool = False, add_timestamp: bool = False):
        if not export:
            return
        export_dir = self.geoprob_pipe.visualizations.graphs.export_dir
        os.makedirs(export_dir, exist_ok=True)
        timestamp_str = ""
        if add_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
            timestamp_str = f"{timestamp}_"
        self.fig.write_html(os.path.join(export_dir, f"{timestamp_str}hfreq.html"), include_plotlyjs='cdn')
        # if self.geoprob_pipe.software_requirements.chrome_is_installed:
        #     self.fig.write_image(os.path.join(export_dir, f"{timestamp_str}hfreq.png"), format="png")
        # Note CP: Export van PNG uitgezet. Meerwaarde beperkt denk ik aangezien je de HTML al hebt.
