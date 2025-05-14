from __future__ import annotations  # makes all annotations lazy (no quotes needed)

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from app.classes.vak import Vak
    from app.classes.uittredepunt import Uittredepunt
    from app.classes.ondergrond_scenario import OndergrondScenario

from typing import Any, List, Optional, Union

from app.misc._default_values_constants import ALLOWED_SUFFIXES


def get_variable_name_without_suffix(attr_name: Union[str, List[str]], list_suffixes: Optional[List[str]] = None) -> Union[str, List[str]]:
    suffixes = list_suffixes or ALLOWED_SUFFIXES  # Use list_suffixes if provided, otherwise use the default allowed list suffixes
    strip_suffix = lambda s: next((s[:-len(suf)] for suf in suffixes if s.endswith(suf)), s)
    return list(dict.fromkeys(strip_suffix(attr_name) if isinstance(attr_name, str) else [strip_suffix(s) for s in attr_name]))  # Note: dict.fromkeys is used to remove duplicates while preserving order


def generate_variable_dict(attr_name_without_suffix: str, df_row: pd.Series, df_variable_overview: pd.DataFrame) -> dict:
    var_dict = {"type": df_variable_overview.at[attr_name_without_suffix, "variable_type"]}
    var_dict["distribution"] = df_variable_overview.at[attr_name_without_suffix, "variable_distribution"]
    
    if var_dict["distribution"] == "deterministic":
        var_dict["value"] = df_row[attr_name_without_suffix]
    else:
        var_dict["mean"] = df_row[attr_name_without_suffix + "_mean"]
        var_dict["dispersion_type"] = df_variable_overview.at[attr_name_without_suffix, "variable_spreidingstype"]
        var_dict["dispersion_value"] = df_row[attr_name_without_suffix + var_dict["dispersion_type"]]
    
    var_dict["unit"] = df_variable_overview.at[attr_name_without_suffix, "variable_unit"]
    
    # Note that both deterministic and stochastic variables can have lower and upper bounds
    var_dict["lower_bound_mean"] = df_variable_overview.at[attr_name_without_suffix, "variable_mean_lower_bound"]
    var_dict["upper_bound_mean"] = df_variable_overview.at[attr_name_without_suffix, "variable_mean_upper_bound"]

    return var_dict
