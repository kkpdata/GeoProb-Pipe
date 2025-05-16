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
    generate_variable_dict,
    strip_suffix_from_list_parameter_names,
)


class Uittredepunt:

    # Metadata attributes of the Uittredepunt class. These are stored as class-level type hints to make the attributes visible to static type checkers (e.g. Pylance).
    # The actual values are set dynamically in __init__ using setattr and a list of values.
    id: int  # Note: this is a renamed version of uittredepunt_id
    vak_id: int  # ID of the corresponding Vak instance
    uittredepunt_x_coord: float
    uittredepunt_y_coord: float
    uittredelocatie: str
    M_value: float
    vak_naam: str
    hydra_locatie_id: str


    def __init__(self, df_row: pd.Series, vak: Vak, df_overview_parameters: pd.DataFrame, input_parameter_names_without_suffix: list[str]) -> None:
        
        # Add each input parameter to the Uittredepunt instance
        for attr_name_without_suffix in input_parameter_names_without_suffix:
            check_attribute_already_exists(self, attr_name_without_suffix)
            check_attribute_in_overview(attr_name_without_suffix, df_overview_parameters)
            
            # TODO nice to have: convert x,y coordinates to a Shapely Point
            if df_overview_parameters.at[attr_name_without_suffix, "parameter_type"] == "metadata":
                # Metadata should be set on the Uittredepunt instance directly
                name = "id" if attr_name_without_suffix == "uittredepunt_id" else attr_name_without_suffix  # Rename uittredepunt_id to id to simplify the attribute name
                setattr(self, name, df_row[attr_name_without_suffix])
                
            elif df_overview_parameters.at[attr_name_without_suffix, "parameter_type"] in ["variable", "constant"]:
                # Variables and constants should be set on the variables attribute of the Uittredepunt instance
                if not hasattr(self, "variables"):
                    # Create a SimpleNamespace to hold the variables/constants of this Uittredepunt instance
                    self.variables = SimpleNamespace()
                    
                # Generate input_dict for the variable or constant. This is a dictionary containing the parameters (e.g. mean, stdev/vc, etc.)
                # All input dicts will be stored in the variables attribute of the Uittredepunt instance
                input_dict = generate_variable_dict(attr_name_without_suffix, df_row, df_overview_parameters)
                
                enforce_lower_upper_bounds(attr_name_without_suffix, input_dict, df_overview_parameters, self.__class__, df_row["uittredepunt_id"])
                
                setattr(self.variables, attr_name_without_suffix, input_dict)

        self.vak = vak  # Link the corresponding Vak instance to this Uittredepunt instance


    def __repr__(self) -> str:
        return _pretty_repr(self)


class UittredepuntCollection(BaseCollection[Uittredepunt]):
    def __init__(self, df_uittredepunten: pd.DataFrame, vak_collection: VakCollection, df_overview_parameters: pd.DataFrame) -> None:
        super().__init__()  # Initialize the base collection
        self.df = df_uittredepunten
        
        # Get unique column names from the df (without suffix)
        input_parameter_names_without_suffix = strip_suffix_from_list_parameter_names(self.df.columns)
        
        # Create uittredepunten from df. Note that the created Uittredepunt is linked to the corresponding Vak
        for _, row in self.df.iterrows():

            uittredepunt_id = row["uittredepunt_id"]

            # Perform checks
            try:
                vak = vak_collection[str(row["vak_id"])]
            except KeyError:
                # If the vak_id is not found in the vak_collection, raise an error
                raise KeyError(f"Vak ID '{row["vak_id"]}' (corresponding to uittredepunt {uittredepunt_id}') not found in VakCollection")        

            if any(punt.id == uittredepunt_id for punt in vak.uittredepunten):
                # Check for duplicate uittredepunt_id within the same Vak
                raise ValueError(f"Duplicate uittredepunt_id: uittredepunt '{uittredepunt_id}' already exists in vak '{vak.id}'")            
            
            # Create Uittredepunt instance
            uittredepunt = Uittredepunt(row, vak, df_overview_parameters, input_parameter_names_without_suffix)
            
            # Add Uittredepunt instance as attribute to the corresponding Vak instance 
            vak.uittredepunten.append(uittredepunt)
            
            # Add Uittredepunt instance to the collection
            self.add(str(uittredepunt.id), uittredepunt)