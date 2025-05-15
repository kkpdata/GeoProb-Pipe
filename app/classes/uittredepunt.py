from pathlib import Path
from types import SimpleNamespace

import pandas as pd
from shapely.geometry import Point

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


    def __init__(self, df_row: pd.Series, vak: Vak, df_variable_overview: pd.DataFrame, input_variable_names_without_suffix: list[str]) -> None:
        
        # For each variable of this Uittredepunt instance, generate a dictionary containing its parameters
        for attr_name_without_suffix in input_variable_names_without_suffix:
            check_attribute_already_exists(self, attr_name_without_suffix)
            check_attr_in_overview(attr_name_without_suffix, df_variable_overview)
            
            if df_variable_overview.at[attr_name_without_suffix, "variable_type"] == "metadata":
                # Metadata should be set on the Uittredepunt instance directly
                name = "id" if attr_name_without_suffix == "uittredepunt_id" else attr_name_without_suffix  # Rename uittredepunt_id to id to simplify the attribute name
                setattr(self, name, df_row[attr_name_without_suffix])
                
            elif df_variable_overview.at[attr_name_without_suffix, "variable_type"] in ["variable", "constant"]:
                # Variables and constants should be set on the variables attribute of the Uittredepunt instance
                if not hasattr(self, "variables"):
                    # Create a SimpleNamespace to hold the variables/constants of this Uittredepunt instance
                    self.variables = SimpleNamespace()
                    
                # Generate input_dict for the variable or constant. This is a dictionary containing the parameters (e.g. mean, stdev/vc, etc.)
                # All input dicts will be stored in the variables attribute of the Uittredepunt instance
                input_dict = generate_variable_dict(attr_name_without_suffix, df_row, df_variable_overview)
                
                enforce_lower_upper_bounds(attr_name_without_suffix, input_dict, df_variable_overview, self.__class__, df_row["uittredepunt_id"])
                
                setattr(self.variables, attr_name_without_suffix, input_dict)

        self.vak = vak  # Link the corresponding Vak instance to this Uittredepunt instance


    def __repr__(self) -> str:
        return _pretty_repr(self)


class UittredepuntCollection(BaseCollection[Uittredepunt]):
    def __init__(self, path_input_xlsx: Path, vak_collection: VakCollection, df_variable_overview: pd.DataFrame) -> None:
        super().__init__()  # Initialize the base collection
        
        # Read Excel, strip trailing whitespace
        self.df = pd.read_excel(path_input_xlsx, sheet_name="Uittredepunten").rename(columns=lambda x: x.strip())
        
        # Get unique column names from the df (without suffix)
        input_variable_names_without_suffix = strip_suffix_from_list_variable_names(self.df.columns)
        
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
            uittredepunt = Uittredepunt(row, vak, df_variable_overview, input_variable_names_without_suffix)
            
            # Add Uittredepunt instance as attribute to the corresponding Vak instance 
            vak.uittredepunten.append(uittredepunt)
            
            # Add Uittredepunt instance to the collection
            self.add(str(uittredepunt.id), uittredepunt)