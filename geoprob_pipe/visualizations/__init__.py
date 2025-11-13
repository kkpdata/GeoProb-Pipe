from __future__ import annotations
from typing import TYPE_CHECKING
from geoprob_pipe.visualizations.graphs import Graphs
import os
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


class Visualizations:

    def __init__(self, app_obj: GeoProbPipe):
        self.geoprob_pipe = app_obj
        self.graphs = Graphs(app_obj)

    @property
    def export_dir(self) -> str:
        path = os.path.join(self.geoprob_pipe.input_data.app_settings.workspace_dir, "visualizations")
        os.makedirs(path, exist_ok=True)
        return path

    def export_visualizations(self):
        self.graphs.export_graphs()
