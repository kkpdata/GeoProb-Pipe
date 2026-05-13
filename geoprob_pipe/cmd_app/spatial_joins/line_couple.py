from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

import geopandas as gpd

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


class BaseShapeCouple:
    
    def __init__(self, app_settings: ApplicationSettings, param: str) -> None:
        self.app_settings = app_settings
        self.param = param
        conn = sqlite3.connect(app_settings.geopackage_filepath)
        cur = conn.cursor()
        cur.execute(
            "SELECT metadata_value FROM geoprob_pipe_metadata WHERE metadata_type = ?",
            ("ruimtelijke_scenarios",),
        )
        self.scenarios: list[str] = cur.fetchone()[0].split(", ")
        conn.close()

    def couple_exit_points(self):
        # Read uittredepunten
        gdf_exit_points: gpd.GeoDataFrame = gpd.read_file(
            self.app_settings.geopackage_filepath, layer="uittredepunten"
        )
        
        # Read lijn met parameter:
        gdf_parameter: gpd.GeoDataFrame = gpd.read_file(
            self.app_settings.geopackage_filepath, layer=f"{self.param}"
        )
        
        # join
        gdf_input = gdf_exit_points.sjoin_nearest(
            gdf_parameter[["geometry", f"{self.param}"]], how='left', distance_col='distance'
        )
        gdf_input = gdf_input[["uitredepunt_id", f"{self.param}"]]
        gdf_input = gdf_input.rename({f"{self.param}": "mean"})
        
        # Add to gis_join_parameter_invoer
        # TODO add all of the parts of a parameter input
        pass
