from __future__ import annotations
from geoprob_pipe.visualizations.graphs.betrouwbaarheidsindex import beta_scenarios_graph
from geoprob_pipe.visualizations.graphs.betrouwbaarheidsindex import beta_uittredepunten_graph
from geoprob_pipe.visualizations.graphs.hfreq import hfreq_graphs
from typing import TYPE_CHECKING, List
from matplotlib.pyplot import Figure
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

    def hfreq(self) -> List[Figure]:
        return hfreq_graphs(self.geoprob_pipe, export=False)

    def beta_scenarios(self) -> Figure:
        return beta_scenarios_graph(self.geoprob_pipe, export=False)

    def beta_uittredepunten(self) -> Figure:
        return beta_uittredepunten_graph(self.geoprob_pipe, export=False)

    def export_graphs(self):
        hfreq_graphs(self.geoprob_pipe, export=True)
        beta_scenarios_graph(self.geoprob_pipe, export=True)
        beta_uittredepunten_graph(self.geoprob_pipe, export=True)
