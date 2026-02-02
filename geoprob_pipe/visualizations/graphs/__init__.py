from __future__ import annotations
from geoprob_pipe.visualizations.graphs.betrouwbaarheidsindex import ( 
    GraphBetaValuesSingleInteractive,
    beta_uittredepunten_graph, beta_scenarios_graph, beta_vakken_graph)
from geoprob_pipe.visualizations.graphs.hfreq import GraphHFreqSingleInteractive
from geoprob_pipe.visualizations.graphs.assemblage_icicle import IciclePlot
from geoprob_pipe.visualizations.graphs.physical_values_along_levee import physical_values_buitenwaterstand_and_top_zand
from geoprob_pipe.visualizations.graphs.invloedsfactoren import invloedsfactoren
from geoprob_pipe.visualizations.graphs.phreatic_waterline import phreatic_waterline
from geoprob_pipe.visualizations.graphs.overview_alpha import overview_alpha
from geoprob_pipe.visualizations.graphs.river_waterlevel import river_waterlevel
from typing import TYPE_CHECKING
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

    def invloedsfactoren(self, export: bool = False) -> PlotlyFigure:
        return invloedsfactoren(self.geoprob_pipe, export=export)

    def physical_values_buitenwaterstand_and_top_zand(self, export: bool = False) -> PlotlyFigure:
        return physical_values_buitenwaterstand_and_top_zand(self.geoprob_pipe, export=export)

    def beta_value_in_single_interactive(self, export: bool = False) -> PlotlyFigure:
        graph = GraphBetaValuesSingleInteractive(self.geoprob_pipe, export=export)
        return graph.fig

    def beta_scenarios(self) -> PlotlyFigure:
        return beta_scenarios_graph(self.geoprob_pipe, export=False)

    def beta_uittredepunten(self) -> PlotlyFigure:
        return beta_uittredepunten_graph(self.geoprob_pipe, export=False)

    def beta_vakken(self) -> PlotlyFigure:
        return beta_vakken_graph(self.geoprob_pipe, export=False)

    def phreatic_waterline(self) -> PlotlyFigure:
        return phreatic_waterline(self.geoprob_pipe, export=False)

    def overview_alpha(self) -> PlotlyFigure:
        return overview_alpha(self.geoprob_pipe, export=False)

    def river_waterlevel(self) -> PlotlyFigure:
        return river_waterlevel(self.geoprob_pipe, export=False)

    def icicle_assemblage(self) -> PlotlyFigure:
        graph = IciclePlot(self.geoprob_pipe, export=False)
        return graph.fig

    def export_graphs(self):
        GraphHFreqSingleInteractive(self.geoprob_pipe, export=True)
        GraphBetaValuesSingleInteractive(self.geoprob_pipe, export=True)
        IciclePlot(self.geoprob_pipe, export=True)
        beta_scenarios_graph(self.geoprob_pipe, export=True)
        beta_uittredepunten_graph(self.geoprob_pipe, export=True)
        beta_vakken_graph(self.geoprob_pipe, export=True)
        self.physical_values_buitenwaterstand_and_top_zand(export=True)
        self.invloedsfactoren(export=True)
        phreatic_waterline(self.geoprob_pipe, export=True)
        overview_alpha(self.geoprob_pipe, export=True)
        river_waterlevel(self.geoprob_pipe, export=True)
