from pathlib import Path

import pandas as pd

from app.classes.base_collection import BaseCollection
from app.classes.vak import Vak, VakCollection
from app.helper_functions.data_validation import (
    attribute_already_exists,
    check_required_columns,
    enforce_lower_upper_bounds,
)


class OndergrondScenario:
    
    def __init__(self, df_row: pd.Series, vak: Vak, df_variable_overview: pd.DataFrame) -> None:

        self.vak = vak  # Link the corresponding Vak instance to this OndergrondScenario instance
        
        # Set values from Excel row as attributes of the OndergrondScenario instance
        for col, value in df_row.items():
            attr_name = str(col)  # Make sure the attribute name is a string (just in case it's interpreted in a wrong format)
            
            # Perform data validation
            attribute_already_exists(self, attr_name)
            enforce_lower_upper_bounds(attr_name, value, df_variable_overview)
            
            # Custom mapping of attribute names (if needed)
            if attr_name == "ondergrondscenario_id":
                # Rename ondergrondscenario_id to id to simplify the attribute name
                attr_name = "id"

            # Set attribute dynamically
            setattr(self, attr_name, value)        

    def __repr__(self) -> str:
        return f"OndergrondScenario(id={self.id})"
    
    
class OndergrondScenarioCollection(BaseCollection[OndergrondScenario]):
    def __init__(self, path_input_xlsx: Path, vak_collection: VakCollection, df_variable_overview: pd.DataFrame) -> None:
        super().__init__()  # Initialize the base collection
        
        # Read Excel, strip trailing whitespace. Also, unused ondergrondscenario's (ondergrondscenario_kans=Nan or ondergrondscenario_kans=0) are removed
        self.df = pd.read_excel(path_input_xlsx, sheet_name="Ondergrondscenarios").rename(columns=lambda x: x.strip()).dropna(subset=['ondergrondscenario_kans']).loc[lambda x: x['ondergrondscenario_kans'] != 0]

        # Data validation
        check_required_columns(self, self.df)

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
            
            scenario = OndergrondScenario(row, vak, df_variable_overview)
            vak.ondergrond_scenarios.append(scenario)
            self.add(str(scenario.id), scenario)