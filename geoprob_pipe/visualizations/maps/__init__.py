from __future__ import annotations
from typing import TYPE_CHECKING
import os
from plotly.graph_objects import Figure as PlotlyFigure

from geoprob_pipe.visualizations.maps.betamap import BetaMap


if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


class Maps:

    def __init__(self, app_obj: GeoProbPipe):
        self.geoprob_pipe = app_obj

    @property
    def export_dir(self) -> str:
        path = os.path.join(self.geoprob_pipe.visualizations.export_dir, "maps")
        os.makedirs(path, exist_ok=True)
        return path

    def betamap(self, export: bool = False) -> PlotlyFigure:
        map_figure = BetaMap(self.geoprob_pipe, export=export)
        return map_figure.fig

    def export_maps(self):
        BetaMap(self.geoprob_pipe, export=True)
