import shutil
from pathlib import Path

import pandas as pd
from classes.toolkit import Toolkit

from app.classes.dstability import DStability
from app.classes.toolkit import Toolkit
from app.classes.waterlevel_statistics import WaterlevelStatistics
from app.classes.workspace import Workspace
from app.helper_functions.fragility_curve_functions import (
    integrating_FC_with_water_levels,
)
from app.helper_functions.plotting_functions import (
    _plot_fragility_curve,
    _plot_influence_factors,
    _plot_multiple_fragility_curves,
)


class FragilityCurve:
    """FragilityCurve class which carries out all actions required for generating a fragility curve"""

    def __init__(
        self,
        PATH_WORKSPACE: str | Path,
        USE_EXISTING_TKX_RESULTS: bool,
    ) -> None:
        """Initialize FragilityCurve instance which carries out all actions required for generating a fragility curve

        Args:
            PATH_WORKSPACE (str | Path): path to the folder that contains all required input and where all output and working files will be stored
            USE_EXISTING_TKX_RESULTS (bool): whether to use precalculated .tkx files (True) or to start new calculations (False)
        """

        # Initialize Workspace object
        self.workspace = Workspace(PATH_WORKSPACE, USE_EXISTING_TKX_RESULTS)

        # Initialize DStability object
        self.dstability = DStability(self.workspace.input.folderpath)

        # Initialize Toolkit object
        self.toolkit = Toolkit(self.workspace.input.folderpath, USE_EXISTING_TKX_RESULTS)

        # Create fragility curve
        if USE_EXISTING_TKX_RESULTS:
            print(
                f"INFO: USE_EXISTING_TKX_RESULTS=True, so no new calculations are started. Instead, the .tkx files in the specified output folder ({self.workspace.folderpath}) are used."
            )
            self.workspace.map_precalculated_tkx_input_stix(self.toolkit.settings.ptk_server_instance)
            self.toolkit.use_precalculated_results(self.dstability.overview, self.workspace.mapping_tkx_stix)
        else:
            self.toolkit.use_new_calculations(
                self.dstability.overview,
                self.workspace.output.folderpath,
                self.workspace.work_dir.folderpath,
            )
            self.workspace.update_output_filesystem()  # Update output FileSystem object because new output .tkx files were generated

    @property
    def waterlevels(self) -> pd.DataFrame:
        """
        Returns:
            dict: waterlevel for each .stix, shown in dict-format as {path_to_stix: waterlevel}
        """
        return self.toolkit.overview[["waterlevel", "stix", "tkx"]]

    @property
    def betas(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: waterlevels and corresponding beta values (reliability indices)
        """
        return self.toolkit.results.betas

    @property
    def alphas(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: alpha values per variable for each waterlevel
        """
        return self.toolkit.results.alphas

    @property
    def influence_factors(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: influence factor (which is the squared alpha value) for each waterlevel
        """
        return self.toolkit.results.influence_factors

    @property
    def variables(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: distribution parameters per variable for each waterlevel
        """
        return self.toolkit.results.variables

    def plot_fragility_curve(self) -> None:
        """Plotting functions for fragility curve"""
        _plot_fragility_curve(self.toolkit.results.overview["waterlevel"], self.toolkit.results.overview["beta"], show=True)

    def plot_multiple_fragility_curves(self) -> None:
        """Plotting functions for multiple fragility curves"""
        _plot_multiple_fragility_curves(self.toolkit.results.overview["waterlevel"], self.toolkit.results.overview["beta"], show=True)

    def plot_influence_factors(self) -> None:
        """Plotting functions for influence factors"""
        _plot_influence_factors(self.influence_factors)

    def integrating(self, waterlevel_statistics: WaterlevelStatistics, waterlevel_range: list[float]) -> None:
        """Integrating functions (uitintegreren) to obtain the total failure probability using waterlevel
        statistics and the betas (reliability indices) from the PTK calculation

        Args:
            waterlevel_statistics (WaterlevelStatistics): waterlevel statistics mu (mode) and sigma (standard deviation) (Gumbel fit)
            waterlevel_range (list[float]): range of waterlevels for which we want an integrated fragility curve
        """
        self.total_beta, self.total_failure_probability = integrating_FC_with_water_levels(
            self.toolkit.results.overview["waterlevel"],
            self.toolkit.results.overview["beta"],
            waterlevel_statistics,
            waterlevel_range,
        )
