from pathlib import Path

import pandas as pd

from app.classes.base_collection import BaseCollection


class Vak:
    
    def __init__(self, df_row: pd.Series) -> None:
        
        # Initialize attributes which will be filled later
        self.uittredepunten = []  # Filled in the UittredepuntCollection class and shows all Uittredepunten in this Vak
        self.ondergrond_scenarios = []  # Filled in the OndergrondScenarioCollection class and shows all OndergrondScenarios in this Vak
        
        # Set values from Excel row as attributes of the Vak instance
        for col, value in df_row.items():
            attr_name = str(col).lower()  # Enforce lowercase attribute name to avoid case sensitivity issues

            # Custom mapping of attribute names
            if attr_name == "vak_id":
                # Rename vak_id to id to simplify the attribute name
                attr_name = "id"

            # Check if attribute already exists
            if hasattr(self, attr_name):
                raise AttributeError(f"{self.__class__.__name__} already has an attribute named '{attr_name}', please rename the column in the input Excel file.")
            
            setattr(self, attr_name, value) 

    def __repr__(self) -> str:
        return f"Vak(id={self.id})"

        
class VakCollection(BaseCollection[Vak]):
    def __init__(self, path_input_xlsx=Path) -> None:
        super().__init__()
        
        # Read Excel, strip trailing whitespace, and convert to lowercase
        # Note: the 2nd row is skipped because it contains the units of the variables, which is not needed in the code
        self.df = pd.read_excel(path_input_xlsx, sheet_name="Vakken", skiprows=[1]).rename(columns=lambda x: x.strip().lower())

        # Create vakken from df
        for _, row in self.df.iterrows():
            vak = Vak(row)
            
            # Check for duplicate vak_id before adding Vak to collection
            if vak.id in self._items:
                raise ValueError(f"Duplicate vak_id {vak.id} found")
            
            self.add(vak.id, vak)




