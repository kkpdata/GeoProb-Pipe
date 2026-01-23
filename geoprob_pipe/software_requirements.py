from __future__ import annotations
from plotly.graph_objects import Figure, Scatter
import os
from geoprob_pipe.utils.validation_messages import BColors
from typing import TYPE_CHECKING
from datetime import datetime
from geoprob_pipe.utils.validation_messages import ValidationMessages
import numpy as np
# noinspection PyPep8Naming
from geoprob_pipe.utils.loggers import TmpAppConsoleHandler as logger
if TYPE_CHECKING:
    from geoprob_pipe.questionnaire.cmd import ApplicationSettings


class SoftwareRequirements:

    def __init__(self, app_settings: ApplicationSettings):
        logger.info("Checking software requirements.")
        self.validation_messages = ValidationMessages(about="Checking software requirements")
        self.chrome_is_installed = self._check_chrome_is_installed(app_settings=app_settings)

    def _check_chrome_is_installed(self, app_settings: ApplicationSettings) -> bool:
        try:
            t = np.linspace(0, 10, 100)
            fig = Figure(data=Scatter(x=t, y=np.sin(t), mode='markers'))
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
            file_path = os.path.join(app_settings.workspace_dir, f"{timestamp}_test_chrome_install_figure.png")
            fig.write_image(file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except RuntimeError:
            msg = (f"Google Chrome is not installed. This is an optional requirements used for exporting "
                   f"Plotly-figures to .png. GeoProb-Pipe will skip exporting these figures to .png, but will still "
                   f"export them to .html.")
            print(BColors.WARNING, msg, BColors.ENDC)
            self.validation_messages.add_warning(msg=msg)
            return False
