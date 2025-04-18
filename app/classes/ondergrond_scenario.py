from pathlib import Path

import pandas as pd

from app.classes.base_collection import BaseCollection
from app.classes.vak import VakCollection


class OndergrondScenario:
    
    def __init__(self, vak: Vak, id: str, scenario_probability: float) -> None:  # type: ignore
        self.id = id
        self.scenario_probability = scenario_probability
        self.vak = vak

    def __repr__(self) -> str:
        return f"OndergrondScenario(naam={self.id}, scenario_probability={self.scenario_probability}, valid={self.vak.id})"
    
    
class OndergrondScenarioCollection(BaseCollection[OndergrondScenario]):
    def __init__(self, path_input_xlsx: Path, vak_collection: VakCollection) -> None:
        super().__init__()
        self.df = pd.read_excel(path_input_xlsx, sheet_name="Ondergrondscenarios")
        
        # Create ondergrondscenarios from df. Note that the created OndergrondScenario is linked to the corresponding Vak
        for _, row in self.df.iterrows():
            
            ondergrondscenario_id = row["ScenarioID"]

            # Perform checks
            try:
                vak = vak_collection[row["VakID"]]
            except KeyError:
                # If the VakID is not found in the vak_collection, raise an error
                raise KeyError(f"Vak '{row["VakID"]}' (corresponding to scenario '{ondergrondscenario_id}') not found in VakCollection")        

            if any(punt.id == ondergrondscenario_id for punt in vak.ondergrond_scenarios):
                # Check for duplicate ScenarioID within the same Vak
                raise ValueError(f"Duplicate ScenarioID: scenario '{ondergrondscenario_id}' already exists in vak '{vak.id}'")            
            
            scenario = OndergrondScenario(id=row["ScenarioID"], scenario_probability=row["Scenariokans [%]"], vak=vak)
            vak.ondergrond_scenarios.append(scenario)
            self.add(scenario.id, scenario)