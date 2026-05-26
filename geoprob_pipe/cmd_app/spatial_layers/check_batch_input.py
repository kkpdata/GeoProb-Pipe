from __future__ import annotations

from typing import TYPE_CHECKING
from geoprob_pipe.cmd_app.utils.batch_input import batch_inquiry, read_metadata

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings

def check_batch_input(app_settings: ApplicationSettings):
    if not read_metadata(app_settings=app_settings):
        return True
    batch_inquiry(app_settings=app_settings)
    return True