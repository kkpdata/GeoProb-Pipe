from __future__ import annotations
from typing import TYPE_CHECKING
from pandas import DataFrame
import os
from typing import Optional
from geopandas import GeoDataFrame, read_file
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

    def _add_traject_level_data(self, fig: go.Figure, parameter_name: str) -> go.Figure:
        df_filter = self.df_parameter_invoer[
            (self.df_parameter_invoer['parameter'] == parameter_name) &
            (self.df_parameter_invoer['scope'] == 'traject')]
        mean = df_filter.iloc[0]['mean']
        fig.add_trace(go.Scatter(
            x=[self.x_min, self.x_max, self.x_max, self.x_min],
            y=[self.y_min, self.y_min, mean, mean],
            fill='toself',
            mode='lines',
            fillcolor='lightblue',
            name="Traject-niveau",
            showlegend=True,
            line=dict(width=0),
            opacity=0.5,
        ))
        return fig

    def _create_figures(self):
        export_dir = os.path.join(self.app_settings.workspace_dir, "parameter_input_process")
        os.makedirs(export_dir, exist_ok=True)

        for parameter_name in self.df_parameter_invoer['parameter'].unique():

            # Initiate figure
            fig = go.Figure()

            # Add geospatial-level
            # TODO

            # Add traject-level
            fig = self._add_traject_level_data(fig=fig, parameter_name=parameter_name)

            # Add vak-level
            # TODO

            # Add vak-level per scenario
            # TODO

            # Add uittredepunten-level
            # TODO

            # Update layout
            fig.update_layout(
                title=f"Parameter invoer voor '{parameter_name}'",
                xaxis_title="Metrering [m]",
                yaxis_title="Y-as",
            )

            # Export figure
            if self.export:
                export_path = os.path.join(export_dir, f"parameter_invoer_{parameter_name}.html")
                fig.write_html(export_path, include_plotlyjs='cdn')
