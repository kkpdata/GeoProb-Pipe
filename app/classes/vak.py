from pathlib import Path

import pandas as pd

from app.classes.base_collection import BaseCollection


class Vak:
    
    def __init__(self, df_row: pd.Series) -> None:
        self.id = df_row["VakID"]
        self.uittredepunten = []  # This will be filled in the UittredepuntCollection class and shows all Uittredepunten in this Vak
        self.ondergrond_scenarios = []  # This will be filled in the OndergrondScenarioCollection class and shows all OndergrondScenarios in this Vak

    def __repr__(self) -> str:
        return f"Vak(naam={self.id})"

        
class VakCollection(BaseCollection[Vak]):
    def __init__(self, path_input_xlsx=Path) -> None:
        super().__init__()
        self.df = pd.read_excel(path_input_xlsx, sheet_name="Vakken")
        
        # Create vakken from df
        for _, row in self.df.iterrows():
            vak = Vak(row)
            
            # Check for duplicate VakID before adding Vak to collection
            if vak.id in self._items:
                raise ValueError(f"Duplicate VakID {vak.id} found")
            
            self.add(vak.id, vak)




