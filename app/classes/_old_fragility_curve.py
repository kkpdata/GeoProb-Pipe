from pathlib import Path

import pandas as pd
import scipy.stats as stats
from scipy.stats import gumbel_r, norm

from app.classes.dike_geometry import DikeGeometry
from app.classes.file_system import FileSystem
from app.classes.heave import Heave
from app.classes.line_geometry import LineGeometry
from app.classes.opbarsten import Opbarsten
from app.classes.subsoil import Subsoil
from app.classes.table import Table
from app.classes.terugschrijdende_erosie import Terugschr_erosie
from app.classes.toolkit import Toolkit
from app.classes.waterlevel_statistics import WaterlevelStatistics
from app.classes.workspace import Workspace
from app.helper_functions.fragility_curve_functions import (
    _densify_extrapolate_alphas,
    _densify_extrapolate_betas,
    calculate_design_point_beta,
    calculate_design_point_waterlevel,
    calculate_influence_factors_including_waterlevel,
)
from app.helper_functions.geodatabase_functions import process_geodatabase
from app.helper_functions.plotting_functions import (
    _plot_fragility_curve,
    _plot_influence_factors,
    _plot_multiple_fragility_curves,
    _plot_waterlevel_statistics,
)

# df_dike_geometry = pd.read_excel(
#     r"V:\dr_Waterkeringen\08. Kennis\02. Probabilitische rekenen - werkmap\GeoProb-Pipe\testcase 20-4 STPH\Test_bestand_geoprob_pipe.xlsx",
#     sheet_name="test_vak_par",
# )

# df_traject_par = pd.read_excel(
#     r"V:\dr_Waterkeringen\08. Kennis\02. Probabilitische rekenen - werkmap\GeoProb-Pipe\testcase 20-4 STPH\Test_bestand_geoprob_pipe.xlsx",
#     sheet_name="test_traject_par",
#     index_col="Parameter",
# )

# df_general_par = pd.read_excel(
#     r"V:\dr_Waterkeringen\08. Kennis\02. Probabilitische rekenen - werkmap\GeoProb-Pipe\testcase 20-4 STPH\Test_bestand_geoprob_pipe.xlsx",
#     sheet_name="test_gen_par",
#     index_col="Parameter",
# )


