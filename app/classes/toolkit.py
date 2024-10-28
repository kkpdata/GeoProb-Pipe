import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

from app.classes.toolkit_results import ToolkitResults
from app.classes.toolkit_settings import ToolkitSettings
from app.helper_functions.toolkit_functions import (
    load_tkx_file,
    run_parallel_toolkit_calculations,
    tkx_model_factor_dist_params_correct,
    tkx_model_factor_in_variables,
    tkx_variable_count_correct,
    xml_change_path_stix,
    xml_change_work_dir,
    xml_cleanup_work_dir_after_run,
)


class Toolkit:
    """Toolkit class containing functions related to the Probabilistic Toolkit"""

    def __init__(
        self,
        path_input_folder: Path,
        USE_EXISTING_TKX_RESULTS: bool,
    ) -> None:
        """Initialize Toolkit instance containing settings and functions related to the Probabilistic Toolkit

        Args:
            path_input_folder (Path): folder containing input files required for creating a fragility curve
            USE_EXISTING_TKX_RESULTS (bool): whether to use precalculated .tkx files (True) or to start new calculations (False)
        """
        self.settings = ToolkitSettings(path_input_folder, USE_EXISTING_TKX_RESULTS)

    def _use_precalculated_results(self, dstability_overview: pd.DataFrame, mapping_tkx_stix: pd.DataFrame) -> None:
        """Executes actions for extracting PTK results from precalculated .tkx files

        Args:
            dstability_overview (pd.DataFrame): overview of D-Stability (.stix) input, models and waterlevels
            mapping_tkx_stix (pd.DataFrame): overview used to find the correct .stix file belonging to a .tkx file
        """
        self.overview = dstability_overview.copy(deep=True)  # Use the overview of the DStability class as basis

        # Combine the overview of the DStability instance and the mapping DataFrame to create one DataFrame
        # that contains all relevant info regarding .stix filepaths, parsed D-Stability models and the
        # corresponding .tkx filepaths.
        self.overview["stix_name"] = self.overview["stix"].apply(lambda x: x["name"])
        self.overview = self.overview.merge(mapping_tkx_stix[["stix_name", "tkx_path"]], on="stix_name", how="left")
        self.overview["tkx"] = self.overview["tkx_path"].apply(lambda tkx: {"path": tkx, "name": tkx.name})
        self.overview.drop(columns=["stix_name", "tkx_path"], inplace=True)

        # Get results from .tkx files and save these as a ToolkitResults object
        self.results = ToolkitResults(self.overview, self.settings.ptk_server_instance)

    def _use_new_calculations(
        self, dstability_overview: pd.DataFrame, path_output_folder: Path, path_work_dir: Path
    ) -> None:
        """Executes actions for creating new .tkx files, starting PTK calculations and extracting the PTK results from the .tkx files

        Args:
            dstability_overview (pd.DataFrame): overview of D-Stability (.stix) input, models and waterlevels
            path_output_folder (Path): path to output folder
            path_work_dir (Path): path to working directory
        """
        self.overview = dstability_overview.copy(deep=True)  # Use the overview of the DStability class as basis
        self.results = self._start_toolkit_calculations(path_output_folder, path_work_dir)

    def _preprocessing_input_tkx(self, path_work_dir: Path) -> list[Path]:
        """Preprocessing actions to prepare the input .tkx files for the calculation process.
        For each .stix in the input folder these actions are carried out:
            - Open template .tkx from the input folder
            - Modify contents of the .tkx (e.g. change path to .stix file used in .tkx)
            - Saves the modified file as a new .tkx in the working directory.

        Args:
            path_work_dir (Path): path to working directory

        Raises:
            ValueError: raised if the preprocessed .tkx file is not valid anymore

        Returns:
            list[Path]: list of paths to the modified .tkx files
        """

        list_paths_modified_tkx = []
        for stix in self.overview["stix"]:

            # Read XML code that makes up the .tkx file
            xml_tree = ET.parse(self.settings.path_template_tkx)

            # Define path of the new .tkx, which will be a copy of the template .tkx
            path_modified_tkx = path_work_dir / f"{stix["path"].stem}.tkx"

            # Carry out actions on XML code
            xml_change_path_stix(xml_tree, new_stix=stix["path"])
            xml_change_work_dir(xml_tree, path_new_work_dir=path_work_dir)
            xml_cleanup_work_dir_after_run(xml_tree, cleanup=False)

            # Write the modified XML to a .tkx file which will be run by the PTK later
            xml_tree.write(path_modified_tkx, encoding="utf-8", xml_declaration=True)

            ### NOTE
            ### Legacy code below for reference
            # Prob. waarden van de input variabelen in de tkx te veranderen
            # # Change values of the input variables of the .tkx

            # Load the modified .tkx
            # tkx_modified = load_tkx_file(self.settings.ptk_server_instance, path_modified_tkx)

            # tkx_copy.model.variables[3].mean = 5

            # # Loop through the attributes of each model variable
            # for idx, var in enumerate(tkx_copy.model.variables):
            #     print(f"Var loop {idx}")

            #     for attr in dir(var):
            #         # Skip special methods and attributes
            #         if not attr.startswith("__"):
            #             # Get the attribute (this could be a method or property)
            #             prop = getattr(var.__class__, attr, None)

            #             # Check if the attribute is a property and has a setter
            #             if isinstance(prop, property) and prop.fset is not None:
            #                 # Set the attribute value of the copied object equal to that of the template tkx
            #                 setattr(tkx_copy.model.variables[idx], attr, getattr(var, attr))
            #                 print(f"Set attr: {attr}")

            # Verander de mean-waarde van ScenarioIndex om zo door de verschillende waterniveaus te loopen. Hierdoor kan je 1 .stix gebruiken ipv losse stix per waterstand. Let op: mogelijk ook CalculationIndex veranderen
            # if var == "ScenarioIndex":
            # tkx_copy.model.variables[index].mean = ...

            # self.ptk_server_instance.save(path_input_tkx)

            # Validate modified tkx and carry out custom checks
            try:
                tkx_project = load_tkx_file(self.settings.ptk_server_instance, path_modified_tkx)
            except ValueError:
                raise ValueError(
                    f"The .tkx file {path_modified_tkx} is not valid anymore after preprocessing modifications!"
                )

            if not tkx_model_factor_in_variables(tkx_project):
                raise ValueError(
                    f"The .tkx file {path_modified_tkx} has no model factor defined in the 'variables' tab. Make sure you enable 'add model factor' under tab Model->Response Parameters and select the correct operation (multiply or divide)"
                )

            if not tkx_model_factor_dist_params_correct(tkx_project):
                raise ValueError(
                    f"The .tkx file {path_modified_tkx} has a variable 'model factor' defined in the 'variables' tab, but it appears that it has incorrect distribution parameters since it's currently deterministic with a value of 1."
                )

            if not tkx_variable_count_correct(tkx_project):
                raise ValueError(
                    f"The .tkx file {path_modified_tkx} has a variable 'model factor' defined in the 'variables' tab, but it appears that it has incorrect distribution parameters since it's currently deterministic with a value of 1."
                )

            list_paths_modified_tkx.append(path_modified_tkx)

        return list_paths_modified_tkx

    def _postprocessing_output_tkx(self) -> None:
        """Postprocessing actions to cleanup output .tkx files where necessary

        Raises:
            ValueError: raised if the postprocessed .tkx file is not valid anymore
        """
        for tkx in self.overview["tkx"]:

            # Read XML code that makes up the .tkx file
            xml_tree = ET.parse(tkx["path"])

            # Reset the working directory that was used in the PTK calculations
            # If this isn't done, the PTK gives a validation error when the
            # (obsolete) work_dir is deleted after the run
            xml_change_work_dir(xml_tree, path_new_work_dir="")

            # Update the .tkx file
            xml_tree.write(tkx["path"], encoding="utf-8", xml_declaration=True)

            # Validate modified tkx
            try:
                load_tkx_file(self.settings.ptk_server_instance, tkx["path"])
            except ValueError:
                raise ValueError(
                    f"The output .tkx file {tkx["path"]} is not valid anymore after postprocessing modifications!"
                )

    def _start_toolkit_calculations(self, path_output_folder, path_work_dir: Path) -> ToolkitResults:
        """Start the PTK calculations and return the calculation results

        Returns:
            ToolkitResults: object that stores PTK calculation results
        """
        # Preprocess the input .tkx files in the working directory before PTK calculations are started
        self.overview["filepath_work_dir_tkx"] = self._preprocessing_input_tkx(path_work_dir)

        # Create overview of output .tkx files that will be created and start calculations
        self.overview["tkx"] = [
            {"path": path_output_folder / temp_tkx.name, "name": temp_tkx.name}
            for temp_tkx in self.overview["filepath_work_dir_tkx"]
        ]
        run_parallel_toolkit_calculations(
            self.settings.ptk_console_path,
            self.overview["filepath_work_dir_tkx"],
            self.overview["tkx"].apply(lambda tkx: tkx["path"]),
        )

        # Postprocess output .tkx files
        self._postprocessing_output_tkx()

        # Drop column with filepaths to .tkx files in working directory since these are not needed anymore
        self.overview.drop("filepath_work_dir_tkx", axis=1, inplace=True)

        return ToolkitResults(self.overview, self.settings.ptk_server_instance)
