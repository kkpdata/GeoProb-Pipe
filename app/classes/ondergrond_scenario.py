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
            attr_name = str(col)
            
            # Custom mapping of attribute names
            if attr_name == "ondergrondscenario_id":
                # Rename ondergrondscenario_id to id to simplify the attribute name
                attr_name = "id"

            # Check if attribute already exists
            if hasattr(self, attr_name):
                raise AttributeError(f"{self.__class__.__name__} already has an attribute named '{attr_name}', please rename the column in the input Excel file.")
            
            setattr(self, attr_name, value)        

    def __repr__(self) -> str:
        return f"OndergrondScenario(id={self.id})"
    
    
class OndergrondScenarioCollection(BaseCollection[OndergrondScenario]):
    def __init__(self, path_input_xlsx: Path, vak_collection: VakCollection) -> None:
        super().__init__()  # Initialize the base collection
        
        # Read Excel, strip trailing whitespace
        self.df = pd.read_excel(path_input_xlsx, sheet_name="Ondergrondscenarios").rename(columns=lambda x: x.strip())
        
        # Check if all required columns are present in the DataFrame
        required_columns = ['vak_id',
                            'ondergrondscenario_id',
                            'ondergrondscenario_naam',
                            'ondergrondscenario_kans',
                            'top_zand_mean',
                            'top_zand',
                            'gamma_sat_deklaag_mean',
                            'gamma_sat_deklaag_stdev',
                            'D_wvp_mean',
                            'D_wvp_stdev',
                            'kD_wvp_mean',
                            'kD_wvp_vc',
                            'k_wvp_mean',
                            'd70_mean',
                            'd70_vc']
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns in the 'Uittredepunten' sheet of the input Excel file: {', '.join(missing_columns)}")
     
        # Create ondergrondscenarios from df. Note that the created OndergrondScenario is linked to the corresponding Vak
        for _, row in self.df.iterrows():
            
            ondergrondscenario_id = row["ondergrondscenario_id"]

            # Perform checks
            try:
                vak = vak_collection[str(row["vak_id"])]
            except KeyError:
                # If the vak_id is not found in the vak_collection, raise an error
                raise KeyError(f"Vak ID '{row["vak_id"]}' (corresponding to scenario '{ondergrondscenario_id}') not found in VakCollection")        

            if any(punt.id == ondergrondscenario_id for punt in vak.ondergrond_scenarios):
                # Check for duplicate ondergrondscenario_id within the same Vak
                raise ValueError(f"Duplicate ondergrondscenario_id: scenario '{ondergrondscenario_id}' already exists in vak '{vak.id}'")            
            
            scenario = OndergrondScenario(df_row=row, vak=vak)
            vak.ondergrond_scenarios.append(scenario)
            self.add(str(scenario.id), scenario)