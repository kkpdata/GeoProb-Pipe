import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))  # Add repo to sys.path to make sure all imports are correctly found

from app.classes.fragility_curve import FragilityCurve
from app.classes.waterlevel_statistics import WaterlevelStatistics
from app.helper_functions.plotting_functions import _plot_multiple_fragility_curves

# ====================================
# User Input Section
# ====================================

# Define path to workspace (either absolute or relative)
PATH_WORKSPACE: str | Path = r"..\\example_workspaces\example_precalculated_output"

# Whether existing calculation results should be used
# If True, the .tkx files that are found the "PATH_WORKSPACE/output" folder are used
USE_EXISTING_TKX_RESULTS: bool = True

# Define waterlevel (buitenwaterstand) range for which you want an integrated fragility curve
# Format: [range_start, range_end]. Suggested values:
#   - range_start: should be at min. the daily waterlevel
#   - range_end: should be max. either the dike crest level (kruinniveau) or the 95th percentile of the waterlevel statistics (MU, SIGMA)
waterlevel_range: list[float] = [0.3, 4.5]

# Define the distribution parameters of the load (water level) uncertainty distribution
# Use the script helper_functions/fit_extreme_value_dis_water_level.py for this
# Traject 17-1
MU: float = 2.57
SIGMA: float = 0.102

## Traject 20-4
# MU: float = 2.17
# SIGMA: float = 0.088

# ====================================
# End of User Input Section
# ====================================


def start_tool(
    PATH_WORKSPACE: str | Path, USE_EXISTING_TKX_RESULTS: bool, waterlevel_range: list[float], MU: float, SIGMA: float
) -> FragilityCurve:
    """Start PTK tool

    Args:
        PATH_WORKSPACE: path to the folder that contains all required input and where all output and working files will be stored
        USE_EXISTING_TKX_RESULTS (bool): whether to use precalculated .tkx files (True) or to start new calculations (False)
        MU (float): mode (modus) of the load (water level) uncertainty distribution (Gumbel fit)
        SIGMA (float): standard deviation of the load (water level) uncertainty distribution (Gumbel fit)

    Returns:
        FragilityCurve: fragility curve instance
    """
    time_start = datetime.now()
    print(f"Start time: {time_start.strftime('%d %b %Y %H:%M:%S')}")

    # Calculate fragility curve
    fc = FragilityCurve(
        PATH_WORKSPACE,
        USE_EXISTING_TKX_RESULTS,
    )

    # Overview of fragility curve results
    results = fc.toolkit.results.overview

    # Some fragility curve results can also be accessed from the FragilityCurve object, which are
    # references to the corresponding attributes in fc.toolkit.results
    betas = fc.betas
    waterlevels = fc.waterlevels
    alphas = fc.alphas
    variables = fc.variables

    # Plot the fragility curve and influence factors found in the PTK calculations
    fc.plot_fragility_curve()
    fc.plot_influence_factors()

    # Integrate the fragility curve with the waterlevel statistics
    fc.integrating(WaterlevelStatistics(MU, SIGMA), waterlevel_range)

    # Print results
    print("Total failure probability after integration = %0.2e" % (fc.total_failure_probability))
    print("Reliability index after integration = ", fc.total_beta)

    # Code for plotting multiple FCs, currently not used
    # fragility_data = {
    #     "FC A": (fc.toolkit.results.overview),
    #     "FC B": (fc.toolkit.results.overview),
    #     "FC C": (fc.toolkit.results.overview),
    # }
    # fc.plot_multiple_fragility_curves(fragility_data)

    # Save dataframe to csv
    fc.toolkit.results.overview.to_excel(fc.workspace.output.folderpath / "fragility_curve_data.xlsx")

    # Print info
    print(f"\nResults are saved in: {fc.workspace.output.folderpath}")

    time_end = datetime.now()
    time_diff = time_end - time_start
    print(f"\nFinished succesfully, end time: {time_end.strftime('%d %b %Y %H:%M:%S')}")
    print(
        f"Total runtime (h:m:s): {int(time_diff.total_seconds() // 3600):02}:{int((time_diff.total_seconds() % 3600) // 60):02}:{int(time_diff.total_seconds() % 60):02}"
    )

    return fc


if __name__ == "__main__":
    # Run rool
    fc = start_tool(PATH_WORKSPACE, USE_EXISTING_TKX_RESULTS, waterlevel_range, MU, SIGMA)
