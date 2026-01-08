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
    from geoprob_pipe.calculations.system_calculations.system_base_objects.parallel_system_reliability_calculation import \
        ParallelSystemReliabilityCalculation


def _worker(row_unique,
            geohydrologisch_model: str,
            geopackage_filepath: str,
            to_run_vakken_ids: list[int],
            out_dir: str):
    try:
        system_builder: BaseSystemBuilder = (
            SYSTEM_CALCULATION_MAPPER[geohydrologisch_model]['system_builder'](
                geopackage_filepath=geopackage_filepath,
                to_run_vakken_ids=to_run_vakken_ids)
            )
        calc = system_builder.build_instance(row_unique=row_unique)
        calc.run()

        # Export to temp files
        df_limit_state = collect_df_beta_per_limit_state(calc)
        limit_state_dir = os.path.join(out_dir, "limit_state")
        os.makedirs(limit_state_dir, exist_ok=True)
        limit_state_filename = f"limit_state_{row_unique["uittredepunt_id"]}.csv"
        df_limit_state.to_csv(os.path.join(limit_state_dir, limit_state_filename))

        df_scenario = collect_df_beta_per_scenario(calc)
        scenario_dir = os.path.join(out_dir, "scenario")
        os.makedirs(scenario_dir, exist_ok=True)
        scenario_filename = f"scenario_{row_unique["uittredepunt_id"]}.csv"
        df_scenario.to_csv(os.path.join(scenario_dir, scenario_filename))

        df_stochast = collect_stochast_values(calc)
        stochast_dir = os.path.join(out_dir, "stochast")
        os.makedirs(stochast_dir, exist_ok=True)
        stochast_filename = f"stochast_{row_unique["uittredepunt_id"]}.csv"
        df_stochast.to_csv(os.path.join(stochast_dir, stochast_filename))

        df_derived = calculate_derived_values(df_scenario,
                                              geohydrologisch_model)
        derived_dir = os.path.join(out_dir, "derived")
        os.makedirs(derived_dir, exist_ok=True)
        derived_filename = f"derived_{row_unique["uittredepunt_id"]}.csv"
        df_derived.to_csv(os.path.join(derived_dir, derived_filename))
        
    except Exception as e:
        print(f"[PID {os.getpid()}] ERROR: {e}", flush=True)
        raise


def build_and_run_system_calculations(geoprob_pipe: GeoProbPipe):
    out_dir = os.path.join(
        str(geoprob_pipe.input_data.app_settings.workspace_dir),
        "exports",
        str(geoprob_pipe.input_data.app_settings.datetime_stamp),
        "temp")
    os.makedirs(out_dir, exist_ok=True)
    # Determine geohydrologisch model
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
             geopackage_filepath, to_run_vakken_ids,
             out_dir) for _, row in
            df_unique_combos.iterrows()]
    with Pool(processes=min(len(args), cpu_count()-1)) as pool:
        pool.starmap(_worker, args)
