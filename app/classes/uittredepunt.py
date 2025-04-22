from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
from shapely.geometry import Point

from app.classes.base_collection import BaseCollection
from app.classes.vak import VakCollection


class Uittredepunt:
    
    def __init__(self, df_row: pd.Series, vak: Vak) -> None:  # type: ignore
        
        self.vak = vak  # Link the corresponding Vak instance to this Uittredepunt instance
        
        # Set values from Excel row as attributes of the Uittredepunt instance
        for col, value in df_row.items():
            attr_name = str(col).lower()  # Enforce lowercase attribute name to avoid case sensitivity issues
            
            # Custom mapping of attribute names
            if attr_name == "uittredepunt_id":
                # Rename uittredepunt_id to id to simplify the attribute name
                attr_name = "id"

            # Check if attribute already exists
            if hasattr(self, attr_name):
                raise AttributeError(f"{self.__class__.__name__} already has an attribute named '{attr_name}', please rename the column in the input Excel file.")
            
            setattr(self, attr_name, value)        


    def __repr__(self) -> str:
        return f"Uittredepunt(id={self.id}, vak={self.vak.id})"


class UittredepuntCollection(BaseCollection[Uittredepunt]):
    def __init__(self, path_input_xlsx: Path, vak_collection: VakCollection) -> None:
        super().__init__()  # Initialize the base collection
        
        # Read Excel, strip trailing whitespace, and convert to lowercase
        # Note: the 2nd row is skipped because it contains the units of the variables, which is not needed in the code
        self.df = pd.read_excel(path_input_xlsx, sheet_name="Uittredepunten", skiprows=[1]).rename(columns=lambda x: x.strip().lower())
        
        # Create uittredepunten from df. Note that the created Uittredepunt is linked to the corresponding Vak
        for _, row in self.df.iterrows():

            uittredepunt_id = row["uittredepunt_id"]

            # Perform checks
            try:
                vak = vak_collection[row["vak_id"]]
            except KeyError:
                # If the vak_id is not found in the vak_collection, raise an error
                raise KeyError(f"Vak '{row["vak_id"]}' (corresponding to uittredepunt {uittredepunt_id}') not found in VakCollection")        

            if any(punt.id == uittredepunt_id for punt in vak.uittredepunten):
                # Check for duplicate uittredepunt_id within the same Vak
                raise ValueError(f"Duplicate uittredepunt_id: uittredepunt '{uittredepunt_id}' already exists in vak '{vak.id}'")            
            
            uittredepunt = Uittredepunt(df_row=row, vak=vak)
            vak.uittredepunten.append(uittredepunt)
            self.add(uittredepunt.id, uittredepunt)