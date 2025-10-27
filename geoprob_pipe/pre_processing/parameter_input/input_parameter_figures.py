from __future__ import annotations
from typing import TYPE_CHECKING
from pandas import DataFrame
import os
import numpy as np
from typing import Optional, Dict, Tuple, List
from geopandas import GeoDataFrame, read_file
from geoprob_pipe.utils.statistics import calc_kar_waarde_lognormal, calc_kar_waarde_normal
import plotly.graph_objects as go
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings
    from geoprob_pipe.pre_processing.parameter_input.input_parameter_tables import InputParameterTables


class InputParameterFigures:

    def __init__(self, app_settings: ApplicationSettings, tables: InputParameterTables, export: bool = False):
        self.app_settings: ApplicationSettings = app_settings
        self.tables: InputParameterTables = tables
        self.export: bool = export

        # Placeholders
        self.df_parameter_invoer: Optional[DataFrame] = None
        self.dict_vakindeling: Dict[int, Dict] = {}
        self.traject_length: Optional[float] = None
        self.x_min = 0
        self.x_max = 0  # Will be set
        self.y_min = 0
        self.y_max = 0  # Will be adjusted on each parameter

        # Perform logic
        self._gather_data()
        self._create_figures()

    def _gather_data(self):

        # Dataframe parameter invoer
        self.df_parameter_invoer = self.tables.df_parameter_invoer

        # Lengte traject
        gpkg_file_path = self.app_settings.geopackage_filepath
        gdf: GeoDataFrame = read_file(gpkg_file_path, layer="dijktraject")
        assert gdf.__len__() == 1
        self.traject_length = gdf.iloc[0].geometry.length
        self.x_max = self.traject_length

        # Vakindeling dictionary
        gdf_vakindeling: GeoDataFrame = read_file(self.app_settings.geopackage_filepath, layer="vakindeling")
        self.dict_vakindeling = gdf_vakindeling.set_index('id').to_dict(orient='index')

        # Uittredepunten dictionary
        gdf_uittredepunten: GeoDataFrame = read_file(self.app_settings.geopackage_filepath, layer="uittredepunten")
        self.dict_uittredepunten = gdf_uittredepunten.set_index('uittredepunt_id').to_dict(orient='index')

    @staticmethod
    def _get_display_values_from_row(row) -> Tuple[float, Optional[float], Optional[float]]:
        """

        :param row:
        :return: mean, 5% ondergrens, 95% bovengrens
        """

        # Deterministic
        mean_value: float = row['mean']
        if row['distribution_type'] == 'deterministic':
            return mean_value, None, None

        # Determine standard deviation
        variation = row['variation']
        deviation = row['deviation']
        deviation_value: Optional[float] = None
        if not np.isnan(deviation):
            deviation_value = deviation
        elif not np.isnan(variation):
            deviation_value = mean_value * variation
        else:
            ValueError(f"Should have either a variation or deviation. Or maybe a bug and contact the developer.")

        # Log normal
        if row['distribution_type'] == 'log_normal':
            kar_5pr = calc_kar_waarde_lognormal(mean=mean_value, sd=deviation_value, percentiel=0.05)  # TODO: Shift bepalen
            kar_95pr = calc_kar_waarde_lognormal(mean=mean_value, sd=deviation_value, percentiel=0.95)
            return mean_value, kar_5pr, kar_95pr

        # Normal
        if row['distribution_type'] == 'normal':
            kar_5pr = calc_kar_waarde_normal(mean=mean_value, std=deviation_value, percentiel=0.05)
            kar_95pr = calc_kar_waarde_normal(mean=mean_value, std=deviation_value, percentiel=0.95)
            return mean_value, kar_5pr, kar_95pr

        raise ValueError(f"Unknown distribution_type '{row['distribution_type']}'.")

    @staticmethod
    def _get_display_values_from_df(
            df: DataFrame
) -> Tuple[
        List[float],
        Optional[List[Optional[None]]],
        Optional[List[Optional[None]]],
    ]:
        """ Leest de gemiddelde en 5% en 95% karakteristieke waarden uit o.b.v. de mean en deviation. """

        mean_values = []
        kar5pr_values = []
        kar95pr_values = []

        for index, row in df.iterrows():
            print(f"{row=}")
            mean_value = row['mean']
            mean_values.append(mean_value)
            if row['distribution_type'] == 'deterministic':
                kar5pr_values.append(None)
                kar95pr_values.append(None)
                continue
            deviation_value: Optional[float] = None
            if not np.isnan(row['deviation']):
                deviation_value = row['deviation']
            elif not np.isnan(row['variation']):
                deviation_value = mean_value * row['variation']
            else:
                ValueError(f"Should have either a variation or deviation. Or maybe a bug and contact the developer.")
            if row['distribution_type'] == 'log_normal':
                kar5pr_values.append(calc_kar_waarde_lognormal(
                    mean=mean_value, sd=deviation_value, percentiel=0.05))  # TODO: Shift bepalen
                kar95pr_values.append(
                    calc_kar_waarde_lognormal(mean=mean_value, sd=deviation_value, percentiel=0.95))
                continue
            if row['distribution_type'] == 'normal':
                kar5pr_values.append(calc_kar_waarde_normal(mean=mean_value, std=deviation_value, percentiel=0.05))
                kar95pr_values.append(calc_kar_waarde_normal(mean=mean_value, std=deviation_value, percentiel=0.95))
                continue

        # mean_values: List[float] = df['mean'].values.tolist()
        # variation: List = df['variation'].values.tolist()
        # deviation: List = df['deviation'].values.tolist()
        #
        # deviation_values: List[Optional[float]] = []
        # for mean, var, dev in zip(mean_values, variation, deviation):
        #     if not np.isnan(dev):
        #         deviation_values.append(dev)
        #     elif not np.isnan(var):
        #         deviation_values.append(mean * var)
        #     else:
        #         deviation_values.append(None)

        return mean_values, kar5pr_values, kar95pr_values

    def _add_traject_level_data(self, fig: go.Figure, parameter_name: str) -> go.Figure:
        df_filter = self.df_parameter_invoer[
            (self.df_parameter_invoer['parameter'] == parameter_name) &
            (self.df_parameter_invoer['scope'] == 'traject')]
        for index, row in df_filter.iterrows():
            mean, kar_5pr, kar_95pr = self._get_display_values_from_row(row=row)

            fig.add_trace(go.Scatter(
                x=[self.x_min, self.x_max, self.x_max, self.x_min, self.x_min],
                y=[self.y_min, self.y_min, mean, mean, self.y_min],
                fill='toself',
                mode='lines',
                fillcolor='lightblue',
                name="Traject-niveau",
                legendgroup="Traject-niveau",
                showlegend=True,
                line=dict(width=1, color="rgb(0, 0, 0)"),
            ))

            # Add (possibly) kar values
            if kar_5pr:
                fig.add_trace(go.Scatter(
                    x=[self.x_min, self.x_max],
                    y=[kar_5pr, kar_5pr],
                    mode='lines',
                    name="Traject-niveau",
                    legendgroup="Traject-niveau",
                    showlegend=False,
                    line=dict(width=4, color="rgba(0, 0, 0, 1)"),
                ))
            if kar_95pr:
                fig.add_trace(go.Scatter(
                    x=[self.x_min, self.x_max],
                    y=[kar_95pr, kar_95pr],
                    mode='lines',
                    name="Traject-niveau",
                    legendgroup="Traject-niveau",
                    showlegend=False,
                    line=dict(width=4, color="rgba(0, 0, 0, 1)", dash='dot'),
                ))

        return fig

    def _add_vak_level_data(self, fig: go.Figure, parameter_name: str) -> go.Figure:
        df_filter: DataFrame = self.df_parameter_invoer[
            (self.df_parameter_invoer['parameter'] == parameter_name) &
            (self.df_parameter_invoer['scope'] == 'vak') &
            (self.df_parameter_invoer['ondergrondscenario_naam'].isna())
        ]
        show_legend_item = True

        for index, row in df_filter.iterrows():
            mean, kar_5pr, kar_95pr = self._get_display_values_from_row(row=row)
            vak_id = row['scope_referentie']
            x_min = self.dict_vakindeling[vak_id]['m_start']
            x_max = self.dict_vakindeling[vak_id]['m_end']

            # Add mean
            fig.add_trace(go.Scatter(
                x=[x_min, x_max, x_max, x_min, x_min],
                y=[self.y_min, self.y_min, mean, mean, self.y_min],
                fill='toself',
                mode='lines',
                fillcolor='orange',
                name="Vak-niveau",
                legendgroup="Vak-niveau",
                showlegend=show_legend_item,
                line=dict(width=1, color="rgba(0, 0, 0, 1)"),
            ))
            show_legend_item = False

            # Add (possibly) deviation
            if kar_5pr:
                fig.add_trace(go.Scatter(
                    x=[x_min, x_max],
                    y=[kar_5pr, kar_5pr],
                    mode='lines',
                    name="Vak-niveau",
                    legendgroup="Vak-niveau",
                    showlegend=False,
                    line=dict(width=4, color="rgba(0, 0, 0, 1)")))
            if kar_95pr:
                fig.add_trace(go.Scatter(
                    x=[x_min, x_max],
                    y=[kar_95pr, kar_95pr],
                    mode='lines',
                    name="Vak-niveau",
                    legendgroup="Vak-niveau",
                    showlegend=False,
                    line=dict(width=4, color="rgba(0, 0, 0, 1)", dash='dot')))

        return fig

    def _add_vak_level_per_scenario_data(self, fig: go.Figure, parameter_name: str) -> go.Figure:
        df_filter: DataFrame = self.df_parameter_invoer[
            (self.df_parameter_invoer['parameter'] == parameter_name) &
            (self.df_parameter_invoer['scope'] == 'vak') &
            (self.df_parameter_invoer['ondergrondscenario_naam'].notna())]
        show_legend_item = True

        for vak_id in df_filter['scope_referentie'].unique():
            df_filter2 = df_filter[df_filter['scope_referentie'] == vak_id]
            mean_values, kar_5pr_values, kar_95pr_values = self._get_display_values_from_df(df_filter2)
            max_mean = max(mean_values)
            x_min = self.dict_vakindeling[vak_id]['m_start']
            x_max = self.dict_vakindeling[vak_id]['m_end']

            # Add max mean with fill to self
            fig.add_trace(go.Scatter(
                x=[x_min, x_max, x_max, x_min, x_min],
                y=[self.y_min, self.y_min, max_mean, max_mean, self.y_min],
                fill='toself',
                mode='lines',
                fillcolor='rgb(148, 103, 189)',
                name="Vak-niveau per scenario",
                legendgroup="Vak-niveau per scenario",
                showlegend=show_legend_item,
                line=dict(width=1, color="rgba(0, 0, 0, 1)"),
            ))
            show_legend_item = False

            # Add (possibly) deviation
            for mean, kar_5pr_value, kar_95pr_value in zip(mean_values, kar_5pr_values, kar_95pr_values):
                if mean is not max_mean:
                    fig.add_trace(go.Scatter(
                        x=[x_min, x_max],
                        y=[mean, mean],
                        mode='lines',
                        name="Vak-niveau per scenario",
                        legendgroup="Vak-niveau per scenario",
                        showlegend=False,
                        line=dict(width=1, color="rgba(0, 0, 0, 1)")))
                if kar_5pr_value is not None:
                    fig.add_trace(go.Scatter(
                        x=[x_min, x_max],
                        y=[kar_5pr_value, kar_5pr_value],
                        mode='lines',
                        name="Vak-niveau per scenario",
                        legendgroup="Vak-niveau per scenario",
                        showlegend=False,
                        line=dict(width=4, color="rgba(0, 0, 0, 1)")))
                if kar_95pr_value is not None:
                    fig.add_trace(go.Scatter(
                        x=[x_min, x_max],
                        y=[kar_95pr_value, kar_95pr_value],
                        mode='lines',
                        name="Vak-niveau per scenario",
                        legendgroup="Vak-niveau per scenario",
                        showlegend=False,
                        line=dict(width=4, color="rgba(0, 0, 0, 1)", dash='dot')))

        return fig

    def _add_uittredepunt_level_data(self, fig: go.Figure, parameter_name: str) -> go.Figure:
        df_filter: DataFrame = self.df_parameter_invoer[
            (self.df_parameter_invoer['parameter'] == parameter_name) &
            (self.df_parameter_invoer['scope'] == 'uittredepunt')]
        show_legend_item_mean = True

        for index, row in df_filter.iterrows():
            mean, kar_5pr, kar_95pr = self._get_display_values_from_row(row=row)
            x_value = self.dict_uittredepunten[row['scope_referentie']]['metrering']

            # Add mean
            fig.add_trace(go.Scatter(
                x=[x_value],
                y=[mean],
                mode='markers',
                name="Uittredepunt-niveau",
                legendgroup="Uittredepunt-niveau",
                showlegend=show_legend_item_mean,
                marker=dict(color='rgba(0, 0, 0, 1)', size=10, symbol="circle"),
            ))
            show_legend_item_mean = False

            # Add (possibly) deviation
            if kar_5pr:
                fig.add_trace(go.Scatter(
                    x=[x_value, x_value],
                    y=[kar_5pr, kar_5pr],
                    mode='markers',
                    name="Uittredepunt-niveau",
                    legendgroup="Uittredepunt-niveau",
                    showlegend=False,
                    marker=dict(color='rgba(0, 0, 0, 1)', size=10, symbol="triangle-up")))
            if kar_95pr:
                fig.add_trace(go.Scatter(
                    x=[x_value, x_value],
                    y=[kar_95pr, kar_95pr],
                    mode='markers',
                    name="Uittredepunt-niveau",
                    legendgroup="Uittredepunt-niveau",
                    showlegend=False,
                    marker=dict(color='rgba(0, 0, 0, 1)', size=10, symbol="triangle-down")))

        return fig

    @staticmethod
    def _add_legend_symbols(fig: go.Figure) -> go.Figure:
        fig.add_trace(go.Scatter(
            x=[-1000, -1000],
            y=[0, 0],
            mode='lines',
            name="95% bovengrens",
            legendgroup="95% bovengrens",
            showlegend=True,
            line=dict(width=4, color="rgba(0, 0, 0, 1)", dash='dot')))
        fig.add_trace(go.Scatter(
            x=[-1000, -1000],
            y=[0, 0],
            mode='lines',
            name="5% ondergrens",
            legendgroup="5% ondergrens",
            showlegend=True,
            line=dict(width=4, color="rgba(0, 0, 0, 1)")))
        fig.add_trace(go.Scatter(
            x=[-1000, -1000],
            y=[0, 0],
            mode='markers',
            name="95% bovengrens",
            legendgroup="95% bovengrens",
            showlegend=True,
            marker=dict(color='rgba(0, 0, 0, 1)', size=10, symbol="triangle-down")))
        fig.add_trace(go.Scatter(
            x=[-1000, -1000],
            y=[0, 0],
            mode='markers',
            name="5% ondergrens",
            legendgroup="5% ondergrens",
            showlegend=True,
            marker=dict(color='rgba(0, 0, 0, 1)', size=10, symbol="triangle-up")))

        return fig

    def _create_figures(self):
        export_dir = os.path.join(self.app_settings.workspace_dir, "parameter_input_process")
        os.makedirs(export_dir, exist_ok=True)

        # TODO: Overal hovers toepassen

        for parameter_name in self.df_parameter_invoer['parameter'].unique():

            # Initiate figure
            fig = go.Figure()

            # Add geospatial-level
            # TODO

            # Add traject-level
            fig = self._add_traject_level_data(fig=fig, parameter_name=parameter_name)

            # Add vak-level
            fig = self._add_vak_level_data(fig=fig, parameter_name=parameter_name)

            # Add vak-level per scenario
            fig = self._add_vak_level_per_scenario_data(fig=fig, parameter_name=parameter_name)

            # Add uittredepunten-level
            fig = self._add_uittredepunt_level_data(fig=fig, parameter_name=parameter_name)

            # Add some legend items
            fig = self._add_legend_symbols(fig=fig)

            # Update layout
            fig.update_layout(
                title=f"Parameter invoer voor '{parameter_name}'",
                xaxis_title="Metrering [m]",
                yaxis_title="Y-as")
            fig.update_layout(xaxis=dict(range=[0, self.x_max]))

            # Export figure
            if self.export:
                export_path = os.path.join(export_dir, f"parameter_invoer_{parameter_name}.html")
                fig.write_html(export_path, include_plotlyjs='cdn')
