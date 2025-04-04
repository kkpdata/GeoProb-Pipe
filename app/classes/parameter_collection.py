from pathlib import Path
from dataclasses import dataclass
import pandas as pd

from app.classes.file_system import FileSystem

# FIXME werkt nog niet
class ParameterCollection():
    """Contains input parameters from Excel"""
    def __init__(self, filepath: Path) -> None:
        self.filepath = FileSystem.find_files_in_dir(filepath, "xlsx")[0]
        self.vak = self.Vak(self.filepath)
        
    class Vak:
        def __init__(self, filepath: Path) -> None:
            self.df = pd.read_excel(filepath, sheet_name="Vak")
            
            @dataclass
            class Params:
                UittredepuntID: int
                X_uitrede: float
                Y_uitrede: float
                Uitredelocatie: str
                Mvalue: float
                VakID: int
                Vaknaam: str
                DIST_L_GEOM: float
                DIST_BUT: float
                DIST_BIT: float
                WBN: float
                HydraLocatieID: str
                Bodemhoogte: float
                Polderpei: float
                Top_zand_lokaal: float
                Top_zand_regionaal: float
                Top_klei_lokaal: float            
            
            self.params = Params(self.df)
        
