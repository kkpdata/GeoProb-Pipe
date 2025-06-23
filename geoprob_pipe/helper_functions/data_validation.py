from __future__ import annotations  # makes all annotations lazy (no quotes needed)

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from geoprob_pipe.classes.vak import Vak
    from geoprob_pipe.classes.uittredepunt import Uittredepunt
    from geoprob_pipe.classes.ondergrond_scenario import OndergrondScenario

from typing import Any, Optional, Type

from geoprob_pipe.helper_functions.parameter_functions import (
    strip_suffix_from_list_parameter_names,
)


def check_attribute_already_exists(instance: Vak | Uittredepunt | OndergrondScenario, attr_name: str) -> None:
    if hasattr(instance, attr_name):
        raise AttributeError(f"{instance.__class__.__name__} already has an attribute named '{attr_name}', please rename the column in the input Excel file.")


def checks_input_parameters(df_overview_parameters: pd.DataFrame, df_vak_collection: pd.DataFrame, df_uittredepunt_collection: pd.DataFrame, df_ondergrond_scenario_collection: pd.DataFrame) -> None:
    
    # Parameter names given
    set_parameter_names_given = set(df_vak_collection.columns).union(df_uittredepunt_collection.columns, df_ondergrond_scenario_collection.columns)
    
    if not all(isinstance(param_name, str) for param_name in set_parameter_names_given):
        # Parameter names should all be strings
        raise ValueError(f"Parameter names in sheet 'Vakken'/'Uittredepunten'/'Ondergrondscenarios' must all be strings. Found invalid names: {[type(param_name).__name__ for param_name in set_parameter_names_given if not isinstance(param_name, str)]}")
    
    if any(" " in param_name for param_name in set_parameter_names_given):
        # Prevent spaces in parameter names since we're using dot notation for accessing attributes later in the tool
        raise ValueError(f"Parameter names in sheet 'Vakken'/'Uittredepunten'/'Ondergrondscenarios' are not allowed to contain spaces. Found invalid names: {[param_name for param_name in set_parameter_names_given if ' ' in param_name]}")

    # Parameter names expected
    set_parameter_names_expected = set()
    
    for index, row in df_overview_parameters[df_overview_parameters["parameter_type"] == "metadata"].iterrows():
        # All expected metadata should be given in de Vakken/Uittredepunten/Ondergrondscenarios sheets
        set_parameter_names_expected.update([str(index)])

    for index, row in df_overview_parameters[df_overview_parameters["parameter_type"] == "variable"].iterrows():
        # All expected variables should be given in de Vakken/Uittredepunten/Ondergrondscenarios sheets, but we need to check if
        # the suffix "_mean" should be added (necessary if the input is stochastic). Otherwise, if deterministic, simply add the variable name
        if pd.notna(row["parameter_spreidingstype"]):
            set_parameter_names_expected.update([str(index) + "_mean", str(index) + row["parameter_spreidingstype"]])
        else:
            set_parameter_names_expected.update([str(index)])

    if any(" " in c for c in set_parameter_names_expected):
        # Prevent spaces in parameter names since we're using dot notation for accessing attributes later in the tool 
        raise ValueError(f"Parameter names in sheet 'Overzicht_parameters' are not allowed to contain spaces: {[c for c in set_parameter_names_expected if ' ' in c]}")

    # Check for missing or surplus input parameters
    if set_parameter_names_expected != set_parameter_names_given:
        parameters_missing = set_parameter_names_expected - set_parameter_names_given
        parameters_surplus = set_parameter_names_given - set_parameter_names_expected
        
        def link_variables_to_source(variable_names: set[str]) -> pd.DataFrame:
            df = pd.DataFrame({'variable name': list(strip_suffix_from_list_parameter_names(variable_names))})  # Note: make it a set to remove duplicates, then cast it back again to a list
            df["source input sheet"] = df["variable name"].apply(lambda x: "Vakken" if x in strip_suffix_from_list_parameter_names(df_vak_collection.columns) else ("Uittredepunten" if x in strip_suffix_from_list_parameter_names(df_uittredepunt_collection.columns) else ("Ondergrondscenarios" if x in strip_suffix_from_list_parameter_names(df_ondergrond_scenario_collection.columns) else "Unknown")))
            return df

        if len(parameters_missing) > 0:
            raise ValueError(f"\nMissing variables in input Excel file:\n\n{link_variables_to_source(parameters_missing)}\n\nHave a look at the sheet 'Overzicht_parameters' for an overview of expected variables.\nNote that if a variable (e.g. called 'my_variable') is stochastic, two input variables are expected: 'my_variable_mean' and 'my_variable_<variabele_spreidingstype>' (e.g. 'my_variable_stdev').")
        elif len(parameters_surplus) > 0:
            raise ValueError(f"\nToo many variables in input Excel file:\n\n{link_variables_to_source(parameters_surplus)}\n\nPossible causes:\n1. The variables are not defined in sheet 'Overzicht_parameters'.\n2. The variables are defined in 'Overzicht_parameters' but no 'variabele_spreidingstype' is specified.\n3. Unknown reason")


