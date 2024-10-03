import math

import pandas as pd

from app.classes.toolkit_native_model import ToolkitNative, ToolkitProject
from app.helper_functions.toolkit_functions import load_tkx_file


class ToolkitResults:
    """ToolkitResults class containing the results of the Probabilistic Toolkit calculations"""

    def __init__(self, toolkit_overview: pd.DataFrame, toolkit_server_instance: ToolkitNative) -> None:
        """Initialize ToolkitResults instance containing the results of the Probabilistic Toolkit calculations

        Args:
            toolkit_overview (pd.DataFrame): general overview of the calculated .tkx files and their corresponding .stix files and parsed D-Stability models
            toolkit_server_instance (ToolkitNative): running instance of the PTK server
        """
        self.overview = self._get_results(toolkit_overview, toolkit_server_instance)
        self._valid_results()

    @property
    def betas(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: waterlevels and corresponding beta values (reliability indices)
        """
        return self.overview[["waterlevel", "beta"]]

    @property
    def variables(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: distribution parameters per variable for each waterlevel
        """
        return pd.concat(
            self.overview["variables"].values, keys=self.overview["waterlevel"], names=["waterlevel", "variables"]
        )

    @property
    def alphas(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: alpha values per variable for each waterlevel
        """
        return pd.DataFrame(self.variables["alpha"])  # type: ignore

    @property
    def influence_factors(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: influence factor (which is the squared alpha value) for each waterlevel
        """
        df_influence_factors = self.alphas**2
        return df_influence_factors.rename(columns={"alpha": "influence_factor"})

    def _get_variables(self, tkx: ToolkitProject) -> pd.DataFrame:
        """Get all variables and corresponding distribution parameters

        Args:
            tkx (ToolkitProject): ToolkitProject object

        Returns:
            pd.DataFrame: overview of variables and corresponding distribution parameters
        """
        rows = []
        for variable in tkx.model.variables:
            rows.append(
                {
                    "variable": variable.name,
                    "distribution": variable.distribution,
                    "mean": variable.mean,
                    "sigma dev": variable.deviation,
                    "alpha": tkx.design_point.get_alpha(variable).alpha_value,
                }
            )
        return pd.DataFrame(rows).set_index("variable")

    def _get_reliability_index(self, tkx: ToolkitProject) -> float:
        """Get calculated beta value (reliability index) of the PTK calculation

        Args:
            tkx (ToolkitProject): ToolkitProject object

        Returns:
            float: beta value (reliability index)
        """
        return tkx.design_point.reliability_index

    def _valid_results(self) -> None:
        """Checks whether the PTK calculation results are valid"""
        sum_squared_alphas = self.alphas["alpha"].pow(2).groupby(level="waterlevel").sum()

        if not sum_squared_alphas.apply(lambda x: math.isclose(x, 1)).all():
            with pd.option_context("display.float_format", "{:.9f}".format):
                # Make sure that the floats in the DataFrame are printed with up to 9 digits to facilitate
                # inspection by the user
                print(
                    f"\nWARNING: The sum of squared alpha's of each waterlevel should equal 1. This is not the case:\n{pd.DataFrame(sum_squared_alphas)}"
                )

    def _get_results(self, toolkit_overview: pd.DataFrame, toolkit_server_instance: ToolkitNative) -> pd.DataFrame:
        """Adds the PTK calculations results to the overview with general information of the PTK calculations

        Args:
            toolkit_overview (pd.DataFrame): overview with general information of the PTK calculations (e.g. tkx filepaths and corresponding stix files and waterlevels)
            toolkit_server_instance (ToolkitNative): running instance of the PTK server

        Returns:
            pd.DataFrame: overview with PTK calculations results
        """
        results_overview = toolkit_overview.copy(deep=True)

        list_beta = []
        list_variables = []

        for output_tkx in results_overview["tkx"]:
            tkx = load_tkx_file(toolkit_server_instance, output_tkx["path"])

            list_beta.append(self._get_reliability_index(tkx))
            list_variables.append(self._get_variables(tkx))

        results_overview["beta"] = list_beta
        results_overview["variables"] = list_variables

        # Return the DataFrame and make sure the waterlevels, betas and variables are shown as the first columns
        return results_overview[
            ["waterlevel", "beta", "variables"]
            + [col for col in results_overview.columns if col not in ["waterlevel", "beta", "variables"]]
        ]
