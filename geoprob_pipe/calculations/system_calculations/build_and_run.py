from __future__ import annotations
from typing import TYPE_CHECKING
from geoprob_pipe.calculations.system_calculations.system_calculation_mapper import SYSTEM_CALCULATION_MAPPER
from multiprocessing import Pool, cpu_count
import os
from geoprob_pipe.results.construct_dataframes import (
    collect_df_beta_per_limit_state, collect_df_beta_per_scenario)
from geoprob_pipe.results.df_alphas_influence_factors_and_physical_values import (
    collect_stochast_values, calculate_derived_values)
# noinspection PyPep8Naming
from geoprob_pipe.utils.loggers import TmpAppConsoleHandler as logger

if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe
    from geoprob_pipe.calculations.system_calculations.system_base_objects.base_system_build import BaseSystemBuilder


def _worker(row_unique,
            geohydrologisch_model: str,
            geopackage_filepath: str,
            to_run_vakken_ids: list[int]
            ):
    try:
        system_builder: BaseSystemBuilder = (
            SYSTEM_CALCULATION_MAPPER[geohydrologisch_model]['system_builder'](
                geopackage_filepath=geopackage_filepath,
                to_run_vakken_ids=to_run_vakken_ids)
            )
        
        calc = system_builder.build_instance(row_unique=row_unique)
        calc.run()

        df_limit_state = collect_df_beta_per_limit_state(calc)
        df_scenario = collect_df_beta_per_scenario(calc)
        df_stochast = collect_stochast_values(calc)
        df_derived = calculate_derived_values(df_scenario,
                                              geohydrologisch_model)
        df_scenario = df_scenario.drop(columns=["system_calculation"])
    except Exception as e:
        print(f"[PID {os.getpid()}] ERROR: {e}", flush=True)
        raise
    return df_limit_state, df_scenario, df_stochast, df_derived, calc.validation_messages


def build_and_run_system_calculations(geoprob_pipe: GeoProbPipe):
    geohydrologisch_model = geoprob_pipe.input_data.geohydrologisch_model
    geopackage_filepath = geoprob_pipe.input_data.app_settings.geopackage_filepath
    to_run_vakken_ids = geoprob_pipe.input_data.app_settings.to_run_vakken_ids
    system_builder: BaseSystemBuilder = (
        SYSTEM_CALCULATION_MAPPER[geohydrologisch_model]['system_builder'](
            geopackage_filepath=geopackage_filepath,
            to_run_vakken_ids=to_run_vakken_ids)
        )
    logger.info("Now building calculations...")

    df_unique_combos = system_builder.setup_iteration_df()

    logger.info("Now running calculations...")

    args = [(row, geohydrologisch_model,
             geopackage_filepath, to_run_vakken_ids) for _, row in
            df_unique_combos.iterrows()]
    with Pool(processes=min(len(args), cpu_count()-1)) as pool:
        results = pool.starmap(_worker, args)
    
    return results
