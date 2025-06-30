
from collections.abc import Iterable
from typing import Optional

import pandas as pd

from geoprob_pipe.globals import ALLOWED_SUFFIXES


def strip_suffix_from_parameter_name(var_name: str, list_suffixes: Optional[list[str]] = None) -> str:
    suffixes = list_suffixes or ALLOWED_SUFFIXES
    # Use list_suffixes if provided, otherwise use the default allowed list suffixes
    return next((var_name[:-len(suf)] for suf in suffixes if var_name.endswith(suf)), var_name)


def strip_suffix_from_list_parameter_names(
        list_var_names: Iterable[str], list_suffixes: Optional[list[str]] = None) -> list[str]:
    if isinstance(list_var_names, str):
        raise TypeError("Input must be an iterable of strings (e.g. list/set/pd.Index), not a single string.")
    return list(dict.fromkeys([strip_suffix_from_parameter_name(var_name, list_suffixes)
                               for var_name in list_var_names]))
    # Note: dict.fromkeys is used to remove duplicates while preserving order


def generate_parameter_dict_for_variable(attr_name: str, df_overview_row: pd.Series, df_row: pd.Series) -> dict:
    return _generate_parameter_dict(attr_name, df_overview_row, df_row=df_row)

def generate_parameter_dict_for_constant(attr_name: str, df_overview_row: pd.Series) -> dict:
    return _generate_parameter_dict(attr_name, df_overview_row, df_row=None)

def _generate_parameter_dict(attr_name_without_suffix: str, df_overview_row: pd.Series,
                             df_row: Optional[pd.Series] = None) -> dict:
    def _get_value(suffix: str, default_col: str):
        col = attr_name_without_suffix + suffix
        if df_row is not None and col in df_row and not pd.isna(df_row[col]):
            # If df_row is provided (i.e. a variable is passed) and the value is not NaN, return the value from df_row
            return df_row[col]
        elif pd.notna(df_overview_row[default_col]):
            # If df_row is None (i.e. a constant is passed) or the value is NaN, use the default value from
            # df_overview (if available)
            return df_overview_row[default_col]
        else:
            raise ValueError(f"Value for '{col}' is not provided in the input Excel. Please check the input data.")

    parameter_dict = {
                "name": attr_name_without_suffix,
                "type": df_overview_row["parameter_type"],
                "distribution": df_overview_row["parameter_distribution"],
        # Note: all supported distribution strings can be found in probabilistic_library.statistic.DistributionType
                "unit": df_overview_row["parameter_unit"],
                "lower_bound_mean": df_overview_row["parameter_mean_lower_bound"],
                "upper_bound_mean": df_overview_row["parameter_mean_upper_bound"]
            }

    if parameter_dict["distribution"] == "deterministic":
        parameter_dict["value"] = _get_value("", "parameter_default_value_mean")
    else:
        parameter_dict["mean"] = _get_value("_mean", "parameter_default_value_mean")
        parameter_dict["dispersion_type"] = df_overview_row["parameter_spreidingstype"]
        parameter_dict["dispersion_value"] = _get_value(parameter_dict["dispersion_type"],
                                                        "parameter_default_value_spreiding")

    return parameter_dict