def checks_overview_parameters(df_overview_parameters: pd.DataFrame) -> None:
    
    if not all(isinstance(i, str) for i in df_overview_parameters.index):
        raise ValueError(f"All parameter names in sheet 'Overzicht_parameters' must be strings/text. Found: {[type(i).__name__ for i in df_overview_parameters.index if not isinstance(i, str)]}")

    if df_overview_parameters.index.has_duplicates:
        # Check duplicates
        raise ValueError(f"Duplicate variables found in sheet 'Overzicht_parameters': {df_overview_parameters.index[df_overview_parameters.index.duplicated()].unique().tolist()}")

    for index, row in df_overview_parameters[df_overview_parameters["parameter_type"].isin(["Input", "Constant"])].iterrows():
        # Check all input variables and constants
        
        if row["parameter_distribution"] == "deterministic":
            if pd.notna(row["parameter_spreidingstype"]):
                # Make sure all deterministic variables have no dispersion type specified (e.g. _stdev, _vc)
                raise ValueError(f"Deterministic variable '{index}' in sheet 'Overzicht_parameters' should have no dispersion type speciifed (e.g. _stdev, _vc). Remove it.")
        else:
            if pd.isna(row["parameter_spreidingstype"]):
                # Make sure all stochastic variables have a dispersion type specified (e.g. _stdev, _vc)
                raise ValueError(f"Stochastic variable '{index}' in sheet 'Overzicht_parameters' has no dispersion type specified (e.g. _stdev, _vc). Add it.")


def check_attribute_in_overview(attr_name_without_suffix: str, df_overview_parameters: pd.DataFrame) -> None:
    if not attr_name_without_suffix in df_overview_parameters.index:
        raise ValueError(f"Variable '{attr_name_without_suffix}' not found in sheet 'Overzicht_parameters' of input Excel file")


def is_number(var_value: Any) -> float:
    return isinstance(var_value, (int, float)) and not pd.isna(var_value)


def enforce_lower_upper_bounds(parameter_dict: dict, id_print: str) -> None:
    # Note: only appplicable to input parameters (variables and constants)

    
    # Value (mean) is accessed differently for deterministic and stochastic parameters
    attr_value = parameter_dict["value"] if parameter_dict["distribution"] == "deterministic" else parameter_dict["mean"]
    
    # Make sure the attribute value is a number (int/float) before checking bounds
    if not is_number(attr_value):
        raise ValueError(f"Value of parameter '{parameter_dict["name"]}' ({id_print}) should be a number (int/float) since lower/upper bounds were specified, but it's {attr_value} of type {type(attr_value)}")
    
    # Check if value lies within upper and lower bounds in parameter_dict (if specified)
    if pd.notna(parameter_dict["lower_bound_mean"]):
        if not is_number(parameter_dict["lower_bound_mean"]):
            raise ValueError(f"Lower bound of parameter {parameter_dict["name"]} should be a number (int/float) but got {parameter_dict["lower_bound_mean"]} of type {type(parameter_dict["lower_bound_mean"])}")
        if not (parameter_dict["lower_bound_mean"] <= attr_value):
            raise ValueError(f"Parameter '{parameter_dict["name"]}' ({id_print}) has a mean value that exceeds the lower bound (value: {attr_value} < lower bound: {parameter_dict["lower_bound_mean"]})")

    if pd.notna(parameter_dict["upper_bound_mean"]):
        if not is_number(parameter_dict["upper_bound_mean"]):
            raise ValueError(f"Upper bound of parameter {parameter_dict["name"]} should be a number (int/float) but got {parameter_dict["upper_bound_mean"]} of type {type(parameter_dict["upper_bound_mean"])}")
        if not (attr_value <= parameter_dict["upper_bound_mean"]):
            raise ValueError(f"Parameter '{parameter_dict["name"]}' ({id_print}) has a mean value that exceeds the upper bound (value: {attr_value} > upper bound: {parameter_dict["upper_bound_mean"]})")

