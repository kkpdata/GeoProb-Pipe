import os
import subprocess
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from pathlib import Path

import pandas as pd

from app.classes.toolkit_native_model import ToolkitNative, ToolkitProject
from app.helper_functions.toolkit_native_functions import SERVER_PORT, CheckConnection


def load_tkx_file(toolkit_server_instance: ToolkitNative, path_tkx: Path) -> ToolkitProject:
    """Load .tkx file using the PTK server executable (Deltares.Probabilistic.Server.exe)

    Args:
        toolkit_server_instance (ToolkitNative): instance of PTK server executable
        path_tkx (Path): path to .tkx file

    Raises:
        ConnectionError: raised if the .tkx file for some reason couldn't be loaded
        ValueError: raised if .tkx file is invalid

    Returns:
        ToolkitProject: parsed .tkx model (ToolkitProject instance)
    """
    try:
        tkx_project = toolkit_server_instance.load(path_tkx)
    except:
        raise ConnectionError(f"The PTK server couldn't load .tkx file for unknown reasons: {path_tkx}.")

    # Validate tkx
    if not tkx_project.validate() == "ok":
        raise ValueError(f"Invalid .tkx file: {path_tkx}\nError message: {tkx_project.validate()}")

    return tkx_project


def run_console(PATH_PTK_CONSOLE: Path, path_input_tkx: Path, path_output_tkx: Path) -> None:
    """Function to run the executable for a given input/output pair of .tkx files
       The PTK console is run using this command in a command line (cmd):
       Deltares.Probabilistic.Console.exe InputFile.tkx OutputFile.tkx

    Args:
        PATH_PTK_CONSOLE (Path): path to the .exe of the PTK console ("Deltares.Probabilistic.Console.exe")
        path_input_tkx (Path): path to input tkx
        path_output_tkx (Path): path to output tkx
    """
    process = subprocess.Popen(
        f'"{PATH_PTK_CONSOLE.resolve()}" "{path_input_tkx.resolve()}" "{path_output_tkx.resolve()}"',
        shell=True,
    )

    process.wait()  # Block the code until the command prompt process is finished

    ### NOTE
    ### Legacy code below for reference
    ### NOTE subprocess.run in combination with "start cmd" doesnt block the code!
    # subprocess.run(
    #     f'start cmd /k ""{PATH_PTK_CONSOLE.resolve()}" "{path_input_tkx.resolve()}" "{path_output_tkx.resolve()}"',
    #     shell=True,
    # )
    # Legacy code:
    # subprocess.run(
    #     f'"{PATH_PTK_CONSOLE.resolve()}" "{path_input_tkx.resolve()}" "{path_output_tkx.resolve()}"',
    #     shell=True,
    # )


def run_parallel_toolkit_calculations(
    path_ptk_console: Path, series_path_work_dir_tkx: pd.Series, series_path_output_tkx: pd.Series
) -> None:
    """Execute multiple Probabilistic Toolkit calculations in parallel

    Args:
        path_ptk_console (Path): path to the .exe of the PTK console ("Deltares.Probabilistic.Console.exe")
        series_path_work_dir_tkx (pd.Series): paths of .tkx files in the working directory that will be calculated
        series_path_output_tkx (pd.Series): paths of the new output .tkx files that contain the calculation results

    Raises:
        ValueError: raised if for some reason the .tkx files could not be calculated in parallel.
    """

    if os.cpu_count() > 1:  # type: ignore
        # Use all cores but reserve one for OS processes
        max_workers = os.cpu_count() - 1  # type: ignore
    else:
        max_workers = 1
        print("WARNING: only 1 CPU was found. Therefore, the calculations are not performed in parallel")

    print(
        f"""\nStarting a total of {len(series_path_work_dir_tkx)} PTK calculations using (a maximum of) {max_workers} CPU cores/threads! This can take a long time depending on the number of available CPUs and their performance. Indication: 1-20 hours per calculation.\nIf you want to make sure the calculation is still running, check for the process 'D-Stability Console' in your task manager and check if files are being created/modified in the working direcotry: {Path(series_path_work_dir_tkx.iloc[0].parent)}"""
    )

    try:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            executor.map(
                run_console,
                [Path(path_ptk_console)] * len(series_path_work_dir_tkx),
                series_path_work_dir_tkx,
                series_path_output_tkx,
            )
    except:
        raise ValueError(".tkx files could not be calculated in parallel")


