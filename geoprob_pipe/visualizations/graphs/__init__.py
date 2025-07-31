from __future__ import annotations
from geoprob_pipe.visualizations.graphs.betrouwbaarheidsindex import export_beta_scenarios_graph
from geoprob_pipe.visualizations.graphs.hfreq import export_hfreq_graphs
from typing import TYPE_CHECKING
import os

if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


class Graphs:

    def __init__(self, app_obj: GeoProbPipe):
        self.geoprob_pipe = app_obj

    @property
    def export_dir(self) -> str:
        path = os.path.join(self.geoprob_pipe.visualizations.export_dir, "graphs")
        os.makedirs(path, exist_ok=True)
        return path

    def export_graphs(self):

        export_hfreq_graphs(self.geoprob_pipe)
        export_beta_scenarios_graph(self.geoprob_pipe)


