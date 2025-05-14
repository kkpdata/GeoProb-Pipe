from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from app.classes.base_collection import BaseCollection
from app.helper_functions.data_validation import (
    check_attr_in_overview,
    check_attribute_already_exists,
    enforce_lower_upper_bounds,
)
from app.helper_functions.variables import (
    generate_variable_dict,
    get_variable_name_without_suffix,
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

    def __init__(self, df_row: pd.Series, df_variable_overview: pd.DataFrame, input_variable_names_without_suffix: list) -> None:
        
        # Initialize attributes which will be filled later
        self.uittredepunten = []  # Filled in the UittredepuntCollection class and shows all Uittredepunten in this Vak
        self.ondergrond_scenarios = []  # Filled in the OndergrondScenarioCollection class and shows all OndergrondScenarios in this Vak
        self.variables = SimpleNamespace()  # Create a SimpleNamespace to hold the variables of this Vak instance
        
                
        # For each variable of this Vak instance, generate a dictionary containing it's parameters
        for attr_name_without_suffix in input_variable_names_without_suffix:
            check_attribute_already_exists(self, attr_name_without_suffix)
            check_attr_in_overview(attr_name_without_suffix, df_variable_overview)
            
            if df_variable_overview.at[attr_name_without_suffix, "variable_type"] == "metadata":
                # Metadata should be set on the Vak instance directly
                
                name = "id" if attr_name_without_suffix == "vak_id" else attr_name_without_suffix  # Rename vak_id to id to simplify the attribute name
                
                setattr(self, name, df_row[attr_name_without_suffix])
                
            elif df_variable_overview.at[attr_name_without_suffix, "variable_type"] in ["variable", "constant"]:
                # Generate input_dict for the variable or constant. This is a dictionary containing the parameters (e.g. mean, stdev/vc, etc.)
                # All input dicts will be stored in the variables attribute of the Vak instance
                input_dict = generate_variable_dict(attr_name_without_suffix, df_row, df_variable_overview)
                
                enforce_lower_upper_bounds(attr_name_without_suffix, input_dict, df_variable_overview, self.__class__, df_row["vak_id"])
                
                setattr(self.variables, attr_name_without_suffix, input_dict)
                #FIXME LET OP: SOMMIGE VARS KOMEN OP SELF EN SOMMIGEN OP SELF.VARIABLES, MOET ALLEMAAL OP SELF.VARIABLES KOMEN
        
        # # Set values from Excel row as attributes of the Vak instance
        # for col, value in df_row.items():
        #     attr_name = str(col)  # Make sure the attribute name is a string (just in case it's interpreted in a wrong format)

        #     # Data validation
        #     check_attribute_already_exists(self, attr_name)
        #     check_attr_in_overview(attr_name, df_variable_overview)
        #     enforce_lower_upper_bounds(self, attr_name, value, df_variable_overview, df_row["vak_id"])

        #     # Custom mapping of attribute names (if needed)
        #     if attr_name == "vak_id":
        #         # Rename vak_id to id to simplify the attribute name
        #         attr_name = "id"

        #     # Set attribute dynamically
        #     setattr(self, attr_name, value)

    def __repr__(self) -> str:
        return f"Vak(id={self.id})"

        
class VakCollection(BaseCollection[Vak]):
    def __init__(self, path_input_xlsx: Path, df_variable_overview: pd.DataFrame) -> None:
        super().__init__()
        
        # Read Excel, strip trailing whitespace
        self.df = pd.read_excel(path_input_xlsx, sheet_name="Vakken").rename(columns=lambda x: x.strip())

        input_variable_names_without_suffix = get_variable_name_without_suffix(self.df.columns.to_list())

        # Create vakken from df
        for _, row in self.df.iterrows():
            
            

            vak = Vak(row, df_variable_overview, input_variable_names_without_suffix)
            
            # Check for duplicate vak_id before adding Vak to collection
            if vak.id in self._items:
                raise ValueError(f"Duplicate vak_id {vak.id} found")
            
            self.add(str(vak.id), vak)




