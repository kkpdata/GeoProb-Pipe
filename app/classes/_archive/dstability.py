from pathlib import Path

import pandas as pd

from app.classes.file_system import FileSystem
from app.helper_functions.geolib_functions import (
    check_stix_one_calculation,
    check_stix_one_scenario,
    check_stix_validity_integrity_structure,
    get_waterlevels,
    parse_stix,
)


class DStability:
    """DStability class which holds info related to the D-Stability (.stix) models"""
    def __init__(self, path_folder_input_stix: str | Path) -> None:
        """Initialize DStability instance which holds info related to the D-Stability (.stix) models

        Args:
            path_folder_input_stix (str | Path): path to folder containing .stix files
        """
        self.filesystem = FileSystem(path_folder_input_stix, "stix")
        self.overview = self._get_overview()
        self.overview["model"].apply(
            lambda model: (
                check_stix_validity_integrity_structure(model),
                check_stix_one_scenario(model),
                check_stix_one_calculation(model),
            )
        )

    @property
    def models(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: overview of .stix filepaths and their parsed D-Stability models
        """
        return self.overview[["stix", "model"]]

    @property
    def waterlevels(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: overview of waterlevels used in .stix files 
        """
        return self.overview[["stix", "waterlevel"]]

    def _get_overview(self) -> pd.DataFrame:
        """Create overview of D-Stability .stix files, their parsed models and the waterlevels used in these models

        Returns:
            pd.DataFrame: overview showing .stix filepaths, parsed D-Stability models and the waterlevels
        """
        df = pd.DataFrame(
            {
                "stix": [
                    {"path": filepath, "name": filename}
                    for filepath, filename in zip(self.filesystem.files["filepath"], self.filesystem.files["filename"])
                ]
            },
            dtype=object,
        )

        df["model"] = df["stix"].apply(lambda stix: parse_stix(stix["path"]))  # type: ignore
        df["waterlevel"] = df["model"].apply(get_waterlevels)

        # Sort DataFrame based on the waterlevel values
        df.sort_values(by="waterlevel", ignore_index=True, inplace=True)

        # Return the DataFrame and make sure the waterlevels are shown in the first column
        return df[["waterlevel"] + [col for col in df.columns if col != "waterlevel"]]
