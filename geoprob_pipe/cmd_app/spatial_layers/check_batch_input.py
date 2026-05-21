from __future__ import annotations

from typing import TYPE_CHECKING
from geoprob_pipe.cmd_app.utils.batch_input import batch_inquiry

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings

# TODO Vincent: Voeg een check aan de metadata toe of dit gevraagd moet worden.
# Eerste keer en als de input veranderd moet worden.
def check_batch_input(app_settings: ApplicationSettings):
    batch_inquiry(app_settings=app_settings)
    return True