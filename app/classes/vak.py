from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from app.classes.base_collection import BaseCollection
from app.helper_functions.data_validation import (
    check_attr_in_overview,
    check_attribute_already_exists,
    enforce_lower_upper_bounds,
)
from app.helper_functions.variable_functions import (
    generate_variable_dict,
    strip_suffix_from_list_variable_names,
)
from app.classes.base_collection import _pretty_repr

class Vak:
    
    # Metadata attributes of the Vak class. These are stored as class-level type hints to make the attributes visible to static type checkers (e.g. Pylance).
    # The actual values are set dynamically in __init__ using setattr and a list of values.
    id: int  # Note: this is a renamed version of vak_id
    vak_naam: str
    M_van: float
    M_tot: float
    vak_lengte: float
    

    def __init__(self, df_row: pd.Series, df_variable_overview: pd.DataFrame, input_variable_names_without_suffix: list[str]) -> None:
        
        # For each variable of this Vak instance, generate a dictionary containing its parameters
        for attr_name_without_suffix in input_variable_names_without_suffix:
            check_attribute_already_exists(self, attr_name_without_suffix)
            check_attr_in_overview(attr_name_without_suffix, df_variable_overview)
            
            if df_variable_overview.at[attr_name_without_suffix, "variable_type"] == "metadata":
                # Metadata should be set on the Vak instance directly
                name = "id" if attr_name_without_suffix == "vak_id" else attr_name_without_suffix  # Rename vak_id to id to simplify the attribute name
                setattr(self, name, df_row[attr_name_without_suffix])
                
            elif df_variable_overview.at[attr_name_without_suffix, "variable_type"] in ["variable", "constant"]:
                # Variables and constants should be set on the variables attribute of the Vak instance
                if not hasattr(self, "variables"):
                    # Create a SimpleNamespace to hold the variables/constants of this Vak instance
                    self.variables = SimpleNamespace()
                    
                # Generate input_dict for the variable or constant. This is a dictionary containing the parameters (e.g. mean, stdev/vc, etc.)
                # All input dicts will be stored in the variables attribute of the Vak instance
                input_dict = generate_variable_dict(attr_name_without_suffix, df_row, df_variable_overview)
                
                enforce_lower_upper_bounds(attr_name_without_suffix, input_dict, df_variable_overview, self.__class__, df_row["vak_id"])
                
                setattr(self.variables, attr_name_without_suffix, input_dict)
        
        # Initialize attributes which will be filled later
        self.uittredepunten = []  # Filled in the UittredepuntCollection class and shows all Uittredepunten in this Vak
        self.ondergrond_scenarios = []  # Filled in the OndergrondScenarioCollection class and shows all OndergrondScenarios in this Vak

    def __repr__(self) -> str:
        return _pretty_repr(self)
        
        
class VakCollection(BaseCollection[Vak]):
    def __init__(self, path_input_xlsx: Path, df_variable_overview: pd.DataFrame) -> None:
        super().__init__()
        
        # Read Excel, strip trailing whitespace
        self.df = pd.read_excel(path_input_xlsx, sheet_name="Vakken").rename(columns=lambda x: x.strip())

        # Get unique column names from the df (without suffix)
        input_variable_names_without_suffix = strip_suffix_from_list_variable_names(self.df.columns)

        # Create Vak instances from df
        for _, row in self.df.iterrows():
            
            # Create Vak instance
            vak = Vak(row, df_variable_overview, input_variable_names_without_suffix)
            
            # Check for duplicate vak_id before adding Vak to collection
            if vak.id in self._items:
                raise ValueError(f"Duplicate vak_id {vak.id} found")
            
            # Add Vak instance to the collection
            self.add(str(vak.id), vak)
