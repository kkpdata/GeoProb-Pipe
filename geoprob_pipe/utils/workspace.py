# from pathlib import Path
# from typing import Tuple
# import pandas as pd
# from geoprob_pipe.utils.file_system import FileSystem
# from datetime import datetime
# import logging


# class Workspace:
#     """Workspace class which handles all actions related to input, output and intermediate working files"""
#
#     def __init__(self, path_workspace: str | Path) -> None:
#         """Initialize Workspace instance
#
#         Args:
#             path_workspace (str | Path): path to the folder that contains all required input and where all output and
#                 working files will be stored
#         """
#         self.folderpath = FileSystem.validate_path(path_workspace)
#         self.path_output_folder = _prepare_output_folder(self.folderpath)
#         self.input, self.path_input_excel, self.path_hrd = _prepare_input_folder(self.folderpath)
#         # TODO Later Could Groot: Add functionality to read existing results (without running prob. calculations again)
#         logger.info("Workspace (I/O folders) successfully processed.")
#
#     def update_output_filesystem(self) -> None:
#         """
#         Update the output subfolder FileSystem instance (to include new calculation results)
#         """
#         self.path_output_folder = _prepare_output_folder(self.folderpath)


# def _prepare_output_folder(path_workspace: Path) -> FileSystem:
#     """ Prepare output subfolder
#
#     Args:
#         path_workspace (Path): path to the folder that contains all required input and where all output and working
#             files will be stored
#
#     Raises:
#         FileNotFoundError: raised if USE_EXISTING_TKX_RESULTS=True but the output subfolder contains no .tkx files
#         FileExistsError: raised if USE_EXISTING_TKX_RESULTS=False but the output subfolder still contains .tkx files
#             from a previous run
#
#     Returns:
#         FileSystem: _description_
#     """
#     timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
#     export_path = path_workspace / "output" / timestamp
#     export_path.mkdir(exist_ok=False, parents=True)
#     logger.info(f"Output folder was successfully created in workspace folder: output/{timestamp}/.")
#     return FileSystem(export_path)


# def _prepare_input_folder(path_workspace: Path) -> Tuple[FileSystem, Path, Path]:
#
#     """Prepare input subfolder
#
#     Args:
#         path_workspace (Path): path to the folder that contains all required input and where all output and working
#             files will be stored
#
#     Raises:
#         FileNotFoundError: raised if USE_EXISTING_TKX_RESULTS=True but the number of .stix files in the input subfolder
#             don't match the number of .tkx files in the output subfolder
#         FileNotFoundError: raised if USE_EXISTING_TKX_RESULTS=False but the input subfolder contains no .stix files
#         FileNotFoundError: raised if USE_EXISTING_TKX_RESULTS=False but the input subfolder contains no template .tkx
#             file
#
#     Returns:
#         FileSystem: FileSystem instance which creates a convenient overview of the input subfolder and the files within it
#     """
#     # Create input folder if it didn't exist yet
#     if not Path(path_workspace / "input").exists():
#         Path.mkdir(path_workspace / "input", parents=False, exist_ok=False)
#         print(f"INFO: input folder was successfully created in project folder ({path_workspace / 'input'})")
#
#     # Create FileSystem instance for input folder
#     filesystem_input = FileSystem(path_workspace / "input")
#
#     # Make sure the "input" subfolder contains 1 .xlsx file named input.xlsx
#     xlsx_input = [filepath.name
#                   for filepath in FileSystem.find_files_in_dir(filesystem_input.folderpath, "xlsx")]
#
#     if len(xlsx_input) != 1 or xlsx_input[0] != "input.xlsx":
#         raise FileNotFoundError(
#             f"\nInput folder {filesystem_input.folderpath} should contain exactly 1 .xlsx files named 'input.xlsx'\n"
#             f"(Currently found: {xlsx_input})"
#         )
#
#     # Check if input.xlsx has exactly four required sheets (case-sensitive!)
#     expected_sheets = {"Vakken", "Uittredepunten", "Ondergrondscenarios", "Overzicht_parameters", "Settings"}
#     xlsx_input_folderpath = pd.ExcelFile(filesystem_input.folderpath / "input.xlsx")
#
#     if set(xlsx_input_folderpath.sheet_names) != expected_sheets:
#         raise FileNotFoundError(
#             f"\n{filesystem_input.folderpath / 'input.xlsx'} should contain exactly these sheets:\n"
#             f"{', '.join(expected_sheets)}\n"
#             f"Found sheets: {', '.join(xlsx_input_folderpath.sheet_names)}\n"
#             f"Note:\n1) Sheet names are case-sensitive!\n2) The order of sheets does not matter."
#         )
#
#     # Find HRD path
#     hrd_matches = filesystem_input.files.loc[
#         lambda df: df["filename"].str.endswith(".sqlite") &
#                 (df["filename"] != "hlcd.sqlite") &
#                 ~df["filename"].str.endswith(".config.sqlite")
#     ]
#     # The .zip files containing HRD have multiple .sqlite files, but we only want the one that ends with .sqlite (not
#     # ending with .config.sqlite) and is not called 'hlcd.sqlite'
#
#     if len(hrd_matches) != 1:
#         if len(hrd_matches) > 1:
#             filepaths = ', '.join(hrd_matches["filepath"].tolist())
#             raise ValueError(f"Expected exactly one matching HRD .sqlite file, but found {len(hrd_matches)}:\n{filepaths}")
#         else:
#             raise ValueError("One HRD .sqlite file is required in the input folder, but none was found.")
#
#     hrd_path = hrd_matches["filepath"].iloc[0]
#
#     return filesystem_input, filesystem_input.folderpath / "input.xlsx", hrd_path
