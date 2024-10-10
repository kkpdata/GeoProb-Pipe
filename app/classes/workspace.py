from pathlib import Path

import pandas as pd

from app.classes.file_system import FileSystem
from app.classes.toolkit_native_model import ToolkitNative
from app.helper_functions.toolkit_functions import load_tkx_file


class Workspace:
    """Workspace class which handles all actions related to input, output and intermediate working files"""

    def __init__(self, PATH_WORKSPACE: str | Path, USE_EXISTING_TKX_RESULTS: bool) -> None:
        """Initialize Workspace instance

        Args:
            PATH_WORKSPACE (str | Path): path to the folder that contains all required input and where all output and working files will be stored
            USE_EXISTING_TKX_RESULTS (bool): whether to use precalculated .tkx files (True) or to start new calculations (False)
        """
        self.folderpath = FileSystem.validate_path(PATH_WORKSPACE)

        self.output = _prepare_output_folder(self.folderpath, USE_EXISTING_TKX_RESULTS)
        self.input = _prepare_input_folder(self.folderpath, USE_EXISTING_TKX_RESULTS)

        if not USE_EXISTING_TKX_RESULTS:
            self.work_dir = _prepare_work_dir(self.folderpath)


def _prepare_output_folder(PATH_WORKSPACE: Path, USE_EXISTING_TKX_RESULTS: bool) -> FileSystem:
    """Prepare output subfolder

    Args:
        PATH_WORKSPACE (Path): path to the folder that contains all required input and where all output and working files will be stored
        USE_EXISTING_TKX_RESULTS (bool): whether to use precalculated .tkx files (True) or to start new calculations (False)

    Raises:
        FileNotFoundError: raised if USE_EXISTING_TKX_RESULTS=True and the output subfolder contains no .tkx files
        FileExistsError: raised if USE_EXISTING_TKX_RESULTS=False and the output subfolder still contains .tkx files from a previous run

    Returns:
        FileSystem: FileSystem instance which creates a convenient overview of the output subfolder and the files within it
    """
    # Create output folder if it didn't exist yet
    if not Path(PATH_WORKSPACE / "output").exists():
        Path.mkdir(PATH_WORKSPACE / "output", parents=False, exist_ok=False)
        print(f"INFO: output folder was succesfully created in project folder ({PATH_WORKSPACE / 'output'})")

    # Create FileSystem instance for output folder
    filesystem_output = FileSystem(PATH_WORKSPACE / "output", "tkx")

    # Perform checks
    if USE_EXISTING_TKX_RESULTS and filesystem_output.files.empty:
        # Raise error if existing PTK calculation results should be used but no .tkx files were found
        raise FileNotFoundError(
            f"You specified USE_EXISTING_TKX_RESULTS=True meaning that the output folder {filesystem_output.folderpath} should contain .tkx files with results from a previous run. However, no .tkx files were found."
        )
    elif not USE_EXISTING_TKX_RESULTS and not filesystem_output.files.empty:
        # Raise error if new PTK calculations should be started but the found output working folder is not empty
        # Let the user take of this in order to prevent accidental deletion of files.
        raise FileExistsError(
            f"The project folder contains a subfolder 'output' with results from a previous run. Delete (or archive) this folder before you continue: {filesystem_output.folderpath}."
        )

    return filesystem_output


def _prepare_input_folder(PATH_WORKSPACE: Path, USE_EXISTING_TKX_RESULTS: bool) -> FileSystem:
    """Prepare input subfolder

    Args:
        PATH_WORKSPACE (Path): path to the folder that contains all required input and where all output and working files will be stored
        USE_EXISTING_TKX_RESULTS (bool): whether to use precalculated .tkx files (True) or to start new calculations (False)

    Raises:
        FileNotFoundError: raised if the input subfolder contains no GeoDataBase (.gdb)
        FileNotFoundError: raised if USE_EXISTING_TKX_RESULTS=False and the input subfolder contains no template .tkx file

    Returns:
        FileSystem: FileSystem instance which creates a convenient overview of the input subfolder and the files within it
    """
    # Create input folder if it didn't exist yet
    if not Path(PATH_WORKSPACE / "input").exists():
        Path.mkdir(PATH_WORKSPACE / "input", parents=False, exist_ok=False)
        print(f"INFO: input folder was succesfully created in project folder ({PATH_WORKSPACE / 'input'})")

    # Create FileSystem instance for input folder
    filesystem_input = FileSystem(PATH_WORKSPACE / "input")

    # Perform checks
    if len(FileSystem.find_files_in_dir(filesystem_input.folderpath, "gdb")) != 1:
        # Note: a .gdb in the input subfolder is not really necessary if we're simply showing previously run PTK results (USE_EXISTING_TKX_RESULTS=True),
        # but it's good practice to force the user to keep the input/output files together in order to improve traceability of input/output combinations.
        raise FileNotFoundError(f"The 'input' subfolder should contain exactly 1 GeoDataBase (.gdb)")

    if not USE_EXISTING_TKX_RESULTS and len(FileSystem.find_files_in_dir(filesystem_input.folderpath, "tkx")) == 1:
        # Make sure the "input" subfolder contains 1 .tkx file (= template .tkx)
        raise FileNotFoundError(
            f"Input folder {filesystem_input.folderpath} should contain exactly 1 .tkx file which will be used as template .tkx file for PTK calculations"
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
