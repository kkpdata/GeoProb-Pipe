from __future__ import annotations
from typing import TYPE_CHECKING
from geoprob_pipe.calculations.system_calculations.system_calculation_mapper import SYSTEM_CALCULATION_MAPPER
from multiprocessing import Pool, cpu_count
import os
import time
import math
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


def _starify(args):
    return _worker(*args)


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
    n_threads: int = cpu_count() - 1
    n_calc_totaal: int = len(df_unique_combos)
    chunk_size: int = math.ceil(n_calc_totaal / (n_threads * 10))
    logger.info(f"Running with chunks of {chunk_size} calculations with {n_threads} parallel threads.")
    logger.info(f"Progress: 0 / {n_calc_totaal} calculations.")

    args = [(row, geohydrologisch_model,
             geopackage_filepath, to_run_vakken_ids) for _, row in
            df_unique_combos.iterrows()]

    last_report = time.time()
    done = 0
    results = []
    pool_size = (min(math.floor(n_calc_totaal / chunk_size), n_threads)
                 if n_calc_totaal > 0 else 1)
    with Pool(processes=pool_size) as pool:
        for res in pool.imap_unordered(_starify, args, chunksize=chunk_size):
            results.append(res)
            done += 1
            now = time.time()
            if now - last_report >= 30:
                logger.info(f"Progress: {done} / {n_calc_totaal} calculations.")
                last_report = now
    return results
