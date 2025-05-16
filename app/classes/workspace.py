from pathlib import Path

import pandas as pd

from app.classes.file_system import FileSystem


# FIXME docstring
# FIXME add functionality to read existing results (without running prob. calculations again)
class Workspace:
    """Workspace class which handles all actions related to input, output and intermediate working files"""

    def __init__(self, PATH_WORKSPACE: str | Path) -> None:
        """Initialize Workspace instance

        Args:
            PATH_WORKSPACE (str | Path): path to the folder that contains all required input and where all output and working files will be stored
        """
        self.folderpath = FileSystem.validate_path(PATH_WORKSPACE)

        self.output = _prepare_output_folder(self.folderpath, checks=True)
        self.input = _prepare_input_folder(self.folderpath, self.output.folderpath)

        # FIXME add functionality to read existing results (without running prob. calculations again)
        # self.output = _prepare_output_folder(self.folderpath, USE_EXISTING_TKX_RESULTS, checks=True)
        # self.input = _prepare_input_folder(self.folderpath, self.output.folderpath, USE_EXISTING_TKX_RESULTS)

        # if not USE_EXISTING_TKX_RESULTS:
        #     self.work_dir = _prepare_work_dir(self.folderpath)


    def update_output_filesystem(self) -> None:
        """
        Update the output subfolder FileSystem instance (to include new calculation results)
        """
        self.output = _prepare_output_folder(self.folderpath, checks=False)


# FIXME docstring
def _prepare_output_folder(PATH_WORKSPACE: Path, checks: bool) -> FileSystem:
# def _prepare_output_folder(PATH_WORKSPACE: Path, USE_EXISTING_TKX_RESULTS: bool, checks: bool) -> FileSystem:
    """Prepare output subfolder

    Args:
        PATH_WORKSPACE (Path): path to the folder that contains all required input and where all output and working files will be stored
        USE_EXISTING_TKX_RESULTS (bool): whether to use precalculated .tkx files (True) or to start new calculations (False)
        checks (bool): whether to carry out checks on the output subfolder (only when the output subfolder is initialized, not when updating the FileSystem instance of the output subfolder after generating new results)

    Raises:
        FileNotFoundError: raised if USE_EXISTING_TKX_RESULTS=True but the output subfolder contains no .tkx files
        FileExistsError: raised if USE_EXISTING_TKX_RESULTS=False but the output subfolder still contains .tkx files from a previous run

    Returns:
        FileSystem: _description_
    """
    # Create output folder if it didn't exist yet
    if not Path(PATH_WORKSPACE / "output").exists():
        Path.mkdir(PATH_WORKSPACE / "output", parents=False, exist_ok=False)
        print(f"INFO: output folder was succesfully created in project folder ({PATH_WORKSPACE / 'output'})")

    # FIXME extension of output files is not correct (shouldn't be .tkx)
    # Create FileSystem instance for output folder
    filesystem_output = FileSystem(PATH_WORKSPACE / "output", "tkx")
    
    # FIXME customize checks for STPH files
    # if checks:
    #     # Perform checks
    #     if USE_EXISTING_TKX_RESULTS and filesystem_output.files.empty:
    #         # Raise error if existing PTK calculation results should be used but no .tkx files were found
    #         raise FileNotFoundError(
    #             f"You specified USE_EXISTING_TKX_RESULTS=True meaning that the output folder {filesystem_output.folderpath} should contain .tkx files with results from a previous run. However, no .tkx files were found."
    #         )
    #     elif not USE_EXISTING_TKX_RESULTS and not filesystem_output.files.empty:
    #         # Raise error if new PTK calculations should be started but the found output working folder is not empty
    #         # Let the user take of this in order to prevent accidental deletion of files.
    #         raise FileExistsError(
    #             f"You specified USE_EXISTING_TKX_RESULTS=False, meaning new calculations will be run. The project folder contains a subfolder 'output' with results from a previous run. Delete (or archive) this folder before you continue: {filesystem_output.folderpath}."
    #         )

    return filesystem_output

