from types import SimpleNamespace

import pandas as pd

from app.classes.base_collection import BaseCollection, _pretty_repr
from app.helper_functions.data_validation import (
    check_attribute_already_exists,
    check_attribute_in_overview,
    enforce_lower_upper_bounds,
)
from app.helper_functions.parameter_functions import (
    generate_parameter_dict_for_variable,
    strip_suffix_from_list_parameter_names,
)


class Vak:
    
    # Metadata attributes of the Vak class. These are stored as class-level type hints to make the attributes visible to static type checkers (e.g. Pylance).
    # The actual values are set dynamically in __init__ using setattr and a list of values.
    id: int  # Note: this is a renamed version of vak_id
    vak_naam: str
    M_van: float
    M_tot: float
    vak_lengte: float
    

    def __init__(self, df_row: pd.Series, df_overview_parameters: pd.DataFrame, input_parameter_names_without_suffix: list[str]) -> None:
        
        # Add each input parameter to the Vak instance
        for attr_name_without_suffix in input_parameter_names_without_suffix:
            check_attribute_already_exists(self, attr_name_without_suffix)
            check_attribute_in_overview(attr_name_without_suffix, df_overview_parameters)
            
            df_overview_row = df_overview_parameters.loc[attr_name_without_suffix]  # Select relevant row from the parameter overview
            
            if df_overview_row["parameter_type"] == "metadata":
                # Metadata should be set on the Vak instance directly
                name = "id" if attr_name_without_suffix == "vak_id" else attr_name_without_suffix  # Rename vak_id to id to simplify the attribute name
                setattr(self, name, df_row[attr_name_without_suffix])
                
            elif df_overview_row.at["parameter_type"] in ["variable", "constant"]:
                # Variables and constants should be set on the variables attribute of the Vak instance
                if not hasattr(self, "variables"):
                    # Create a SimpleNamespace to hold the variables/constants of this Vak instance
                    self.variables = SimpleNamespace()
                    
                # Generate input_dict for the variable or constant. This is a dictionary containing the parameters (e.g. mean, stdev/vc, etc.)
                # All input dicts will be stored in the variables attribute of the Vak instance
                # This function also calls a helper function to enforce lower and upper bounds on the variable
                input_dict = generate_parameter_dict_for_variable(attr_name_without_suffix,
                                                                  df_overview_row=df_overview_row,
                                                                  df_row=df_row)
                                
                setattr(self.variables, attr_name_without_suffix, input_dict)
        
        # Initialize attributes which will be filled later
        self.uittredepunten = []  # Filled in the UittredepuntCollection class and shows all Uittredepunten in this Vak
        self.ondergrond_scenarios = []  # Filled in the OndergrondScenarioCollection class and shows all OndergrondScenarios in this Vak

    def __repr__(self) -> str:
        return _pretty_repr(self)
        
        
class VakCollection(BaseCollection[Vak]):
    def __init__(self, df_vakken: pd.DataFrame, df_overview_parameters: pd.DataFrame) -> None:
        super().__init__()
        self.df = df_vakken

        # Get unique column names from the df (without suffix)
        input_parameter_names_without_suffix = strip_suffix_from_list_parameter_names(self.df.columns)

        # Create Vak instances from df
        for _, row in self.df.iterrows():
            
            # Create Vak instance
            vak = Vak(row, df_overview_parameters, input_parameter_names_without_suffix)
            
            # Check for duplicate vak_id before adding Vak to collection
            if vak.id in self._items:
                raise ValueError(f"Duplicate vak_id {vak.id} found")
            
            # Add Vak instance to the collection
            self.add(str(vak.id), vak)
