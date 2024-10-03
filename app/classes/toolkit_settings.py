from pathlib import Path

from app.classes.file_system import FileSystem
from app.helper_functions.toolkit_functions import load_tkx_file, start_toolkit_server


class ToolkitSettings:
    "ToolkitSettings class containing settings related to the Probabilistic Toolkit"

    DEFAULT_PTK_PATH_CONSOLE = (
        r"C:\Program Files (x86)\Deltares\Probabilistic Toolkit\bin\Deltares.Probabilistic.Console.exe"
    )
    DEFAULT_PTK_PATH_SERVER = (
        r"C:\Program Files (x86)\Deltares\Probabilistic Toolkit\bin\Deltares.Probabilistic.Server.exe"
    )

    def __init__(self, path_input_folder: Path, USE_EXISTING_TKX_RESULTS: bool) -> None:
        """Initialize ToolkitSettings instance containing settings related to the Probabilistic Toolkit

        Args:
            path_input_folder (Path): folder containing input files required for creating a fragility curve
            USE_EXISTING_TKX_RESULTS (bool): whether to use precalculated .tkx files (True) or to start new calculations (False)

        Raises:
            FileNotFoundError: raised if the default path to the server of the PTK is not found
            FileNotFoundError: raised if the default path to the console of the PTK is not found
        """
        self.use_existing_tkx_results = USE_EXISTING_TKX_RESULTS  # Store setting for future reference

        # Start PTK server
        try:
            self.ptk_server_path = FileSystem.validate_path(self.__class__.DEFAULT_PTK_PATH_SERVER)
            self.ptk_server_instance = start_toolkit_server(self.ptk_server_path)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Default path to the server of the Probabilistic Toolkit doesn't exist: {self.__class__.DEFAULT_PTK_PATH_SERVER}"
            )

        if not self.use_existing_tkx_results:
            # Load template .tkx file. Note: the tool already checked if there is only 1 .tkx file
            # (= template .tkx) present in the input folder
            self.path_template_tkx = FileSystem.find_files_in_dir(path_input_folder, "tkx")[0]
            load_tkx_file(self.ptk_server_instance, self.path_template_tkx)

            # Validate PTK console path
            try:
                self.ptk_console_path = FileSystem.validate_path(self.__class__.DEFAULT_PTK_PATH_CONSOLE)
            except FileNotFoundError:
                raise FileNotFoundError(
                    f"Default path to the console of the Probabilistic Toolkit doesn't exist: {self.__class__.DEFAULT_PTK_PATH_CONSOLE}"
                )
