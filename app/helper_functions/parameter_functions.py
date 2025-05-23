
from collections.abc import Iterable
from typing import Optional

import pandas as pd

from app.misc._default_values_constants import ALLOWED_SUFFIXES


def strip_suffix_from_parameter_name(var_name: str, list_suffixes: Optional[list[str]] = None) -> str:
    suffixes = list_suffixes or ALLOWED_SUFFIXES  # Use list_suffixes if provided, otherwise use the default allowed list suffixes
    return next((var_name[:-len(suf)] for suf in suffixes if var_name.endswith(suf)), var_name)


def strip_suffix_from_list_parameter_names(list_var_names: Iterable[str], list_suffixes: Optional[list[str]] = None) -> list[str]:
    if isinstance(list_var_names, str):
        raise TypeError("Input must be an iterable of strings (e.g. list/set/pd.Index), not a single string.")
    return list(dict.fromkeys([strip_suffix_from_parameter_name(var_name, list_suffixes) for var_name in list_var_names]))  # Note: dict.fromkeys is used to remove duplicates while preserving order


def generate_variable_dict(attr_name_without_suffix: str, df_row: pd.Series, df_overview_parameters: pd.DataFrame) -> dict:
    var_dict = {"type": df_overview_parameters.at[attr_name_without_suffix, "parameter_type"]}
    var_dict["distribution"] = df_overview_parameters.at[attr_name_without_suffix, "parameter_distribution"]  # Note: all supported distribution strings can be found in probabilistic_library.statistic.DistributionType
    
    if var_dict["distribution"] == "deterministic":
        var_dict["value"] = df_row[attr_name_without_suffix]
    else:
        var_dict["mean"] = df_row[attr_name_without_suffix + "_mean"]
        var_dict["dispersion_type"] = df_overview_parameters.at[attr_name_without_suffix, "parameter_spreidingstype"]
        var_dict["dispersion_value"] = df_row[attr_name_without_suffix + var_dict["dispersion_type"]]
    
    var_dict["unit"] = df_overview_parameters.at[attr_name_without_suffix, "parameter_unit"]
    
    # Note that both deterministic and stochastic variables can have lower and upper bounds
    var_dict["lower_bound_mean"] = df_overview_parameters.at[attr_name_without_suffix, "parameter_mean_lower_bound"]
    var_dict["upper_bound_mean"] = df_overview_parameters.at[attr_name_without_suffix, "parameter_mean_upper_bound"]

    return var_dict
