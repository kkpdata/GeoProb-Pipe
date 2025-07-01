from __future__ import annotations
from geoprob_pipe.graphs.combined.betrouwbaarheidsindex import betrouwbaarheidsindex
from typing import TYPE_CHECKING
from matplotlib.pyplot import Figure as MatplotLibFigure
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


class Combined:

    def __init__(self, app_obj: GeoProbPipe):
        self.app_obj: GeoProbPipe = app_obj

    def betrouwbaarheidsindex(self) -> MatplotLibFigure:
        return betrouwbaarheidsindex(self.app_obj)

