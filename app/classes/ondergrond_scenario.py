from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd


class OndergrondScenarioCollection:
    
    def __init__(self, path_input_xlsx=Path) -> None:
        self.df = pd.read_excel(path_input_xlsx, sheet_name="Ondergrondscenarios")


class OndergrondScenario:
    
    def __init__(self, vak: Vak, naam, scenario) -> None:  # type: ignore
        self.vak = vak
        self.naam = naam
        self.scenario = scenario

    def __repr__(self) -> str:
        return f"OndergrondScenario(naam={self.naam}, scenario={self.scenario})"