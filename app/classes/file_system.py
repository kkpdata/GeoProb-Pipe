from pathlib import Path
from typing import Optional

import pandas as pd


class FileSystem:
    """FileSystem class which creates a convenient overview of a given folder and the files within it"""

    def __init__(self, path_folder: str | Path, extension: Optional[str] = None) -> None:
        """Initialize FileSystem instance which creates a convenient overview of a given folder and the files within it

        Args:
            path_folder (str | Path): path of folder for which a FileSystem instance will be created
            extension (Optional[str], optional): extension of specific files to include in the FileSystem instance. Defaults to None, which returns all files path_folder regardless of extension.
        """
        self.folderpath = self.validate_path(path_folder)

        self.files = pd.DataFrame()
        self.files["filepath"] = self.find_files_in_dir(self.folderpath, extension)
        self.files["filename"] = [file.name for file in self.files["filepath"]]

        self.subfolders = pd.DataFrame()
        self.subfolders["subfolderpath"] = self.find_subfolders(self.folderpath)
        self.subfolders["subfoldername"] = [folder.name for folder in self.subfolders["subfolderpath"]]

    @staticmethod
    def validate_path(path_to_check: str | Path) -> Path:
        """Checks if the given path exists

        Args:
            path_to_check (str | Path): path to either a file or a folder

        Raises:
            FileNotFoundError: raised if the file/folder was not found

        Returns:
            Path: Path object for the validated path
        """
        if not Path(path_to_check).exists():
            raise FileNotFoundError(f"Path {path_to_check} doesn't exist")
        else:
            return Path(path_to_check).resolve()

    @staticmethod
    def find_files_in_dir(dir: str | Path, extension: str | None = None) -> list[Path]:
        """Find all files with a specified extension in a folder
        Note: files starting with ~$ are ignored since these are generally temporary files

        Args:
            dir (str | Path): folder to search in
            extension (str, None): extension without the dot (e.g. "txt" instead of ".txt").
                                   If None is passed all files in dir, regarless of extension, are returned

        Returns:
            list[Path]: list of paths to the found files in the dir. Returns None if no files were found.
        """
        if isinstance(extension, str):
            files = [file for file in Path(dir).resolve().glob(f"*.{extension}") if file.is_file() and not file.name.startswith("~$")]
        else:
            files = [file for file in Path(dir).resolve().glob(f"*") if file.is_file() and not file.name.startswith("~$")]
        return files

    @staticmethod
    def find_subfolders(dir: str | Path) -> list[Path]:
        """Find all subfolders within a parent folder

        Args:
            dir (str | Path): folder to search in

        Returns:
            list[Path]: list of paths to the found subfolders in the dir.
        """
        return [subfolder for subfolder in Path(dir).iterdir() if subfolder.is_dir()]
