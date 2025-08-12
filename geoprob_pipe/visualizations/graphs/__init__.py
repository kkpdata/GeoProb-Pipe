from __future__ import annotations
from geoprob_pipe.visualizations.graphs.betrouwbaarheidsindex_oud import beta_uittredepunten_graph, beta_scenarios_graph
from geoprob_pipe.visualizations.graphs.hfreq import GraphHFreqSingleInteractive, hfreq_graphs_per_location
from geoprob_pipe.visualizations.graphs.physical_values_along_levee import physical_values_buitenwaterstand_and_top_zand
from typing import TYPE_CHECKING, List
from matplotlib.pyplot import Figure as MatplotLibFigure
from plotly.graph_objects import Figure as PlotlyFigure
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

    def hfreq_graph_in_single_interactive(self, export: bool = False) -> PlotlyFigure:
        graph = GraphHFreqSingleInteractive(self.geoprob_pipe, export=export)
        return graph.fig

    def physical_values_buitenwaterstand_and_top_zand(self, export: bool = False) -> PlotlyFigure:
        return physical_values_buitenwaterstand_and_top_zand(self.geoprob_pipe, export=export)

    def hfreq_graphs_per_location(self) -> List[MatplotLibFigure]:
        return hfreq_graphs_per_location(self.geoprob_pipe, export=False)

    def beta_scenarios(self) -> MatplotLibFigure:
        return beta_scenarios_graph(self.geoprob_pipe, export=False)

    def beta_uittredepunten(self) -> MatplotLibFigure:
        return beta_uittredepunten_graph(self.geoprob_pipe, export=False)

    def export_graphs(self):
        GraphHFreqSingleInteractive(self.geoprob_pipe, export=True)
        hfreq_graphs_per_location(self.geoprob_pipe, export=True)
        beta_scenarios_graph(self.geoprob_pipe, export=True)  # TODO Tijdelijk uitgezet: in progress
        beta_uittredepunten_graph(self.geoprob_pipe, export=True)  # TODO Tijdelijk uitgezet: in progress
        self.physical_values_buitenwaterstand_and_top_zand(export=True)
