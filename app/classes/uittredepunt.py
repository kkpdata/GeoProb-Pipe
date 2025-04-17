from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd


class UittredepuntCollection:
    
    def __init__(self, path_input_xlsx=Path) -> None:
        self.df = pd.read_excel(path_input_xlsx, sheet_name="Uittredepunten")

class Uittredepunt:
    
    def __init__(self, vak: Vak, locatie) -> None:  # type: ignore
        self.vak = vak
        self.locatie = locatie


    def __repr__(self) -> str:
        return f"Uittredepunt(locatie={self.locatie}, vak={self.vak.naam})"


