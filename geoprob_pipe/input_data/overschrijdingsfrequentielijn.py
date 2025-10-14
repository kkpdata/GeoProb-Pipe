from pathlib import Path
import numpy as np
import pydra_core as pydra
from geoprob_pipe.input_data.base_collection import BaseCollection, pretty_repr
from geoprob_pipe.input_data.uittredepunt import UittredepuntCollection
import os

class Overschrijdingsfrequentielijn:
    def __init__(self, hrd_path: Path, hydra_locatie_id: str):

        self.id = hydra_locatie_id
        if hydra_locatie_id.endswith(".csv"):
            self.overschrijdingsfrequentielijn = self._calculate_overschrijdingsfrequentielijn_from_csv(
                hrd_path, hydra_locatie_id)
        else:
            self.overschrijdingsfrequentielijn = self._calculate_overschrijdingsfrequentielijn_from_hrd(
                hrd_path, hydra_locatie_id)

    @staticmethod
    def _calculate_overschrijdingsfrequentielijn_from_hrd(hrd_path: Path, hydra_locatie_id: str):
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

    @staticmethod
    def _calculate_overschrijdingsfrequentielijn_from_csv(hrd_path: Path, hydra_locatie_id: str):
        """ Leest de overschrijdingsfrequentielijn uit een csv-bestand als in de input.xlsx een de hydra-locatie
        eindigt op '.csv'. Aangenomen wordt dat de csv-bestanden staan op locatie
        workspace_name\input\hr_frequency_lines\.

        TODO: Vervangen voor inlezen in pre-processing. En inlezen vanuit input.xlsx i.p.v. per csv-bestand?
        """

        # Check if file exists
        file_path = os.path.join(hrd_path.parent, "hr_frequency_lines", hydra_locatie_id)
        if not os.path.exists(file_path):
            raise ValueError(f"Overschrijdingsfrequentielijn met id {hydra_locatie_id} eindigt op '.csv', want "
                             f"aangeeft dat de informatie uit een .csv-bestand gehaald moet worden. Echter is dit "
                             f"bestand niet terug gevonden op locatie:\n"
                             f"{file_path}")

        # Import frequency line
        data = np.loadtxt('output.csv', delimiter=',', skiprows=1)
        level = np.array(data[:, 0])
        exceedance_frequency = np.array(data[:, 1])

        # noinspection PyUnresolvedReferences
        return pydra.core.datamodels.frequency_line.FrequencyLine(
            level=level, exceedance_frequency=exceedance_frequency)

    def __repr__(self) -> str:
        return pretty_repr(self)

        
class OverschrijdingsfrequentielijnCollection(BaseCollection[Overschrijdingsfrequentielijn]):

    def __init__(self, path_hrd: Path, uittredepunt_collection: UittredepuntCollection) -> None:
        super().__init__()  # Initialize the base collection
        self.path_hrd = path_hrd

        # Create Overschrijdingsfrequentielijn for each hydra_locatie_id in the UittredepuntCollection
        # Since the calculations for Overschrijdingsfrequentielijn might take a while, we only calculate it once per
        # unique hydra_locatie_id and later assign it to the corresponding Uittredepunt instances.
        unique_hydra_locatie_ids = list(set(uittredepunt.hydra_locatie_id for uittredepunt in uittredepunt_collection))
        for hydra_locatie_id in unique_hydra_locatie_ids:
            self.add(hydra_locatie_id, Overschrijdingsfrequentielijn(self.path_hrd, hydra_locatie_id))

        # Assign the correct Overschrijdingsfrequentielijn to each Uittredepunt
        for uittredepunt in uittredepunt_collection:
            uittredepunt.overschrijdingsfrequentielijn = self[uittredepunt.hydra_locatie_id]