def find_and_terminate_toolkit_server(server_port: int) -> None:
    """Make sure no old instance of the Probabilistic Toolkit server is running

    Args:
        server_port (int): port on which the Probabilistic Toolkit server is running (hardcoded)
    """
    command = f"netstat -ano | findstr :{server_port}"
    result = os.popen(command).read().strip()

    if result:
        # If result is not empty, a previous PTK server instance is still running
        lines = result.splitlines()
        for line in lines:
            parts = line.strip().split()
            if parts[-2] == "LISTENING":
                # The PID that is in state "LISTENING" is the Probabilistic Toolkit server. Terminate the corresponding process ID (PID)
                os.system(f"taskkill /F /PID {parts[-1]}")
                print(
                    f"Terminated previous PTK server instance with PID {parts[-1]} on port {server_port}. Starting up new server."
                )


def start_toolkit_server(path_ptk_server: Path) -> ToolkitNative:
    """Start a toolkit server instance.

    Note: only 1 server can be run at the same time. Multiple instances are not possible
    since the server's .exe is hardcoded to only use port 11178. Parallelization is therefore not possible

    Before starting a server instance, first find the previous instance of the Probabilistic Toolkit server
    if it exist and terminate it to make sure the script has a working server instance

    Args:
        path_ptk_server (Path): path to PTK server executable (Deltares.Probabilistic.Server.exe).

    Raises:
        ConnectionError: raised if no connection could be made to the PTK server instance after the number of seconds specified in TIME_THRESHOLD

    Returns:
        ToolkitNative: Toolkit object (PTK native class, comes pre-installed with the PTK)
    """
    TIME_THRESHOLD = 300  # Seconds

    find_and_terminate_toolkit_server(SERVER_PORT)

    toolkit_server_instance = ToolkitNative(path_ptk_server)
    print(
        "\nServer of the Probabilistic Toolkit is starting up. Warnings shown in the command prompt regarding missing/invalid license files can be ignored."
    )

    start_time = datetime.now()
    while not CheckConnection() and (datetime.now() - start_time).seconds <= TIME_THRESHOLD:
        time.sleep(1)

    if not CheckConnection():
        raise ConnectionError("No connection with the PTK server could be established.")
    else:
        return toolkit_server_instance


def xml_change_path_stix(xml_tree: ET.ElementTree, new_stix: Path) -> None:
    """Function to change the reference to the .stix file in the new .tkx file.
    This can be done using the PTK server, but doing so resets the input variables.
    Since we want to keep the input variables the same, we can change just the .stix reference
    by modifying the corresponding element in the XML-code which makes up a .tkx file.

    Args:
        xml_tree (ET.ElementTree): XML element hierarchy of .tkx file
        new_stix (Path): path to the .stix file that should be used in the new input .tkx

    Raises:
        ValueError: raised if the element which should be modified in the XML-code of the .tkx is not found
    """

    # Navigate to the ModelData element
    model_data = xml_tree.getroot().find(".//ModelData")

    # Check if ModelData exists
    if model_data is None:
        raise ValueError("Could not change the .stix in the .tkx because the element 'ModelData' was not found.")

    # Modify the InputFileInfo attribute of the ModelData element
    model_data.set("InputFileInfo", str(new_stix))
    print(
        "Info: a different .stix was assigned the .tkx. Make sure that the variable names in the new .stix (e.g. soil names) are identical to those used in the .stix of the template .tkx"
    )


