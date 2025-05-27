from types import SimpleNamespace

import pandas as pd

from app.classes.base_collection import BaseCollection, _pretty_repr
from app.classes.vak import Vak, VakCollection
from app.helper_functions.data_validation import (
    check_attribute_already_exists,
    check_attribute_in_overview,
    enforce_lower_upper_bounds,
)
from app.helper_functions.parameter_functions import (
    generate_parameter_dict_for_variable,
    strip_suffix_from_list_parameter_names,
)


class OndergrondScenario:
    
    # Metadata attributes of the OndergrondScenario class. These are stored as class-level type hints to make the attributes visible to static type checkers (e.g. Pylance).
    # The actual values are set dynamically in __init__ using setattr and a list of values.
    ondergrondscenario_id: int  # Note: this is a renamed version of ondergrondscenario_id
    vak_id: int
    ondergrondscenario_naam: str

    
    # Other class-level typehints
    id: int  # Renamed version of ondergrondscenario_id
    
    def __init__(self, df_row: pd.Series, vak: Vak, df_overview_parameters: pd.DataFrame, input_parameter_names_without_suffix: list[str]) -> None:

        # Add each input parameter to the OndergrondScenario instance
        for attr_name_without_suffix in input_parameter_names_without_suffix:
            check_attribute_already_exists(self, attr_name_without_suffix)
            check_attribute_in_overview(attr_name_without_suffix, df_overview_parameters)
            
            df_overview_row = df_overview_parameters.loc[attr_name_without_suffix]  # Select relevant row from the parameter overview
            
            if df_overview_row["parameter_type"] == "metadata":
                # Metadata should be set on the OndergrondScenario instance directly
                name = "id" if attr_name_without_suffix == "ondergrondscenario_id" else attr_name_without_suffix  # Rename ondergrondscenario_id to id to simplify the attribute name
                setattr(self, name, df_row[attr_name_without_suffix])
                
            elif df_overview_row["parameter_type"] in ["variable", "constant"]:
                # Variables and constants should be set on the variables attribute of the OndergrondScenario instance
                if not hasattr(self, "variables"):
                    # Create a SimpleNamespace to hold the variables/constants of this OndergrondScenario instance
                    self.variables = SimpleNamespace()
                    
                # Generate input_dict for the variable or constant. This is a dictionary containing the parameters (e.g. mean, stdev/vc, etc.)
                # All input dicts will be stored in the variables attribute of the OndergrondScenario instance
                # This function also calls a helper function to enforce lower and upper bounds on the variable
                input_dict = generate_parameter_dict_for_variable(attr_name_without_suffix,
                                                                  df_overview_row=df_overview_row,
                                                                  df_row=df_row)
                
                setattr(self.variables, attr_name_without_suffix, input_dict)


        self.vak = vak  # Link the corresponding Vak instance to this OndergrondScenario instance
    

    def __repr__(self) -> str:
        return _pretty_repr(self)
    
    
class OndergrondScenarioCollection(BaseCollection[OndergrondScenario]):
    def __init__(self, df_ondergrond_scenarios: pd.DataFrame, vak_collection: VakCollection, df_overview_parameters: pd.DataFrame) -> None:
        super().__init__()  # Initialize the base collection
        self.df = df_ondergrond_scenarios

        # Get unique column names from the df (without suffix)
        input_parameter_names_without_suffix = strip_suffix_from_list_parameter_names(self.df.columns)

        # Create ondergrondscenarios from df. Note that the created OndergrondScenario is linked to the corresponding Vak
        for _, row in self.df.iterrows():
            
            ondergrond_scenario_id = row["ondergrondscenario_id"]

            # Perform checks
            try:
                vak = vak_collection[str(row["vak_id"])]
            except KeyError:
                # If the vak_id is not found in the vak_collection, raise an error
                raise KeyError(f"Vak ID '{row["vak_id"]}' (corresponding to scenario '{ondergrond_scenario_id}') not found in VakCollection")        

            if any(punt.id == ondergrond_scenario_id for punt in vak.ondergrond_scenarios):
                # Check for duplicate ondergrondscenario_id within the same Vak
                raise ValueError(f"Duplicate ondergrondscenario_id: scenario '{ondergrond_scenario_id}' already exists in vak '{vak.id}'")            
            
            # Create OndergrondScenario instance
            scenario = OndergrondScenario(row, vak, df_overview_parameters, input_parameter_names_without_suffix)
            
            # Add OndergrondScenario instance as attribute to the corresponding Vak instance 
            vak.ondergrond_scenarios.append(scenario)
            
            # Add OndergrondScenario instance to the collection
            self.add(str(scenario.id), scenario)