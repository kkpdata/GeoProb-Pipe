import os
from git import Repo, InvalidGitRepositoryError
from typing import Optional


def find_repo_root():
    """ Alternative version to repository_root_path, which does not always seem to work in PyTest. """
    from pathlib import Path
    import subprocess
    return Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())


def repository_root_path() -> Optional[str]:

    # Bold guess, it is the execution path
    base_dir = os.getcwd()
    print(f"{base_dir=}")
    try:
        print(f"Now trying Repo-class")
        repo_root = Repo(base_dir, search_parent_directories=False).working_tree_dir
        print(f"From Repo-class {repo_root=}")
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
        return None
    return None
