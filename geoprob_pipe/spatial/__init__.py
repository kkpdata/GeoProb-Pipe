from __future__ import annotations
from typing import TYPE_CHECKING
from geoprob_pipe.spatial.gdf_beta_limit_states import (
    get_gdf_beta_limit_states, get_gdf_beta_scenarios)
from geopandas import GeoDataFrame
import os
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


class Spatial:

    def __init__(self, geoprob_pipe: GeoProbPipe):
        self.geoprob_pipe = geoprob_pipe

    def get_gdf_beta_limit_states(self, export: bool = False) -> GeoDataFrame:
        return get_gdf_beta_limit_states(self.geoprob_pipe, export=export)

    def get_gdf_beta_scenarios(self, export: bool = False) -> GeoDataFrame:
        return get_gdf_beta_scenarios(self.geoprob_pipe, export=export)

    @property
    def export_dir(self) -> str:
        return self.geoprob_pipe.workspace.path_output_folder.folderpath

    @property
    def export_path_geopackage(self):
        return os.path.join(self.export_dir, "spatial_data.gpkg")

    def export_geopackage(self):
        self.get_gdf_beta_limit_states(export=True)
        self.get_gdf_beta_scenarios(export=True)
        self.geoprob_pipe.results.gdf_beta_uittredepunten.to_file(
            self.geoprob_pipe.spatial.export_path_geopackage, layer="beta_uittredepunten", driver="GPKG")
