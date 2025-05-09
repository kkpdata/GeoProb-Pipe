from __future__ import annotations  # makes all annotations lazy (no quotes needed)

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from app.classes.vak import Vak, VakCollection
    from app.classes.uittredepunt import Uittredepunt, UittredepuntCollection
    from app.classes.ondergrond_scenario import OndergrondScenario, OndergrondScenarioCollection

from app._default_values_constants import ALLOWED_SUFFIXES, REQUIRED_COLUMNS


def attribute_already_exists(instance: Vak | Uittredepunt | OndergrondScenario, attr_name: str) -> None:
    if hasattr(instance, attr_name):
        raise AttributeError(f"{instance.__class__.__name__} already has an attribute named '{attr_name}', please rename the column in the input Excel file.")

def enforce_lower_upper_bounds(attr_name: str, attr_value: float, df_variable_overview: pd.DataFrame) -> None:
    # Obtain name without suffix (e.g. _mean, _stdev, _vc)
    attr_name_without_suffix = next((attr_name[:-len(suffix)] for suffix in ALLOWED_SUFFIXES if attr_name.endswith(suffix)), attr_name)
    
    # Check if attribute exists in the sheet 'Overzicht_variabelen' of the input Excel file
    if not attr_name_without_suffix in df_variable_overview.index:
        raise ValueError(f"Attribute '{attr_name}' not found in sheet 'Overzicht_variabelen' of input Excel file")
    
    # Check if value lies within upper and lower bounds in df_variable_overview (if specified)
    if pd.notna(df_variable_overview.at[attr_name_without_suffix, "variable_mean_lower_bound"]):
        lower_bound = df_variable_overview.at[attr_name_without_suffix, 'variable_mean_lower_bound']
        if not (lower_bound <= attr_value):
            raise ValueError(f"Mean value {attr_value} for attribute '{attr_name_without_suffix}' exceeds lower bound (min: {lower_bound})")

    if pd.notna(df_variable_overview.at[attr_name_without_suffix, "variable_mean_upper_bound"]):
        upper_bound = df_variable_overview.at[attr_name_without_suffix, 'variable_mean_upper_bound']
        if not (attr_value <= upper_bound):
            raise ValueError(f"Mean value {attr_value} for attribute '{attr_name_without_suffix}' exceeds upper bound (max: {upper_bound})")

def check_required_columns(instance: VakCollection | UittredepuntCollection | OndergrondScenarioCollection, df: pd.DataFrame) -> None:

    if instance.__class__.__name__ == "VakCollection":
        required_columns = REQUIRED_COLUMNS["vak"]
        sheet_name = "Vakken"
    elif instance.__class__.__name__ == "UittredepuntCollection":
        required_columns = REQUIRED_COLUMNS["uittredepunt"]
        sheet_name = "Uittredepunten"
    elif instance.__class__.__name__ == "OndergrondScenarioCollection":
        required_columns = REQUIRED_COLUMNS["ondergrond_scenario"]
        sheet_name = "Ondergrondscenarios"
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in the '{sheet_name}' sheet of the input Excel file: {', '.join(missing_columns)}")

