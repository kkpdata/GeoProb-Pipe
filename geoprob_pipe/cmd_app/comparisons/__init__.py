from __future__ import annotations
import sqlite3
import os
from datetime import datetime
import pandas as pd
import geopandas as gpd
from plotly.graph_objects import Figure as PlotlyFigure
from geoprob_pipe.cmd_app.comparisons.beta_dumbbell import (
    dumbbell_beta, dumbbell_uplift, dumbbell_heave, dumbbell_piping)
from geoprob_pipe.cmd_app.comparisons.beta_map import (
    map_delta_beta_comparison, map_ratio_beta_comparison)


class ComparisonCollector:
    def __init__(self,
                 geopackage_filepath_1: str,
                 geopackage_filepath_2: str,
                 export_dir: str
                 ):
        self.geopackage_filepath_1 = geopackage_filepath_1
        self.geopackage_filepath_2 = geopackage_filepath_2
        self.name_1 = self.geopackage_filepath_1.split("\\")[-1].split(".")[0]
        self.name_2 = self.geopackage_filepath_2.split("\\")[-1].split(".")[0]

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        self.export_dir = os.path.join(
            export_dir, f"comparisons/{self.name_1}_{self.name_2}_{timestamp}"
            )
        os.makedirs(export_dir, exist_ok=True)

        # Placeholders
        self.df1_beta_scenarios: pd.DataFrame
        self.df1_beta_limit_states: pd.DataFrame
        self.df1_beta_uittredepunten: pd.DataFrame

        self.df2_beta_scenarios: pd.DataFrame
        self.df2_beta_limit_states: pd.DataFrame
        self.df2_beta_uittredepunten: pd.DataFrame

        self.gdf1_uittredepunten: gpd.GeoDataFrame
        self.gdf2_uittredepunten: gpd.GeoDataFrame

        # logic
        self._load_result_data_from_geopackage()
        self._load_uittredepunten_gdf()

    def _load_result_data_from_geopackage(self):

        conn_1 = sqlite3.connect(self.geopackage_filepath_1)
        conn_2 = sqlite3.connect(self.geopackage_filepath_2)

        self.df1_beta_limit_states = pd.read_sql(
            "SELECT * FROM beta_limit_states;", conn_1
            )
        self.df2_beta_limit_states = pd.read_sql(
            "SELECT * FROM beta_limit_states;", conn_2
            )
        if len(self.df1_beta_limit_states) != len(self.df2_beta_limit_states):
            raise ValueError("De beta_limit_states tables hebben niet hetzelfde formaat")

        self.df1_beta_scenarios = pd.read_sql(
            "SELECT * FROM beta_scenarios_final;", conn_1
            )
        self.df2_beta_scenarios = pd.read_sql(
            "SELECT * FROM beta_scenarios_final;", conn_2
            )
        if len(self.df1_beta_scenarios) != len(self.df2_beta_scenarios):
            raise ValueError("De beta_scenario tables hebben niet hetzelfde formaat")

        self.df1_beta_uittredepunten = pd.read_sql(
            "SELECT * FROM beta_uittredepunten;", conn_1
            )
        self.df2_beta_uittredepunten = pd.read_sql(
            "SELECT * FROM beta_uittredepunten;", conn_2
            )
        if len(self.df1_beta_uittredepunten) != len(self.df2_beta_uittredepunten):
            raise ValueError("De beta_uittredepunten tables hebben niet hetzelfde formaat")

        conn_1.close()
        conn_2.close()

    def _load_uittredepunten_gdf(self):
        self.gdf1_uittredepunten = gpd.read_file(
            self.geopackage_filepath_1,
            layer="beta_uittredepunten"
            )
        self.gdf2_uittredepunten = gpd.read_file(
            self.geopackage_filepath_2,
            layer="beta_uittredepunten"
            )
        if len(self.gdf1_uittredepunten) != len(self.gdf2_uittredepunten):
            raise ValueError("De beta_uittredepunten tables hebben niet hetzelfde formaat")
        if set(self.gdf1_uittredepunten.geometry) != set(self.gdf2_uittredepunten.geometry):
            raise ValueError("De twee sets uittredepunten hebben afwijkende geometry")

    def dumbbell_beta(self, export: bool = False) -> PlotlyFigure:
        return dumbbell_beta(self, export)

    def dumbbell_uplift(self, export: bool = False) -> list[PlotlyFigure]:
        return dumbbell_uplift(self, export)

    def dumbbell_heave(self, export: bool = False) -> list[PlotlyFigure]:
        return dumbbell_heave(self, export)

    def dumbbell_piping(self, export: bool = False) -> list[PlotlyFigure]:
        return dumbbell_piping(self, export)

    def map_delta_beta_comparison(self, export: bool = False) -> PlotlyFigure:
        return map_delta_beta_comparison(self, export)

    def map_ratio_beta_comparison(self, export: bool = False) -> PlotlyFigure:
        return map_ratio_beta_comparison(self, export)

    def create_and_export_figures(self):
        dumbbell_beta(self, export=True)
        dumbbell_uplift(self, export=True)
        dumbbell_heave(self, export=True)
        dumbbell_piping(self, export=True)
        map_delta_beta_comparison(self, export=True)
        map_ratio_beta_comparison(self, export=True)