class FragilityCurve:
    """FragilityCurve class which carries out all actions required for generating a fragility curve and finding the design point"""

    def __init__(
        self,
        PATH_WORKSPACE: str | Path,
        USE_EXISTING_TKX_RESULTS: bool,
        CLEANUP_WORK_DIR: bool,
        COMBINE_FRAGILITY_CURVES: bool,
        FRAGILITY_CURVE_NON_FAILURE_ADJUSTMENT: bool,
        NON_FAILURE_THRESHOLD: dict,
        WATERLEVEL_RANGE: list[float],
        MU: float,
        SCALE: float,
    ) -> None:

        # Initialize Workspace object
        self.workspace = Workspace(PATH_WORKSPACE, USE_EXISTING_TKX_RESULTS)

        # Initialize Toolkit object
        self.toolkit = Toolkit(self.workspace.input.folderpath, USE_EXISTING_TKX_RESULTS)
        print("ABC")

        # def _start_heave_calculation(self):
        #     heave = Heave(self.dike_geometry, df_general_par.loc["i_toelaatbaar", "Waarde"])
        #     return heave.fos_heave

        # def _start_terugschr_erosie_calculation(self):
        #     terugschr_erosie = Terugschr_erosie(self.dike_geometry, df_general_par)
        #     return terugschr_erosie.fos_terugschrijdende_erosie

        # # TODO voor nu wordt nog gdf_dikegeometry gebruikt, moet weg als tupple format hiervoor bekend is. (zie ook opbarsten.py)
        # def _start_opbarsten_calculation(self):
        #     opbarsten = Opbarsten(self.dike_geometry, df_dike_geometry, df_general_par, df_general_par)
        #     return opbarsten.kritiek_stijgh_verschil

        # # Calculate fragility curve
        # if USE_EXISTING_TKX_RESULTS:
        #     print(
        #         f"INFO: USE_EXISTING_TKX_RESULTS=True, so no new calculations are started. Instead, the .tkx files in the specified output folder ({self.workspace.folderpath}) are used."
        #     )
        #     self.workspace.map_precalculated_tkx_input_stix(self.toolkit.settings.ptk_server_path)
        #     self.toolkit._use_precalculated_results(self.dstability.overview, self.workspace.mapping_tkx_stix)
        # else:
        #     self.toolkit._use_new_calculations(
        #         self.dstability.overview,
        #         self.workspace.output.folderpath,
        #         self.workspace.work_dir.folderpath,
        #         CLEANUP_WORK_DIR,
        #     )
        #     self.workspace.update_output_filesystem()  # Update output FileSystem object because new output .tkx files were generated

        # # Initialize WaterlevelStatistics object
        # self.waterlevel_statistics = WaterlevelStatistics(MU, SCALE, WATERLEVEL_RANGE)

        # # Interpolate and extrapolate the reliability index and alpha values between and beyond fragility curve points
        # self._betas_densified_extrapolated = _densify_extrapolate_betas(
        #     self.waterlevel_statistics.waterlevel_array,
        #     self.betas,
        # )
        # self._alphas_densified_extrapolate = _densify_extrapolate_alphas(
        #     self.waterlevel_statistics.waterlevel_array, self.alphas
        # )

        # # Convert interpolated/extrapolated reliability indices to failure probabilities
        # self._failure_probabilities_densified_extrapolated = self._betas_densified_extrapolated.copy(deep=True)
        # self._failure_probabilities_densified_extrapolated["Pf_h"] = norm.cdf(
        #     -1 * self._failure_probabilities_densified_extrapolated["beta"]
        # )  # P(f|h) = Φ[−𝛽(ℎ)]
        # self._failure_probabilities_densified_extrapolated.drop(labels="beta", axis=1, inplace=True)

        # # FIXME add option to modify FCs with a non-failure threshold/adjustment
        # if FRAGILITY_CURVE_NON_FAILURE_ADJUSTMENT or NON_FAILURE_THRESHOLD:
        #     raise NotImplementedError()

        # # FIXME add functionality to combine FCs
        # if COMBINE_FRAGILITY_CURVES:
        #     raise NotImplementedError()

        # # Obtain design point
        # self.design_point = DesignPoint(
        #     self._failure_probabilities_densified_extrapolated,
        #     self._alphas_densified_extrapolate,
        #     self.waterlevel_statistics,
        # )

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
            pd.DataFrame: beta values (reliability indices) for each waterlevel
        """
        return self.toolkit.results.betas

    @property
    def alphas(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: alpha values of variables for each waterlevel
        """
        return self.toolkit.results.alphas

    @property
    def influence_factors(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: influence factors (squared alpha values) of variables for each waterlevel
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
        _plot_fragility_curve(
            self.toolkit.results.betas,
            self._failure_probabilities_densified_extrapolated,
            self.workspace.output.folderpath,
            show_save=True,
        )

    def plot_waterlevel_statistics(self) -> None:
        """Plot interpolated/extrapolated fragility curve together with waterlevel statistics"""
        _plot_waterlevel_statistics(
            self.betas,
            self._betas_densified_extrapolated,
            self.waterlevel_statistics,
            self.workspace.output.folderpath,
            design_point_beta=self.design_point.beta,
        )

    def plot_multiple_fragility_curves(self) -> None:
        """Plotting functions for multiple fragility curves"""
        # _plot_multiple_fragility_curves(self.toolkit.results.overview["waterlevel"], self.toolkit.results.overview["beta"], show=True)
        raise NotImplementedError("Functionality to plot multiple fragility curves is not implemented yet!")

    def plot_influence_factors(self) -> None:
        """Plotting functions for influence factors"""
        df_design_point_influence_factors = self.design_point.influence_factors[
            "influence factor including waterlevel"
        ].to_frame()

        df_design_point_influence_factors.rename(
            columns={"influence factor including waterlevel": "influence factor"}, inplace=True
        )

        df_influence_factors_concat = pd.concat([self.influence_factors, df_design_point_influence_factors])
        _plot_influence_factors(df_influence_factors_concat.sort_index(level="waterlevel"))


class DesignPoint:
    """The design point (ontwerppunt) is the waterlevel of the point on the limit state line (Z=0, grenstoestandslijn) is the point on the
    limit state line (Z=0, grenstoestandslijn) that has the highest probability of occurrence (most probable combination of strength and load parameters).
    To find the design point, we integrating (uitintegreren) the conditional failure probability (fragility curve) over the entire range of possible water
    levels, weighted by the probability density function (PDF) of the water levels. This results in a "total" (/design point) failure probability with
    corresponding reliability index. For this design point, the corresponding  waterlevel and alpha values can then be found.

    This class determines the following:
        1. Reliability index (beta) of the design point
        2. Waterlevel of the design point
        3. Influence factors of the variables for the design point, including the influence factor of the waterlevel
    """

    def __init__(
        self,
        failure_probabilities_densified_extrapolated: pd.DataFrame,
        alphas_densified_extrapolate: pd.DataFrame,
        waterlevel_statistics: WaterlevelStatistics,
    ) -> None:
        """ "Initialize DesignPoint (ontwerppunt) instance.

        Args:
            failure_probabilities_densified_extrapolated (pd.DataFrame): interpolated/extrapolated set of failure probabilities
            alphas_densified_extrapolate (pd.DataFrame): interpolated/extrapolated set of alpha values
            waterlevel_statistics (WaterlevelStatistics): WaterlevelStatistics class which stores data related to the waterlevels statistics (Gumbel fit)
        """

        self._beta, self._Pf = calculate_design_point_beta(
            failure_probabilities_densified_extrapolated,
            waterlevel_statistics,
        )

        self._waterlevel = calculate_design_point_waterlevel(waterlevel_statistics, self._Pf)

        self._influence_factors = calculate_influence_factors_including_waterlevel(
            alphas_densified_extrapolate,
            self.waterlevel,
            waterlevel_statistics,
            self.beta.squeeze(),
        )

    @property
    def waterlevel(self) -> float:
        """
        Returns:
            float: waterlevel of the design point
        """
        return self._waterlevel

    @property
    def beta(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: reliability index (beta) at the design point waterlevel
        """
        return pd.DataFrame({"beta": [self._beta]}, index=[self.waterlevel]).rename_axis("waterlevel")

    @property
    def Pf(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: probability of failure at the design point waterlevel
        """
        return pd.DataFrame({"Pf": [self._Pf]}, index=[self.waterlevel]).rename_axis("waterlevel")

    @property
    def alphas(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: alpha values of variables (including and excluding the waterlevel) for the design point
        """
        return (self.influence_factors["inf. factor excluding waterlevel"] ** 0.5).to_frame()

    @property
    def influence_factors(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: influence factor (including and excluding the waterlevel) for the design point
        """
        return self._influence_factors
        return (self.alphas**2).rename(
            columns={
                "alpha excluding waterlevel": "influence factor excluding waterlevel",
                "alpha including waterlevel": "influence factor including waterlevel",
            }
        )
