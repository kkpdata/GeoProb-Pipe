from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
from shapely.geometry import Point

from app.classes.base_collection import BaseCollection
from app.classes.vak import VakCollection


class Uittredepunt:
    
    def __init__(self, id: str, locatie: Point, vak: Vak) -> None:  # type: ignore
        
        self.id = id
        self.locatie = locatie
        self.vak = vak

    def __repr__(self) -> str:
        return f"Uittredepunt(locatie={self.locatie}, vak={self.vak.id})"


class UittredepuntCollection(BaseCollection[Uittredepunt]):
    def __init__(self, path_input_xlsx: Path, vak_collection: VakCollection) -> None:
        super().__init__()
        self.df = pd.read_excel(path_input_xlsx, sheet_name="Uittredepunten")
        
        # Create uittredepunten from df. Note that the created Uittredepunt is linked to the corresponding Vak
        for _, row in self.df.iterrows():

            uittredepunt_id = row["UittredepuntID"]

            # Perform checks
            try:
                vak = vak_collection[row["VakID"]]
            except KeyError:
                # If the VakID is not found in the vak_collection, raise an error
                raise KeyError(f"Vak '{row["VakID"]}' (corresponding to uittredepunt {uittredepunt_id}') not found in VakCollection")        

            if any(punt.id == uittredepunt_id for punt in vak.uittredepunten):
                # Check for duplicate UittredepuntID within the same Vak
                raise ValueError(f"Duplicate UittredepuntID: uittredepunt '{uittredepunt_id}' already exists in vak '{vak.id}'")            
            
            uittredepunt = Uittredepunt(id=row["UittredepuntID"], locatie=row["Locatie"], vak=vak)
            vak.uittredepunten.append(uittredepunt)
            self.add(uittredepunt.id, uittredepunt)