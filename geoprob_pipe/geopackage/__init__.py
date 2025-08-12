from __future__ import annotations
from typing import TYPE_CHECKING
from geoprob_pipe.geopackage.gdf_beta_limit_states import (
    get_gdf_beta_limit_states, get_gdf_beta_scenarios, get_gdf_beta_uittredepunten)
from geopandas import GeoDataFrame
import os
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


class GeoPackage:

    def __init__(self, geoprob_pipe: GeoProbPipe):
        self.geoprob_pipe = geoprob_pipe

    def get_gdf_beta_limit_states(self, export: bool = False) -> GeoDataFrame:
        return get_gdf_beta_limit_states(self.geoprob_pipe, export=export)

    def get_gdf_beta_scenarios(self, export: bool = False) -> GeoDataFrame:
        return get_gdf_beta_scenarios(self.geoprob_pipe, export=export)

    def get_gdf_beta_uittredepunten(self, export: bool = False) -> GeoDataFrame:
        return get_gdf_beta_uittredepunten(self.geoprob_pipe, export=export)

    @property
    def export_dir(self) -> str:
        return self.geoprob_pipe.workspace.path_output_folder.folderpath

    @property
    def export_path(self):
        return os.path.join(self.export_dir, "spatial_data.gpkg")

    def export_gdb(self):
        self.get_gdf_beta_limit_states(export=True)
        self.get_gdf_beta_scenarios(export=True)
        self.get_gdf_beta_uittredepunten(export=True)
