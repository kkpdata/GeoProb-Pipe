from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from app.classes.base_collection import BaseCollection
from app.classes.vak import VakCollection


class OndergrondScenario:
    
    def __init__(self, df_row: pd.Series, vak: Vak) -> None:  # type: ignore

        self.vak = vak  # Link the corresponding Vak instance to this OndergrondScenario instance
        
        # Set values from Excel row as attributes of the OndergrondScenario instance
        for col, value in df_row.items():
            attr_name = str(col).lower()  # Enforce lowercase attribute name to avoid case sensitivity issues
            
            # Custom mapping of attribute names
            if attr_name == "scenario_id":
                # Rename scenario_id to id to simplify the attribute name
                attr_name = "id"

            # Check if attribute already exists
            if hasattr(self, attr_name):
                raise AttributeError(f"{self.__class__.__name__} already has an attribute named '{attr_name}', please rename the column in the input Excel file.")
            
            setattr(self, attr_name, value)        

    def __repr__(self) -> str:
        return f"OndergrondScenario(id={self.id}, scenario_probability={self.scenariokans}, valid={self.vak.id})"
    
    
class OndergrondScenarioCollection(BaseCollection[OndergrondScenario]):
    def __init__(self, path_input_xlsx: Path, vak_collection: VakCollection) -> None:
        super().__init__()  # Initialize the base collection
        
        # Read Excel, strip trailing whitespace, and convert to lowercase
        # Note: the 2nd row is skipped because it contains the units of the variables, which is not needed in the code
        self.df = pd.read_excel(path_input_xlsx, sheet_name="Ondergrondscenarios", skiprows=[1]).rename(columns=lambda x: x.strip().lower())
        
        # Create ondergrondscenarios from df. Note that the created OndergrondScenario is linked to the corresponding Vak
        for _, row in self.df.iterrows():
            
            ondergrondscenario_id = row["scenario_id"]

            # Perform checks
            try:
                vak = vak_collection[row["vak_id"]]
            except KeyError:
                # If the vak_id is not found in the vak_collection, raise an error
                raise KeyError(f"Vak '{row["vak_id"]}' (corresponding to scenario '{ondergrondscenario_id}') not found in VakCollection")        

            if any(punt.id == ondergrondscenario_id for punt in vak.ondergrond_scenarios):
                # Check for duplicate scenario_id within the same Vak
                raise ValueError(f"Duplicate scenario_id: scenario '{ondergrondscenario_id}' already exists in vak '{vak.id}'")            
            
            scenario = OndergrondScenario(df_row=row, vak=vak)
            vak.ondergrond_scenarios.append(scenario)
            self.add(scenario.id, scenario)