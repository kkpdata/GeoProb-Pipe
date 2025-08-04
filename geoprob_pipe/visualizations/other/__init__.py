from __future__ import annotations
from typing import TYPE_CHECKING
from pandas import DataFrame
from geoprob_pipe.visualizations.other.overview.generate_flow_chart_v2 import export_flowchart_overview_beta_results
import os
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


class Other:

    def __init__(self, app_obj: GeoProbPipe):
        self.geoprob_pipe = app_obj

    @property
    def export_dir(self) -> str:
        path = os.path.join(self.geoprob_pipe.visualizations.export_dir, "other")
        os.makedirs(path, exist_ok=True)
        return path

    def export_flowchart_overview_beta_results(self):
        export_flowchart_overview_beta_results(geoprob_pipe=self.geoprob_pipe)

    def export_all_other_visualizations(self):
        self.export_flowchart_overview_beta_results()
