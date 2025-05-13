from __future__ import annotations  # makes all annotations lazy (no quotes needed)

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from app.classes.vak import Vak
    from app.classes.uittredepunt import Uittredepunt
    from app.classes.ondergrond_scenario import OndergrondScenario

from app._default_values_constants import ALLOWED_SUFFIXES


def variable_name_without_suffix(attr_name: str) -> str:
    # Obtain name without suffix (e.g. _mean, _stdev, _vc)
    return next((attr_name[:-len(suffix)] for suffix in ALLOWED_SUFFIXES if attr_name.endswith(suffix)), attr_name)

def check_attribute_already_exists(instance: Vak | Uittredepunt | OndergrondScenario, attr_name: str) -> None:
    if hasattr(instance, attr_name):
        raise AttributeError(f"{instance.__class__.__name__} already has an attribute named '{attr_name}', please rename the column in the input Excel file.")

def check_completeness_input_variables(df_variable_overview: pd.DataFrame, df_vak_collection: pd.DataFrame, df_uittredepunt_collection: pd.DataFrame, df_ondergrond_scenario_collection: pd.DataFrame) -> None:
    set_variable_names_expected = set()
    for index, row in df_variable_overview[df_variable_overview["variable_type"] == "Input"].iterrows():
        if pd.notna(row["variabele_spreidingstype"]):
            set_variable_names_expected.update([str(index) + "_mean", str(index) + row["variabele_spreidingstype"]])
        else:
            set_variable_names_expected.update([str(index)])

    set_variable_names_given = set(df_vak_collection.columns).union(df_uittredepunt_collection.columns, df_ondergrond_scenario_collection.columns)

    if set_variable_names_expected != set_variable_names_given:
        variables_missing = set_variable_names_expected - set_variable_names_given
        variables_surplus = set_variable_names_given - set_variable_names_expected
        
        def link_variables_to_source(variable_names: set[str]) -> pd.DataFrame:
            variables_names_without_suffix = set([variable_name_without_suffix(variable) for variable in variable_names])  # Note: make it a set to remove duplicates

            df = pd.DataFrame({'variable name': list(variables_names_without_suffix)})
            df["source input sheet"] = df["variable name"].apply(lambda x: "Vakken" if x in df_vak_collection.columns else ("Uittredepunten" if x in df_uittredepunt_collection.columns else ("Ondergrondscenarios" if x in df_ondergrond_scenario_collection.columns else "Unknown")))
            return df

        if len(variables_missing) > 0:
            raise ValueError(f"\nMissing variables in input Excel file:\n{link_variables_to_source(variables_missing)}\nHave a look at the sheet 'Overzicht_variabelen' for an overview of expected variables.\nNote that if a variable (e.g. called 'my_variable') is stochastic, two input variables are expected: 'my_variable_mean' and 'my_variable_<variabele_spreidingstype>' (e.g. 'my_variable_stdev').")
        elif len(variables_surplus) > 0:
            raise ValueError(f"\nToo many variables in input Excel file:\n{link_variables_to_source(variables_surplus)}\nPossible causes:\n1. The variables are not defined in sheet 'Overzicht_variabelen'.\n2. The variables are defined in 'Overzicht_variabelen' but no value for 'variabele_spreidingstype' is given.\n3. Unknown reason")

def check_variable_in_overview(attr_name: str, df_variable_overview: pd.DataFrame) -> None:
    # Check if attribute exists in the sheet 'Overzicht_variabelen'
    attr_name_without_suffix = variable_name_without_suffix(attr_name)
    if not attr_name_without_suffix in df_variable_overview.index:
        raise ValueError(f"Variable '{attr_name}' not found in sheet 'Overzicht_variabelen' of input Excel file")

def enforce_lower_upper_bounds(attr_name: str, attr_value: float, df_variable_overview) -> None:
    # Check if value lies within upper and lower bounds in df_variable_overview (if specified)
    attr_name_without_suffix = variable_name_without_suffix(attr_name)
    if pd.notna(df_variable_overview.at[attr_name_without_suffix, "variable_mean_lower_bound"]):
        lower_bound = df_variable_overview.at[attr_name_without_suffix, 'variable_mean_lower_bound']
        if not (lower_bound <= attr_value):
            raise ValueError(f"Mean value {attr_value} for variable '{attr_name_without_suffix}' exceeds lower bound (min: {lower_bound})")

    if pd.notna(df_variable_overview.at[attr_name_without_suffix, "variable_mean_upper_bound"]):
        upper_bound = df_variable_overview.at[attr_name_without_suffix, 'variable_mean_upper_bound']
        if not (attr_value <= upper_bound):
            raise ValueError(f"Mean value {attr_value} for variable '{attr_name_without_suffix}' exceeds upper bound (max: {upper_bound})")
