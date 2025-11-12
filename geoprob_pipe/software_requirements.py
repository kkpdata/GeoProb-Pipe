from __future__ import annotations
from plotly.graph_objects import Figure, Scatter
import os
from geoprob_pipe.utils.validation_messages import BColors
from typing import TYPE_CHECKING
from datetime import datetime
from geoprob_pipe.utils.validation_messages import ValidationMessages
import numpy as np
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe




class SoftwareRequirements:

    def __init__(self, geoprob_pipe: GeoProbPipe):
        self.validation_messages = ValidationMessages(about="Checking software requirements")
        self.chrome_is_installed = self._check_chrome_is_installed(geoprob_pipe=geoprob_pipe)

    def _check_chrome_is_installed(self, geoprob_pipe: GeoProbPipe) -> bool:
        try:
            t = np.linspace(0, 10, 100)
            fig = Figure(data=Scatter(x=t, y=np.sin(t), mode='markers'))
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
            file_path = os.path.join(
                geoprob_pipe.input_data.app_settings.workspace, f"{timestamp}_test_chrome_install_figure.png")
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
