import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))  # Add repo to sys.path to make sure all imports are correctly found

from app.classes.project import Project

# ====================================
# User Input Section
# ====================================

# Define path to workspace (either absolute or relative)
PATH_WORKSPACE: str | Path = r"..\\workspaces\example_new_calculations"

#FIXME implement feature to re-use existing results
# # Whether existing calculation results should be used
# # If True, the .tkx files that are found the "PATH_WORKSPACE/output" folder are used
# USE_EXISTING_TKX_RESULTS: bool = False

# Whether to clean up the working directory in the workspace (True) or not (False).
# FIXME not implemented, perhaps not necessary
CLEANUP_WORK_DIR: bool = True


# ====================================
# End of User Input Section
# ====================================


def start_tool(
    PATH_WORKSPACE: str | Path,
) -> Project:
    """Start PTK tool
    Args:
        PATH_WORKSPACE: path to the folder that contains all required input and where all output and working files will be stored

    Returns:
        Project: project instance
    """
    time_start = datetime.now()
    print(f"Start time: {time_start.strftime('%d %b %Y %H:%M:%S')}")

    # Setup project and automatically start calculations
    project = Project(
        PATH_WORKSPACE,
    )

    # Print hints how to interacts with the results
    print("\nHINTS:\n \t- Show the different result DataFrames using `project.results.unique_models` or `project.results.combined`")
    results_unique_models = project.results.unique_models
    results_combined = project.results.combined

    # Save DataFrame of combined results to csv
    # # FIXME improve output data
    results_combined.to_excel(project.workspace.output.folderpath / "fragility_curve_data_combined.xlsx")

    # # Print info
    # print(f"\nResults are saved to: {fc.workspace.output.folderpath}")

    time_end = datetime.now()
    time_diff = time_end - time_start
    print(f"\nFinished succesfully, end time: {time_end.strftime('%d %b %Y %H:%M:%S')}")
    print(
        f"Total runtime (h:m:s): {int(time_diff.total_seconds() // 3600):02}:{int((time_diff.total_seconds() % 3600) // 60):02}:{int(time_diff.total_seconds() % 60):02}"
    )

    return project


if __name__ == "__main__":

    # Run tool
    project = start_tool(
        PATH_WORKSPACE
    )
