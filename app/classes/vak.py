from pathlib import Path

import pandas as pd

from app.classes.base_collection import BaseCollection
from app.helper_functions.data_validation import (
    check_attr_in_overview,
    check_attribute_already_exists,
    enforce_lower_upper_bounds,
)


class Vak:
    
    # Required column names in the Vakken sheet of the input Excel file and their typehints, accessible through the class (self.__annotations__)
    # These are stored as class-level type hints to make the attributes visible to static type checkers (e.g. Pylance).
    # The actual values are set dynamically in __init__ using setattr and a list of values.
    vak_id : int
    vak_naam: str
    M_van: float
    M_tot: float
    vak_lengte: float
    mv_achterland_vak: float
    L_achterland: float
    c_voorland_mean: float
    c_voorland_stdev: float
    c_achterland_mean: float
    c_achterland_vc: float

    # Other class-level typehints
    id: int  # Renamed version of vak_id

    def __init__(self, df_row: pd.Series, df_variable_overview: pd.DataFrame) -> None:
        
        # Initialize attributes which will be filled later
        self.uittredepunten = []  # Filled in the UittredepuntCollection class and shows all Uittredepunten in this Vak
        self.ondergrond_scenarios = []  # Filled in the OndergrondScenarioCollection class and shows all OndergrondScenarios in this Vak
        
        # Set values from Excel row as attributes of the Vak instance
        for col, value in df_row.items():
            attr_name = str(col)  # Make sure the attribute name is a string (just in case it's interpreted in a wrong format)

            # Data validation
            check_attribute_already_exists(self, attr_name)
            check_attr_in_overview(attr_name, df_variable_overview)
            enforce_lower_upper_bounds(self, attr_name, value, df_variable_overview, df_row["vak_id"])

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

        # Create vakken from df
        for _, row in self.df.iterrows():
            vak = Vak(row, df_variable_overview)
            
            # Check for duplicate vak_id before adding Vak to collection
            if vak.id in self._items:
                raise ValueError(f"Duplicate vak_id {vak.id} found")
            
            self.add(str(vak.id), vak)




