from pathlib import Path

import pydra_core as pydra

from geoprob_pipe.classes.base_collection import BaseCollection, _pretty_repr
from geoprob_pipe.classes.uittredepunt import UittredepuntCollection


class Overschrijdingsfrequentielijn:
    def __init__(self, hrd_path: Path, hydra_locatie_id: str):

        self.id = hydra_locatie_id
        self.overschrijdingsfrequentielijn = self._calculate_overschrijdingsfrequentielijn(hrd_path, hydra_locatie_id)

    @staticmethod
    def _calculate_overschrijdingsfrequentielijn(hrd_path: Path, hydra_locatie_id: str):
        # Read HRD
        hrd = pydra.HRDatabase(hrd_path.__str__())
        
        # Setup calculation object exceedance frequency line
        fl = pydra.ExceedanceFrequencyLine("h")
        
        # Setup location
        settings = hrd.get_settings(hydra_locatie_id)
        location = hrd.create_location(settings)
        
        # Calculate exceedance frequency line for the location
        frequency_line = fl.calculate(location)
        
        return frequency_line
        
    def __repr__(self) -> str:
        return _pretty_repr(self)

        
class OverschrijdingsfrequentielijnCollection(BaseCollection[Overschrijdingsfrequentielijn]):

    def __init__(self, hrd_path: Path, uittredepunt_collection: UittredepuntCollection) -> None:
        super().__init__()  # Initialize the base collection
        self.hrd_path = hrd_path

        # Create Overschrijdingsfrequentielijn for each hydra_locatie_id in the UittredepuntCollection
        # Since the calculations for Overschrijdingsfrequentielijn might take a while, we only calculate it once per
        # unique hydra_locatie_id and later assign it to the corresponding Uittredepunt instances.
        unique_hydra_locatie_ids = list(set(uittredepunt.hydra_locatie_id for uittredepunt in uittredepunt_collection))
        for hydra_locatie_id in unique_hydra_locatie_ids:
            self.add(hydra_locatie_id, Overschrijdingsfrequentielijn(self.hrd_path, hydra_locatie_id))

        # Assign the correct Overschrijdingsfrequentielijn to each Uittredepunt
        for uittredepunt in uittredepunt_collection:
            uittredepunt.overschrijdingsfrequentielijn = self[uittredepunt.hydra_locatie_id]