def xml_change_work_dir(xml_tree: ET.ElementTree, path_new_work_dir: str | Path) -> None:
    """Change the path in the .tkx to the working directory used during the PTK calculations. By passing an empty string (i.e. "") resets this path

    Args:
        xml_tree (ET.ElementTree): XML code of .tkx file
        path_new_work_dir (str | Path): path of the new working directory. An empty string (i.e. "") resets this path

    Raises:
        ValueError: raised if this setting could not be found in the XML code of the .tkx
    """
    # Navigate to the ModelData element
    model_data = xml_tree.getroot().find(".//ModelData")

    # Check if ModelData exists
    if model_data is None:
        raise ValueError(
            "Could not change the working directory in the .tkx because the element 'ModelData' was not found."
        )

    # Make sure RunSameDirectory is set to "False"
    model_data.set("RunSameDirectory", "False")

    # Set RunDirectoryInfo to the working directory.
    # Note that if the XML code does not contain RunDirectoryInfo yet, it will automatically added
    model_data.set("RunDirectoryInfo", str(path_new_work_dir))


def xml_cleanup_work_dir_after_run(xml_tree: ET.ElementTree, cleanup: bool) -> None:
    """Enable/disable option in .tkx file to automatic cleanup the working directory after running the PTK calculation

    Args:
        xml_tree (ET.ElementTree): XML code of .tkx file
        cleanup (bool): yes (True) or no (False)

    Raises:
        ValueError: raised if this setting could not be found in the XML code of the .tkx
    """
    # Navigate to the ModelData element
    model_data = xml_tree.getroot().find(".//ModelData")

    # Check if ModelData exists
    if model_data is None:
        raise ValueError(
            "Could not toggle the 'CleanUpFiles' setting in the .tkx because the element 'ModelData' was not found."
        )

    if cleanup:
        model_data.set("CleanUpFiles", "True")
    else:
        model_data.set("CleanUpFiles", "False")


def tkx_model_factor_in_variables(tkx_projet: ToolkitProject) -> bool:
    """Check if the model factor is included in the variables of the .tkx

    Args:
        tkx_projet (ToolkitProject): (ToolkitProject): parsed .tkx model (ToolkitProject instance)

    Returns:
        bool: True if the model factor is included in the variables of the .tkx, False if this is not the case
    """
    if "Model.Factor" in [var.name for var in tkx_projet.model.variables]:
        return True
    else:
        return False


def tkx_model_factor_dist_params_correct(tkx_projet: ToolkitProject) -> bool:
    """Check if the distribution parameters of the model factor are correctly defined in the .tkx

    Args:
        tkx_projet (ToolkitProject): parsed .tkx model (ToolkitProject instance)

    Returns:
        bool: True if the distribution parameters of the model factor are correctly defined in the .tkx, False if this is (likely) not the case
    """
    if (
        tkx_projet.model.get_variable("Model.Factor").distribution == "Deterministic"
        and tkx_projet.model.get_variable("Model.Factor").mean == 1
    ):
        # If the model factor has default distribution parameters (deterministic with a value of 1),
        # it is very likely that the user didn't correctly change these.
        return False
    else:
        return True


def tkx_variable_count_correct(tkx_projet: ToolkitProject) -> bool:
    """Check whether the number of variables defined in the .tkx are correct

    A .tkx file set up in "Application: D-Stability" mode contains by default the variables 'ScenarioIndex' and
    'CalculationIndex'. Due to previous checks in the tool, the .tkx also contains 'Model.Factor' as default variable.
    In order to carry out meaningful calculations, one should add additional variables (e.g. distribution of soil
    strength parameters). This function therefore checks whether there are more variables present than the 3 default variables.

    Args:
        tkx_projet (ToolkitProject): parsed .tkx model (ToolkitProject instance)

    Returns:
        bool: True if the number of variables present is correct/credible, False if it is likely that the user forgot to define additional variables
    """
    set_default_variables = set(["ScenarioIndex", "CalculationIndex", "Model.Factor"])
    set_variables_presents_tkx = set([var.name for var in tkx_projet.model.variables])
    if len(set_variables_presents_tkx - set_default_variables) > 0:
        return True
    else:
        return False
