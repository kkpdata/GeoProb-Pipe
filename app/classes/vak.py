from pathlib import Path

import pandas as pd

from app.classes.base_collection import BaseCollection
from app.helper_functions.data_validation import (
    attribute_already_exists,
    check_required_columns,
    enforce_lower_upper_bounds,
)


class Vak:
    
    def __init__(self, df_row: pd.Series, df_variable_overview: pd.DataFrame) -> None:
        
        # Initialize attributes which will be filled later
        self.uittredepunten = []  # Filled in the UittredepuntCollection class and shows all Uittredepunten in this Vak
        self.ondergrond_scenarios = []  # Filled in the OndergrondScenarioCollection class and shows all OndergrondScenarios in this Vak
        
        # Set values from Excel row as attributes of the Vak instance
        for col, value in df_row.items():
            attr_name = str(col)  # Make sure the attribute name is a string (just in case it's interpreted in a wrong format)

            # Perform data validation
            attribute_already_exists(self, attr_name)
            enforce_lower_upper_bounds(attr_name, value, df_variable_overview)

            # Custom mapping of attribute names (if needed)
            if attr_name == "vak_id":
                # Rename vak_id to id to simplify the attribute name
                attr_name = "id"

            # Set attribute dynamically
            setattr(self, attr_name, value)

    def __repr__(self) -> str:
        return f"Vak(id={self.id})"

        
class VakCollection(BaseCollection[Vak]):
    def __init__(self, path_input_xlsx: Path, df_variable_overview: pd.DataFrame) -> None:
        super().__init__()
        
        # Read Excel, strip trailing whitespace
        self.df = pd.read_excel(path_input_xlsx, sheet_name="Vakken").rename(columns=lambda x: x.strip())

        # Data validation
        check_required_columns(self, self.df)

        # Create vakken from df
        for _, row in self.df.iterrows():
            vak = Vak(row, df_variable_overview)
            
            # Check for duplicate vak_id before adding Vak to collection
            if vak.id in self._items:
                raise ValueError(f"Duplicate vak_id {vak.id} found")
            
            self.add(str(vak.id), vak)




