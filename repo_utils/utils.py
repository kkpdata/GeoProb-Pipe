import os
from git import Repo, InvalidGitRepositoryError
from typing import Optional
from pathlib import Path


def repository_root_path() -> Optional[str]:

    # Bold guess, it is the execution path
    base_dir = os.getcwd()
    try:
        repo_root = Repo(base_dir, search_parent_directories=False).working_tree_dir
        return repo_root
    except InvalidGitRepositoryError:
        pass

    # Otherwise, search subdirectories
    for subdir, dirs, files in os.walk(os.getcwd()):
        for directory in dirs:
            try:
                repo = Repo(os.path.join(subdir, directory), search_parent_directories=False)
                return repo.working_tree_dir
            except InvalidGitRepositoryError:
                continue

    # Try getcwd
    root_dir: Path = Path(os.getcwd()).parent
    if root_dir.name == "GeoProb-Pipe" and (root_dir / "tests").is_dir():
        return str(root_dir)

    return None
