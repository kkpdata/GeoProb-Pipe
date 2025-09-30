from __future__ import annotations
from geoprob_pipe.pre_processing.spatial_layers.ahn import added_ahn, request_ahn
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings


def algorithm_walking_circles(app_settings: ApplicationSettings):

    if not added_ahn(app_settings=app_settings, display_added_msg=False):
        request_ahn(app_settings=app_settings)

    raise NotImplementedError(f"Walking Circles-algoritme is not niet geïmplementeerd.")
