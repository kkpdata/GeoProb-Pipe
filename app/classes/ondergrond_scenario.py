from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from app.classes.base_collection import BaseCollection, _pretty_repr
from app.classes.vak import Vak, VakCollection
from app.helper_functions.data_validation import (
    check_attr_in_overview,
    check_attribute_already_exists,
    enforce_lower_upper_bounds,
)
from app.helper_functions.variable_functions import (
    generate_variable_dict,
    strip_suffix_from_list_variable_names,
)


class OndergrondScenario:
    
    # Metadata attributes of the OndergrondScenario class. These are stored as class-level type hints to make the attributes visible to static type checkers (e.g. Pylance).
    # The actual values are set dynamically in __init__ using setattr and a list of values.
    ondergrondscenario_id: int  # Note: this is a renamed version of ondergrondscenario_id
    vak_id: int
    ondergrondscenario_naam: str

    
    # Other class-level typehints
    id: int  # Renamed version of ondergrondscenario_id
    
    def __init__(self, df_row: pd.Series, vak: Vak, df_variable_overview: pd.DataFrame, input_variable_names_without_suffix: list[str]) -> None:

        # For each variable of this OndergrondScenario instance, generate a dictionary containing its parameters
        for attr_name_without_suffix in input_variable_names_without_suffix:
            check_attribute_already_exists(self, attr_name_without_suffix)
            check_attr_in_overview(attr_name_without_suffix, df_variable_overview)
            
            if df_variable_overview.at[attr_name_without_suffix, "variable_type"] == "metadata":
                # Metadata should be set on the OndergrondScenario instance directly
                name = "id" if attr_name_without_suffix == "ondergrondscenario_id" else attr_name_without_suffix  # Rename ondergrondscenario_id to id to simplify the attribute name
                setattr(self, name, df_row[attr_name_without_suffix])
                
            elif df_variable_overview.at[attr_name_without_suffix, "variable_type"] in ["variable", "constant"]:
                # Variables and constants should be set on the variables attribute of the OndergrondScenario instance
                if not hasattr(self, "variables"):
                    # Create a SimpleNamespace to hold the variables/constants of this OndergrondScenario instance
                    self.variables = SimpleNamespace()
                    
                # Generate input_dict for the variable or constant. This is a dictionary containing the parameters (e.g. mean, stdev/vc, etc.)
                # All input dicts will be stored in the variables attribute of the OndergrondScenario instance
                input_dict = generate_variable_dict(attr_name_without_suffix, df_row, df_variable_overview)
                
                enforce_lower_upper_bounds(attr_name_without_suffix, input_dict, df_variable_overview, self.__class__, df_row["ondergrondscenario_id"])
                
                setattr(self.variables, attr_name_without_suffix, input_dict)


        self.vak = vak  # Link the corresponding Vak instance to this OndergrondScenario instance


        # self.vak = vak  # Link the corresponding Vak instance to this OndergrondScenario instance
        
        # # Set values from Excel row as attributes of the OndergrondScenario instance
        # for col, value in df_row.items():
        #     attr_name = str(col)  # Make sure the attribute name is a string (just in case it's interpreted in a wrong format)
            
        #     # Data validation
        #     check_attribute_already_exists(self, attr_name)
        #     check_attr_in_overview(attr_name, df_variable_overview)
        #     enforce_lower_upper_bounds(self, attr_name, value, df_variable_overview, df_row["ondergrondscenario_id"])
            
        #     # Custom mapping of ondergrondscenario_id to id to simplify the attribute name
        #     if attr_name == "ondergrondscenario_id":
        #         attr_name = "id"

        #     # Set attribute dynamically
        #     setattr(self, attr_name, value)        

    def __repr__(self) -> str:
        return _pretty_repr(self)
    
    
class OndergrondScenarioCollection(BaseCollection[OndergrondScenario]):
    def __init__(self, path_input_xlsx: Path, vak_collection: VakCollection, df_variable_overview: pd.DataFrame) -> None:
        super().__init__()  # Initialize the base collection
        
        # Read Excel, strip trailing whitespace.
        # Also, unused ondergrondscenario's (ondergrondscenario_kans=Nan or ondergrondscenario_kans=0) are removed
        self.df = pd.read_excel(path_input_xlsx, sheet_name="Ondergrondscenarios").rename(columns=lambda x: x.strip()).dropna(subset=['ondergrondscenario_kans']).loc[lambda x: x['ondergrondscenario_kans'] != 0]

        # Get unique column names from the df (without suffix)
        input_variable_names_without_suffix = strip_suffix_from_list_variable_names(self.df.columns)

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
            
            # Create OndergrondScenario instance
            scenario = OndergrondScenario(row, vak, df_variable_overview, input_variable_names_without_suffix)
            
            # Add OndergrondScenario instance as attribute to the corresponding Vak instance 
            vak.ondergrond_scenarios.append(scenario)
            
            # Add OndergrondScenario instance to the collection
            self.add(str(scenario.id), scenario)