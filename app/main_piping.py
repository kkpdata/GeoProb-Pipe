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
p
    Args:
        PATH_WORKSPACE: path to the folder that contains all required input and where all output and working files will be stored
        USE_EXISTING_TKX_RESULTS (bool): whether to use precalculated .tkx files (True) or to start new calculations (False)
        CLEANUP_WORK_DIR (bool): whether to cleanup temporary (calculation) files in the working directory
        COMBINE_FRAGILITY_CURVES (bool): #FIXME not implemented yet, boolean to toggle combining multiple fragility curves into one.
        FRAGILITY_CURVE_NON_FAILURE_ADJUSTMENT (bool): #FIXME not implemented yet, boolean whether to modify a fragility curve with a non-failure threshold
        NON_FAILURE_THRESHOLD (dict): #FIXME not implemented yet, defines non-failure threshold when FRAGILITY_CURVE_NON_FAILURE_ADJUSTMENT==True
        WATERLEVEL_RANGE (list[float]): range of waterlevels for which we want a integrated fragility curve
        MU (float): mode (modus) of the load (water level) uncertainty distribution (Gumbel fit)
        SCALE (float): scale parameter of the Gumbel fit of the load (water level) uncertainty distribution

    Returns:
        FragilityCurve: fragility curve instance
    """
    time_start = datetime.now()
    print(f"Start time: {time_start.strftime('%d %b %Y %H:%M:%S')}")

    # Setup project and automatically start calculations
    project = Project(
        PATH_WORKSPACE,
    )

    # Overview of results
    results = project.results

    # Save dataframe to csv
    # # FIXME improve output data
    results.to_excel(project.workspace.output.folderpath / "fragility_curve_data.xlsx")

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

    # FIXME variables in preparation of next update, currently set to None
    USE_EXISTING_TKX_RESULTS = None
    COMBINE_FRAGILITY_CURVES = None
    FRAGILITY_CURVE_NON_FAILURE_ADJUSTMENT = None
    NON_FAILURE_THRESHOLD = None

    # Run tool
    project = start_tool(
        PATH_WORKSPACE
    )
