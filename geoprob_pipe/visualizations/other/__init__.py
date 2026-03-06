from __future__ import annotations
from typing import TYPE_CHECKING
from pandas import DataFrame
from geoprob_pipe.visualizations.other.overview.generate_flow_chart_v2 import generate_overview_flow_chart_with_betas
import os
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


class Other:

    def __init__(self, app_obj: GeoProbPipe):
        self.geoprob_pipe = app_obj

    @property
    def export_dir(self) -> str:
        path = os.path.join(self.geoprob_pipe.visualizations.export_dir, "visualizations")
        os.makedirs(path, exist_ok=True)
        return path

    def export_visualizations(self):
        df = self.geoprob_pipe.results.df_beta_scenarios_final
        lowest_beta_row: DataFrame  = df.loc[df['beta'].idxmin()]
        generate_overview_flow_chart_with_betas(
            app_obj=self.geoprob_pipe,
            export_dir=self.export_dir,
            ondergrondscenario_id=lowest_beta_row['ondergrondscenario_id'],
            uittredepunt_id=lowest_beta_row['uittredepunt_id']
        )