# FIXME docstring
def _prepare_input_folder(PATH_WORKSPACE: Path, path_output_folder: Path) -> FileSystem:

    """Prepare input subfolder

    Args:
        PATH_WORKSPACE (Path): path to the folder that contains all required input and where all output and working files will be stored
        path_output_folder (Path): path to the output subfolder
        USE_EXISTING_TKX_RESULTS (bool): whether to use precalculated .tkx files (True) or to start new calculations (False)

    Raises:
        FileNotFoundError: raised if USE_EXISTING_TKX_RESULTS=True but the number of .stix files in the input subfolder don't match the number of .tkx files in the output subfolder
        FileNotFoundError: raised if USE_EXISTING_TKX_RESULTS=False but the input subfolder contains no .stix files
        FileNotFoundError: raised if USE_EXISTING_TKX_RESULTS=False but the input subfolder contains no template .tkx file

    Returns:
        FileSystem: FileSystem instance which creates a convenient overview of the input subfolder and the files within it
    """
    # Create input folder if it didn't exist yet
    if not Path(PATH_WORKSPACE / "input").exists():
        Path.mkdir(PATH_WORKSPACE / "input", parents=False, exist_ok=False)
        print(f"INFO: input folder was succesfully created in project folder ({PATH_WORKSPACE / 'input'})")

    # Create FileSystem instance for input folder
    filesystem_input = FileSystem(PATH_WORKSPACE / "input")

    # Make sure the "input" subfolder contains 1 .xlsx file named input.xlsx
    xlsx_input = [filepath.name for filepath in FileSystem.find_files_in_dir(filesystem_input.folderpath, "xlsx")]

    if len(xlsx_input) != 1 or xlsx_input[0] != "input.xlsx":
        raise FileNotFoundError(
            f"\nInput folder {filesystem_input.folderpath} should contain exactly 1 .xlsx files named 'input.xlsx'\n(Currently found: {xlsx_input})"
        )

    # Check if input.xlsx has exactly four required sheets (case-sensitive!)
    expected_sheets = {"Vakken", "Uittredepunten", "Ondergrondscenarios", "Overzicht_parameters", "Settings"}
    xlsx_input_folderpath = pd.ExcelFile(filesystem_input.folderpath / "input.xlsx")

    if set(xlsx_input_folderpath.sheet_names) != expected_sheets:
        raise FileNotFoundError(
            f"\n{filesystem_input.folderpath / 'input.xlsx'} should contain exactly these sheets"
            f"{', '.join(expected_sheets)}\n"
            f"Found sheets: {', '.join(xlsx_input_folderpath.sheet_names)}\n"
            f"Note:\n1) Sheet names are case-sensitive!\n2) The order of sheets does not matter."
        )
        
    return filesystem_input


def _prepare_work_dir(PATH_WORKSPACE: Path) -> FileSystem:
    """Prepare working directory in which intermediate files are stored.

    Args:
        PATH_WORKSPACE (Path): path to the folder that contains all required input and where all output and working files will be stored

    Raises:
        FileExistsError: raised if the working directory still contains files from a previous run

    Returns:
        FileSystem: FileSystem instance which creates a convenient overview of the working directory and the files within it
    """
    # Create working directory if it didn't exist yet
    if not Path(PATH_WORKSPACE / "_work_dir").exists():
        Path.mkdir(PATH_WORKSPACE / "_work_dir", parents=False, exist_ok=False)
        print(
            f"INFO: working folder for intermediate results was succesfully created in project folder ({PATH_WORKSPACE / '_work_dir'})"
        )

    # Create FileSystem object for working folder (intermediate results)
    filesystem_work_dir = FileSystem(PATH_WORKSPACE / "_work_dir")

    # Perform checks
    if filesystem_work_dir.files.shape[0] != 0:
        # Make sure no files from a previous run are present in the working directory. If this is the case,
        # let the user take of this in order to prevent accidental deletion of files.
        raise FileExistsError(
            f"Project folder {PATH_WORKSPACE} contains a subfolder '_work_dir' with intermediate files from a previous run. Delete (or archive) this folder before you continue."
        )

    return filesystem_work_dir
