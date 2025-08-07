from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from geoprob_pipe.visualizations.other.flowchart_overview_beta_results.logic import flowchart_overview_beta_results
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

    def flowchart_overview_beta_results(
            self, uittredepunt_id: Optional[int] = None, ondergrondscenario_id: Optional[int] = None) -> str:
        return flowchart_overview_beta_results(
            geoprob_pipe=self.geoprob_pipe, export=False,
            uittredepunt_id=uittredepunt_id, ondergrondscenario_id=ondergrondscenario_id)

    def export_all_other_visualizations(self):
        flowchart_overview_beta_results(geoprob_pipe=self.geoprob_pipe, export=True)
