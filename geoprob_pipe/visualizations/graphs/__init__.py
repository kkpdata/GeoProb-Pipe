from __future__ import annotations
from geoprob_pipe.visualizations.graphs.combined import Combined
from typing import TYPE_CHECKING
import os
from geoprob_pipe.visualizations.graphs.combined.hfreq import hfreq
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


class Graphs:

    def __init__(self, app_obj: GeoProbPipe):
        self.geoprob_pipe = app_obj
        self.combined = Combined(app_obj)

    @property
    def export_dir(self) -> str:
        path = os.path.join(self.geoprob_pipe.visualizations.export_dir, "graphs")
        os.makedirs(path, exist_ok=True)
        return path

    def export_graphs(self):

        fig = self.combined.betrouwbaarheidsindex()
        export_path = os.path.join(self.export_dir, f"B_STPH_sc.png")
        fig.savefig(export_path, dpi=300)

        export_hfreq_graphs(self.geoprob_pipe)
