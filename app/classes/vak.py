from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd


class VakCollection:
    
    def __init__(self, path_input_xlsx=Path) -> None:
        self.df = pd.read_excel(path_input_xlsx, sheet_name="Vakken")
        
        # Create vakken from df
        list_vakken = []
        for _, row in self.df.iterrows():
            list_vakken.append(Vak(row))
        self.vakken = list_vakken
        
    def _link_uittredepunten(self, list_uittredepunten: [Uittredepunt]) -> None:  # type: ignore
        self.uittredepunten = list_uittredepunten


class Vak:
    
    def __init__(self, df_row: pd.Series) -> None:
        self.naam = df_row["VakID"]
        self.uittredepunten = []

    def __repr__(self) -> str:
        return f"Vak(naam={self.naam})"
