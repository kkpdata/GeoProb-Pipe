from __future__ import annotations  # makes all annotations lazy (no quotes needed)

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from app.classes.vak import Vak
    from app.classes.uittredepunt import Uittredepunt
    from app.classes.ondergrond_scenario import OndergrondScenario

from typing import List, Optional, Union

from app.misc._default_values_constants import ALLOWED_SUFFIXES


def variable_name_without_suffix(attr_name: Union[str, List[str]], list_suffixes: Optional[List[str]] = None) -> Union[str, List[str]]:
    suffixes = list_suffixes or ALLOWED_SUFFIXES  # Use list_suffixes if provided, otherwise use the default allowed list suffixes
    strip_suffix = lambda s: next((s[:-len(suf)] for suf in suffixes if s.endswith(suf)), s)
    return strip_suffix(attr_name) if isinstance(attr_name, str) else [strip_suffix(s) for s in attr_name]

def check_attribute_already_exists(instance: Vak | Uittredepunt | OndergrondScenario, attr_name: str) -> None:
    if hasattr(instance, attr_name):
        raise AttributeError(f"{instance.__class__.__name__} already has an attribute named '{attr_name}', please rename the column in the input Excel file.")


def check_completeness_input_variables(df_variable_overview: pd.DataFrame, df_vak_collection: pd.DataFrame, df_uittredepunt_collection: pd.DataFrame, df_ondergrond_scenario_collection: pd.DataFrame) -> None:
    set_variable_names_expected = set()
    for index, row in df_variable_overview[df_variable_overview["variable_type"] == "Input"].iterrows():
        if pd.notna(row["variable_spreidingstype"]):
            set_variable_names_expected.update([str(index) + "_mean", str(index) + row["variable_spreidingstype"]])
        else:
            set_variable_names_expected.update([str(index)])

    set_variable_names_given = set(df_vak_collection.columns).union(df_uittredepunt_collection.columns, df_ondergrond_scenario_collection.columns)

    if set_variable_names_expected != set_variable_names_given:
        variables_missing = set_variable_names_expected - set_variable_names_given
        variables_surplus = set_variable_names_given - set_variable_names_expected
        
        def link_variables_to_source(variable_names: set[str]) -> pd.DataFrame:
            variables_names_without_suffix = set([variable_name_without_suffix(variable) for variable in variable_names])  # Note: make it a set to remove duplicates
            print("variables_names_without_suffix", variables_names_without_suffix)
            print("df_uittredepunt_collection.columns", df_uittredepunt_collection.columns)
            df = pd.DataFrame({'variable name': list(variables_names_without_suffix)})
            df["source input sheet"] = df["variable name"].apply(lambda x: "Vakken" if x in variable_name_without_suffix(df_vak_collection.columns.to_list()) else ("Uittredepunten" if x in variable_name_without_suffix(df_uittredepunt_collection.columns.to_list()) else ("Ondergrondscenarios" if x in variable_name_without_suffix(df_ondergrond_scenario_collection.columns.to_list()) else "Unknown")))
            return df

        if len(variables_missing) > 0:
            raise ValueError(f"\nMissing variables in input Excel file:\n\n{link_variables_to_source(variables_missing)}\n\nHave a look at the sheet 'Overzicht_variabelen' for an overview of expected variables.\nNote that if a variable (e.g. called 'my_variable') is stochastic, two input variables are expected: 'my_variable_mean' and 'my_variable_<variabele_spreidingstype>' (e.g. 'my_variable_stdev').")
        elif len(variables_surplus) > 0:
            raise ValueError(f"\nToo many variables in input Excel file:\n\n{link_variables_to_source(variables_surplus)}\n\nPossible causes:\n1. The variables are not defined in sheet 'Overzicht_variabelen'.\n2. The variables are defined in 'Overzicht_variabelen' but no 'variabele_spreidingstype' is specified.\n3. Unknown reason")


def check_variable_overview(df_variable_overview: pd.DataFrame) -> None:
    
    if df_variable_overview.index.has_duplicates:
        # Check duplicates
        raise ValueError(f"Duplicate variables found in sheet 'Overzicht_variabelen': {df_variable_overview.index[df_variable_overview.index.duplicated()].unique().tolist()}")

    for index, row in df_variable_overview[df_variable_overview["variable_type"].isin(["Input", "Constant"])].iterrows():
        # Check all input variables and constants
        
        if row["variable_distribution"] == "deterministic":
            if pd.notna(row["variable_spreidingstype"]):
                # Make sure all deterministic variables have no dispersion type specified (e.g. _stdev, _vc)
                raise ValueError(f"Deterministic variable '{index}' in sheet 'Overzicht_variabelen' should have no dispersion type speciifed (e.g. _stdev, _vc). Remove it.")
        else:
            if pd.isna(row["variable_spreidingstype"]):
                # Make sure all stochastic variables have a dispersion type specified (e.g. _stdev, _vc)
                raise ValueError(f"Stochastic variable '{index}' in sheet 'Overzicht_variabelen' has no dispersion type specified (e.g. _stdev, _vc). Add it.")


def check_attr_in_overview(attr_name: str, df_variable_overview: pd.DataFrame) -> None:
    # Check if attribute exists in the sheet 'Overzicht_variabelen'
    attr_name_without_suffix = variable_name_without_suffix(attr_name)
    if not attr_name_without_suffix in df_variable_overview.index:
        raise ValueError(f"Variable '{attr_name}' not found in sheet 'Overzicht_variabelen' of input Excel file")


def enforce_lower_upper_bounds(instance: Vak | Uittredepunt | OndergrondScenario, attr_name: str, attr_value: float, df_variable_overview: pd.DataFrame, id: str) -> None:
    # Check if value lies within upper and lower bounds in df_variable_overview (if specified)
    if attr_name.endswith("_mean"):
        # Note that only for mean values the bounds are checked, not for dispersion values (e.g. _stdev, _vc)
        attr_name_without_suffix = variable_name_without_suffix(attr_name, ["_mean"])
        if pd.notna(df_variable_overview.at[attr_name_without_suffix, "variable_mean_lower_bound"]):
            lower_bound = df_variable_overview.at[attr_name_without_suffix, 'variable_mean_lower_bound']
            if not (lower_bound <= attr_value):
                print(id)         
                raise ValueError(f"Variable '{attr_name_without_suffix}' of {instance.__class__.__name__} with id '{id}' has a mean value that exceeds the lower bound (value: {attr_value} < lower bound: {lower_bound})")

        if pd.notna(df_variable_overview.at[attr_name_without_suffix, "variable_mean_upper_bound"]):
            upper_bound = df_variable_overview.at[attr_name_without_suffix, 'variable_mean_upper_bound']
            if not (attr_value <= upper_bound):
                raise ValueError(f"Variable '{attr_name_without_suffix}' of {instance.__class__.__name__} with id '{id}' has a mean value that exceeds the upper bound (value: {attr_value} > upper bound: {upper_bound})")
