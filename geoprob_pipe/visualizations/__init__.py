from __future__ import annotations
from typing import TYPE_CHECKING
from geoprob_pipe.visualizations.graphs import Graphs
from geoprob_pipe.visualizations.other import Other
import os
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


class Visualizations:

    def __init__(self, geoprob_pipe: GeoProbPipe):
        self.geoprob_pipe = geoprob_pipe
        self.graphs = Graphs(geoprob_pipe)
        self.other = Other(geoprob_pipe)

    @property
    def export_dir(self) -> str:
        path = os.path.join(self.geoprob_pipe.workspace.path_output_folder.folderpath, "visualizations")
        os.makedirs(path, exist_ok=True)
        return path

    def export_visualizations(self):
        self.graphs.export_graphs()
        self.other.export_all_other_visualizations()
