from __future__ import annotations
from pandas import DataFrame, concat, read_csv
from probabilistic_library import DesignPoint, Alpha
import os
from pathlib import Path
# from geoprob_pipe.calculations.limit_states.piping import z_piping
# from geoprob_pipe.calculations.limit_states.uplift_icw_model4a import z_uplift
# from geoprob_pipe.calculations.limit_states.heave_icw_model4a import z_heave
from typing import TYPE_CHECKING, Dict, List, Union, cast
import numpy as np

from geoprob_pipe.calculations.system_calculations.system_calculation_mapper import SYSTEM_CALCULATION_MAPPER

if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe
    from geoprob_pipe.calculations.system_calculations.system_base_objects.parallel_system_reliability_calculation import (
        ParallelSystemReliabilityCalculation)


def collect_stochast_values(calc: ParallelSystemReliabilityCalculation
                            ) -> DataFrame:
    """ Collects all Alphas, Influence factors and Physical values of
    the stochast input parameters. """

    # Create
    def create_df_rows_for_design_point(
            dp: DesignPoint, calc: ParallelSystemReliabilityCalculation
    ) -> List[Dict[str, Union[str, float]]]:
        rows_from_dp = []
        for alpha in dp.alphas:
            alpha: Alpha
            rows_from_dp.append({
                "uittredepunt_id": calc.metadata['uittredepunt_id'],
                "ondergrondscenario_id": calc.metadata['ondergrondscenario_naam'],
                "vak_id": calc.metadata['vak_id'],
                "design_point": dp.identifier,
                "variable": alpha.identifier,
                "distribution_type": alpha.variable.distribution.value,
                "alpha": alpha.alpha,
                "influence_factor": alpha.alpha * alpha.alpha,
                "physical_value": alpha.x
            })
        return rows_from_dp

    # Gather data
    rows = []
    for design_point in calc.model_design_points:
        rows.extend(create_df_rows_for_design_point(dp=design_point, calc=calc))
    sdp = cast(DesignPoint, calc.system_design_point)
    rows.extend(create_df_rows_for_design_point(dp=sdp, calc=calc))

    # Generate df from rows
    df = DataFrame(rows)

    return df


def _combine_stochast_values(geoprob_pipe: GeoProbPipe)  -> DataFrame:
    out_dir = os.path.join(
        str(geoprob_pipe.input_data.app_settings.workspace_dir),
        "exports",
        str(geoprob_pipe.input_data.app_settings.datetime_stamp),
        "temp",
        "stochast")
    df = concat(read_csv(p) for p in Path(out_dir).glob("*.csv"))
    return df


def calculate_derived_values(df_scenarios: DataFrame,
                             geohydrologisch_model: str):
    """ Re-calculates all derived physical values, i.e. intermediate values that were calculated inside the limit state
    functions. These are not returned by the probabilistic library, hence we need to re-calculate them.
    """

    # Get kwargs per calculation
    df = df_scenarios.copy(deep=True)
    df['physical_values'] = df['system_calculation'].apply(
        lambda sc: {alpha.variable.name: alpha.x for alpha in sc.system_design_point.alphas}
    )

    # Calculate the derived values
    def derived_values_single_calculation(model_naam: str, **kwargs):

        return_keys: List[str] = SYSTEM_CALCULATION_MAPPER[model_naam]["system_return_parameter_keys"]
        system_limit_state_function = SYSTEM_CALCULATION_MAPPER[model_naam]["limit_state_function"]
        derived_values = {key: value for key, value in zip(return_keys, system_limit_state_function(**kwargs))}

        # heave_return_keys = ["z_h", "lengte_voorland", "r_exit", "phi_exit", "h_exit", "d_deklaag", "i_exit"]
        # heave_derived_values = {key: value for key, value in zip(heave_return_keys, z_heave(**kwargs))}
        # uplift_return_keys = ["z_u", "L_voorland", "r_exit", "phi_exit", "h_exit", "d_deklaag", "dphi_c_u"]
        # uplift_derived_values = {key: value for key, value in zip(uplift_return_keys, z_uplift(**kwargs))}
        # piping_return_keys = [
        #     "z_p", "L_voorland", "lambda_voorland", "W_voorland", "L_kwelweg", "dh_c", "h_exit", "d_deklaag", "dh_red"]
        # piping_derived_values = {key: value for key, value in zip(piping_return_keys, z_piping(**kwargs))}
        return {**derived_values}

    df['derived_physical_values'] = df['physical_values'].apply(
        lambda kwargs: derived_values_single_calculation(
            model_naam=geohydrologisch_model, **kwargs)
    )

    # Create df with row per derived physical value
    df_new = df[["uittredepunt_id", "ondergrondscenario_id", "vak_id", "derived_physical_values"]].copy(deep=True)
    df_new['design_point'] = "system"
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


def _combine_derived_values(geoprob_pipe: GeoProbPipe)  -> DataFrame:
    out_dir = os.path.join(
        str(geoprob_pipe.input_data.app_settings.workspace_dir),
        "exports",
        str(geoprob_pipe.input_data.app_settings.datetime_stamp),
        "temp",
        "derived")
    df = concat(read_csv(p) for p in Path(out_dir).glob("*.csv"))
    return df


def construct_df(geoprob_pipe: GeoProbPipe):

    # Merge derived and stochast values
    df = concat([
        _combine_stochast_values(geoprob_pipe=geoprob_pipe),
        _combine_derived_values(geoprob_pipe=geoprob_pipe)
    ])

    # Sort
    df = df.sort_values(by=["vak_id", "uittredepunt_id", "ondergrondscenario_id", "design_point", "variable"])
    return df.reset_index(drop=True)
    # TODO Later Could Klein: Bespreken of we de physical values willen afronden? Af wellicht afrondden in de export.
