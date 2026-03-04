from __future__ import annotations
from pandas import DataFrame, concat
from probabilistic_library import DesignPoint, Alpha
from typing import TYPE_CHECKING, Dict, List, Union, cast, Optional
import numpy as np
from geoprob_pipe.calculations.systems.mappers.calculation_mapper import CALCULATION_MAPPER
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe
    from geoprob_pipe.calculations.systems.base_objects.system_calculation import (
        SystemCalculation)
    from geoprob_pipe.calculations.systems.build_and_run import CalcResult


def collect_stochast_values(calc: SystemCalculation, df_scenario_final: DataFrame) -> DataFrame:
    """ Collects all Alphas, Influence factors and Physical values of the stochast input parameters. """

    # Get method used
    df = df_scenario_final.copy(deep=True)
    assert df.__len__() == 1, \
        f"Developer note: Assumption that this dataframe must have 1 row at all times. If triggered, then investigate."
    method_used = df.iloc[0]['method_used']

    # Create
    def create_df_rows_for_design_point(dp: DesignPoint, append: Optional[str] = None) -> List[Dict[str, Union[str, float]]]:
        rows_from_dp = []
        design_point_method = method_used
        if append:
            design_point_method = f"{design_point_method} ({append})"
        for alpha in dp.alphas:
            alpha: Alpha
            rows_from_dp.append({
                "uittredepunt_id": calc.metadata['uittredepunt_id'],
                "ondergrondscenario_id": calc.metadata['ondergrondscenario_naam'],
                "vak_id": calc.metadata['vak_id'],
                "design_point": design_point_method,
                "variable": alpha.identifier,
                "distribution_type": alpha.variable.distribution.value,
                "alpha": alpha.alpha,
                "influence_factor": alpha.alpha * alpha.alpha,
                "physical_value": alpha.x})
        return rows_from_dp

    rows = []

    if method_used == "1: Max Limit States":
        # Gather for separate limit states
        for design_point in calc.results.dps_limit_states:
            rows.extend(create_df_rows_for_design_point(dp=design_point, append=design_point.identifier))

    elif method_used == "2: Reliability Project":
        # Gather for reliability project
        dp_reliability = cast(DesignPoint, calc.results.dp_reliability)
        rows.extend(create_df_rows_for_design_point(dp=dp_reliability))

    elif method_used == "3: Combined Project":
        # Gather for combine project
        dp_combine = cast(DesignPoint, calc.results.dp_combine)
        rows.extend(create_df_rows_for_design_point(dp=dp_combine))

    else:
        raise ValueError(f"Unknown method_used '{method_used}'. Contact a developer.")

    # Generate df from rows
    df = DataFrame(rows)

    return df


def _combine_stochast_values(calc_results: List[CalcResult])  -> DataFrame:
    df = concat((result.df_stochast for result in calc_results), ignore_index=True)
    return df


def calculate_derived_values(df_scenarios_final: DataFrame, geohydrologisch_model: str):
    """ Re-calculates all derived physical values, i.e. intermediate values that were calculated inside the limit state
    functions. These are not returned by the probabilistic library, hence we need to re-calculate them. """

    # Get kwargs per calculation
    df = df_scenarios_final.copy(deep=True)
    assert df.__len__() == 1, \
        f"Developer note: Assumption that this dataframe must have 1 row at all times. If triggered, then investigate."
    method_used = df.iloc[0]['method_used']
    if method_used == "1: Max Limit States":
        df['physical_values'] = df['system_calculation'].apply(
            lambda sc: {alpha.variable.name: alpha.x
                        for dp in sc.results.dps_limit_states
                        for alpha in dp.alphas})
    elif method_used == "2: Reliability Project":
        df['physical_values'] = df['system_calculation'].apply(
            lambda sc: {alpha.variable.name: alpha.x for alpha in sc.results.dp_reliability.alphas})
    elif method_used == "3: Combined Project":
        df['physical_values'] = df['system_calculation'].apply(
            lambda sc: {alpha.variable.name: alpha.x for alpha in sc.results.dp_combine.alphas})
    else:
        raise NotImplementedError

    # Calculate the derived values
    def derived_values_single_calculation(model_naam: str, **kwargs):
        return_keys: List[str] = CALCULATION_MAPPER[model_naam]["system_return_parameter_keys"]
        system_limit_state_function = CALCULATION_MAPPER[model_naam]["limit_state_function"]
        derived_values = {key: value for key, value in zip(return_keys, system_limit_state_function(**kwargs))}
        return {**derived_values}

    df['derived_physical_values'] = df['physical_values'].apply(
        lambda kwargs: derived_values_single_calculation(model_naam=geohydrologisch_model, **kwargs))

    # Create df with row per derived physical value
    df_new = df[["uittredepunt_id", "ondergrondscenario_id", "vak_id", "derived_physical_values"]].copy(deep=True)
    df_new['design_point'] = method_used
    df_new['distribution_type'] = "derived"
    df_new['alpha'] = np.nan
    df_new['influence_factor'] = np.nan

    # Expand dictionary to new rows
    df_new = concat([
        DataFrame({
            **row.drop('derived_physical_values'),
            'variable': list(row['derived_physical_values'].keys()),
            'physical_value': list(row['derived_physical_values'].values())
        })
        for _, row in df_new.iterrows()
    ], ignore_index=True)

    return df_new


def _combine_derived_values(calc_results: List[CalcResult]) -> DataFrame:
    return concat((result.df_derived for result in calc_results), ignore_index=True)


def construct_df(geoprob_pipe: GeoProbPipe):

    # Merge derived and stochast values
    df = concat([
        _combine_stochast_values(geoprob_pipe.calc_results),
        _combine_derived_values(geoprob_pipe.calc_results)
    ])

    # Sort
    df = df.sort_values(by=["vak_id", "uittredepunt_id", "ondergrondscenario_id", "design_point", "variable"])
    return df.reset_index(drop=True)
    # TODO Later Could Klein: Bespreken of we de physical values willen afronden? Af wellicht afrondden in de export.
