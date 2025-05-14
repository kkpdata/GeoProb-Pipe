from pathlib import Path

import pandas as pd
from shapely.geometry import Point

from app.classes.base_collection import BaseCollection
from app.classes.vak import Vak, VakCollection
from app.helper_functions.data_validation import (
    check_attr_in_overview,
    check_attribute_already_exists,
    enforce_lower_upper_bounds,
)


class Uittredepunt:

    # Required column names in the Uittredepunten sheet of the input Excel file and their typehints, accessible through the class (self.__annotations__)
    # These are stored as class-level type hints to make the attributes visible to static type checkers (e.g. Pylance).
    # The actual values are set dynamically in __init__ using setattr and a list of values.
    vak_id: int
    uittredepunt_id: int
    uittredepunt_x_coord: float
    uittredepunt_y_coord: float
    uittredelocatie: str
    M_value: float
    vak_naam: str
    L_intrede: float
    L_but: float
    L_bit: float
    hydra_locatie_id: str
    buitenwaterstand: float
    mv_exit: float
    polderpeil: float
    modelfactor_u_mean: float
    modelfactor_u_stdev: float
    modelfactor_h_mean: float
    modelfactor_h_stdev: float
    modelfactor_p_mean: float
    modelfactor_p_stdev: float

    # Other class-level typehints
    id: int  # Renamed version of uittredepunt_id

    def __init__(self, df_row: pd.Series, vak: Vak, df_variable_overview: pd.DataFrame) -> None:
        self.__annotations__ = {"id": str}
        self.vak = vak  # Link the corresponding Vak instance to this Uittredepunt instance
        
        # Set values from Excel row as attributes of the Uittredepunt instance
        for col, value in df_row.items():
            attr_name = str(col)  # Make sure the attribute name is a string (just in case it's interpreted in a wrong format)
            
            # Perform data validation
            check_attribute_already_exists(self, attr_name)
            check_attr_in_overview(attr_name, df_variable_overview)
            enforce_lower_upper_bounds(self, attr_name, value, df_variable_overview, df_row["uittredepunt_id"])

            # Custom mapping of uittredepunt_id to id to simplify the attribute name
            if attr_name == "uittredepunt_id":
                attr_name = "id"

            # Set attribute dynamically
            setattr(self, attr_name, value)     
               
    
    def __repr__(self) -> str:
        return f"Uittredepunt(id={self.id}, vak={self.vak.id})"


class UittredepuntCollection(BaseCollection[Uittredepunt]):
    def __init__(self, path_input_xlsx: Path, vak_collection: VakCollection, df_variable_overview: pd.DataFrame) -> None:
        super().__init__()  # Initialize the base collection
        
        # Read Excel, strip trailing whitespace
        self.df = pd.read_excel(path_input_xlsx, sheet_name="Uittredepunten").rename(columns=lambda x: x.strip())
        
        # Data validation
        # check_required_columns(self, self.df)
        
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
            
            uittredepunt = Uittredepunt(row, vak, df_variable_overview)
            vak.uittredepunten.append(uittredepunt)
            self.add(str(uittredepunt.id), uittredepunt)