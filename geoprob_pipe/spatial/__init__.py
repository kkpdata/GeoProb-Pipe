from __future__ import annotations
from typing import TYPE_CHECKING
import os
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


class Spatial:

    def __init__(self, geoprob_pipe: GeoProbPipe):
        self.geoprob_pipe = geoprob_pipe

    @property
    def export_dir(self) -> str:
        return self.geoprob_pipe.workspace.path_output_folder.folderpath

    @property
    def export_path_geopackage(self):
        return os.path.join(self.export_dir, "spatial_data.gpkg")

    def export_geopackage(self):
        self.geoprob_pipe.results.gdf_beta_limit_states.to_file(
            self.geoprob_pipe.spatial.export_path_geopackage, layer="beta_limit_states", driver="GPKG")
        self.geoprob_pipe.results.gdf_beta_scenarios.to_file(
            self.geoprob_pipe.spatial.export_path_geopackage, layer="beta_scenarios", driver="GPKG")
        self.geoprob_pipe.results.gdf_beta_uittredepunten.to_file(
            self.geoprob_pipe.spatial.export_path_geopackage, layer="beta_uittredepunten", driver="GPKG")
