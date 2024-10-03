from pathlib import Path

import pandas as pd

from app.classes.file_system import FileSystem
from app.classes.toolkit_native_model import ToolkitNative
from app.helper_functions.toolkit_functions import load_tkx_file


class Workspace:
    """Workspace class which handles all actions related to input, output and intermediate working files"""
    
    def __init__(self, PATH_PROJECT_FOLDER: str|Path, USE_EXISTING_TKX_RESULTS: bool) -> None:
        """Initialize Workspace instance

        Args:
            PATH_PROJECT_FOLDER (str | Path): path to the folder that contains all required input and where all output and working files will be stored
            USE_EXISTING_TKX_RESULTS (bool): whether to use precalculated .tkx files (True) or to start new calculations (False)
        """
        self.folderpath = FileSystem.validate_path(PATH_PROJECT_FOLDER)
        
        self.output = _prepare_output_folder(self.folderpath, USE_EXISTING_TKX_RESULTS, checks=True)
        self.input = _prepare_input_folder(self.folderpath, self.output.folderpath, USE_EXISTING_TKX_RESULTS)
        
        if not USE_EXISTING_TKX_RESULTS:
            self.work_dir = _prepare_work_dir(self.folderpath)

    # FIXME update docstring
    def map_precalculated_tkx_input_stix(self, toolkit_server_instance: ToolkitNative) -> None:
        """Obtains path of the .stix files that are used in the precalculated .tkx files

        Args:
            toolkit_server_instance (ToolkitNative): running instance of the PTK server

        Raises:
            FileNotFoundError: raised if a .stix path used in a .tkx file is invalid
            ValueError: raised if a .stix path used in a .tkx file is not located within the 'input' folder of the project folder.
        """
        list_path_precalculated_tkx = []
        list_path_stix = []
        for path_precalculated_tkx in self.output.files["filepath"]:
            path_stix = Path(load_tkx_file(toolkit_server_instance, path_precalculated_tkx).model.input_file)

            try:
                FileSystem.validate_path(path_stix)
            except FileNotFoundError:
                raise FileNotFoundError(
                    f"Output .tkx file {path_precalculated_tkx} refers to a non-existing .stix file ({path_stix})"
                )

            if path_stix.parent != self.input.folderpath:
                raise ValueError(f"""All .stix files used by the output .tkx files should be located in the 'input' folder of the project folder. This is not the case for {path_precalculated_tkx} which refers to {path_stix}.\nMove the .stix files to {self.input.folderpath} and update the references to the .stix in the .tkx files""")

            list_path_precalculated_tkx.append(path_precalculated_tkx)
            list_path_stix.append(path_stix)

        self.mapping_tkx_stix = pd.DataFrame.from_dict(
            {
                "tkx_path": list_path_precalculated_tkx,
                "tkx_name": [tkx.name for tkx in list_path_precalculated_tkx],
                "stix_path": list_path_stix,
                "stix_name": [stix.name for stix in list_path_stix],
            }
        )

    # TODO add docstring
    def update_output_filesystem(self) -> None:
        self.output = _prepare_output_folder(self.folderpath, USE_EXISTING_TKX_RESULTS=True, checks=False)

# TODO add docstring
def _prepare_output_folder(path_project_folder: Path, USE_EXISTING_TKX_RESULTS: bool, checks: bool) -> FileSystem:
    # Create output folder if it didn't exist yet
    if not Path(path_project_folder / "output").exists():
        Path.mkdir(path_project_folder / "output", parents=False, exist_ok=False)
        print(f"INFO: output folder was succesfully created in project folder ({path_project_folder / 'output'})")
    
    # Create FileSystem instance for output folder
    filesystem_output = FileSystem(path_project_folder / "output", "tkx")

    if checks:
        # Perform checks
        if USE_EXISTING_TKX_RESULTS and filesystem_output.files.empty:
            # Raise error if existing PTK calculation results should be used but no .tkx files were found
            raise FileNotFoundError(f"You specified USE_EXISTING_TKX_RESULTS=True meaning that the output folder {filesystem_output.folderpath} should contain .tkx files with results from a previous run. However, no .tkx files were found."
            )
        elif not USE_EXISTING_TKX_RESULTS and not filesystem_output.files.empty:
            # Raise error if new PTK calculations should be started but the found output working folder is not empty
            # Let the user take of this in order to prevent accidental deletion of files.
            raise FileExistsError(
                f"The project folder contains a subfolder 'output' with results from a previous run. Delete (or archive) this folder before you continue: {filesystem_output.folderpath}."
            )
    
    return filesystem_output


# TODO add docstring
def _prepare_input_folder(path_project_folder: Path, path_output_folder: Path, USE_EXISTING_TKX_RESULTS: bool) -> FileSystem:
    
    # Create input folder if it didn't exist yet
    if not Path(path_project_folder / "input").exists():
        Path.mkdir(path_project_folder / "input", parents=False, exist_ok=False)
        print(f"INFO: input folder was succesfully created in project folder ({path_project_folder / 'input'})")
    
    # Create FileSystem instance for input folder
    filesystem_input = FileSystem(path_project_folder / "input")
    
    # Perform checks
    if USE_EXISTING_TKX_RESULTS:
        if len(FileSystem.find_files_in_dir(filesystem_input.folderpath, "stix")) != len(FileSystem.find_files_in_dir(path_output_folder, "tkx")):
            raise FileNotFoundError(
                f"The number of .stix files in the 'input' subfolder should match the number of .tkx files in the 'output' subfolder.\nFiles found:\n{len(FileSystem.find_files_in_dir(filesystem_input.folderpath, "stix"))} .stix files in {filesystem_input.folderpath}\n{len(FileSystem.find_files_in_dir(path_output_folder, "tkx"))} .tkx files in {path_output_folder}" 
            )            
    else:
        if len(FileSystem.find_files_in_dir(filesystem_input.folderpath, "stix")) == 0:
            # Checks if the "input" subfolder contains .stix files
            raise FileNotFoundError(
                f"Input folder {filesystem_input.folderpath} should contain at least 1 .stix file for which you want to carry out a PTK-calculation" 
            )

        if len(FileSystem.find_files_in_dir(filesystem_input.folderpath, "tkx")) != 1:
            # Make sure the "input" subfolder contains 1 .tkx file (= template .tkx)
            raise FileNotFoundError(
                f"Input folder {filesystem_input.folderpath} should contain exactly 1 .tkx file which will be used as template .tkx file for PTK calculations"
            )

    return filesystem_input


# TODO add docstring
def _prepare_work_dir(path_project_folder: Path) -> FileSystem:
    
    # Create working directory if it didn't exist yet
    if not Path(path_project_folder / "_work_dir").exists():
        Path.mkdir(path_project_folder / "_work_dir", parents=False, exist_ok=False)
        print(f"INFO: working folder for intermediate results was succesfully created in project folder ({path_project_folder / '_work_dir'})")
    
    # Create FileSystem object for working folder (intermediate results)
    filesystem_work_dir = FileSystem(path_project_folder / "_work_dir")

    # Perform checks
    if filesystem_work_dir.files.shape[0] != 0:
        # Make sure no files from a previous run are present in the working directory. If this is the case,
        # let the user take of this in order to prevent accidental deletion of files.
        raise FileExistsError(
            f"Project folder {path_project_folder} contains a subfolder '_work_dir' with intermediate files from a previous run. Delete (or archive) this folder before you continue."
        )
    
    return filesystem_work_dir
