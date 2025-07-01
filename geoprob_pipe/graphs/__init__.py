from __future__ import annotations
from typing import TYPE_CHECKING
from geoprob_pipe.graphs.combined import Combined
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


class Graphs:

    def __init__(self, app_obj: GeoProbPipe):
        self.combined = Combined(app_obj)
