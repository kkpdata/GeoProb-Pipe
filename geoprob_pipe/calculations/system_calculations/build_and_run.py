from __future__ import annotations
from typing import TYPE_CHECKING, List
from geoprob_pipe.calculations.system_calculations.system_calculation_mapper import SYSTEM_CALCULATION_MAPPER
from multiprocessing import Pool, cpu_count
import time
import math
from dataclasses import dataclass
from geoprob_pipe.results.construct_dataframes import (
    collect_df_beta_per_limit_state, collect_df_beta_per_scenario)
from geoprob_pipe.results.df_alphas_influence_factors_and_physical_values import (
    collect_stochast_values, calculate_derived_values)
# noinspection PyPep8Naming
from geoprob_pipe.utils.loggers import TmpAppConsoleHandler as logger

if TYPE_CHECKING:
    from pandas import DataFrame
    from geoprob_pipe import GeoProbPipe
    from geoprob_pipe.calculations.system_calculations.system_base_objects.base_system_build import BaseSystemBuilder
    from geoprob_pipe.utils.validation_messages import ValidationMessages

_BUILDER: BaseSystemBuilder
_MODEL: str


@dataclass
class CalcResult:
    """
    Dataclass om de resultaten te verzamelen vanuit de calculation.
    Bevat de volgende attributen:
    Dataframe: df_limit_state,
    Dataframe: df_scenario,
    Dataframe: df_stochast,
    Dataframe: df_derived,
    ValidationMessages: validation_message
    """
    df_limit_state: DataFrame
    df_scenario: DataFrame
    df_stochast: DataFrame
    df_derived: DataFrame
    validation_message: ValidationMessages


def _init_worker(geohydrologisch_model, geopackage_filepath,
                 to_run_vakken_ids):
    """ Initiator voor de worker, dit zorgt ervoor dat de tijdrovende
    stappen een keer per worker worden uitgevoerd en dan beschikbaar blijven
    voor iedere run."""
    global _BUILDER, _MODEL
    _MODEL = geohydrologisch_model
    _BUILDER = (
        SYSTEM_CALCULATION_MAPPER[geohydrologisch_model]["system_builder"](
            geopackage_filepath=geopackage_filepath, to_run_vakken_ids=to_run_vakken_ids))


def _worker(row_unique: dict):
    """ De worker functie die op de parallelle rekenkernen wordt gedraaid."""

    # Build and run calculations
    calc = _BUILDER.build_instance(row_unique=row_unique)
    calc.run()

    # Collect results
    df_limit_state = collect_df_beta_per_limit_state(calc)
    df_scenario = collect_df_beta_per_scenario(calc)
    df_stochast = collect_stochast_values(calc)
    df_derived = calculate_derived_values(df_scenario, _MODEL)
    df_scenario = df_scenario.drop(columns=["system_calculation"])

    # Return results (without calculation object)
    return CalcResult(df_limit_state, df_scenario, df_stochast, df_derived, calc.validation_messages)


def build_and_run_system_calculations(
    geoprob_pipe: GeoProbPipe
        ) -> List[CalcResult]:
    """ In deze functie worden de parameters voor de berekeningen verzamelt, aan de workers gegeven en vervolgens de
    resultaten verzameld. """
    geohydrologisch_model = geoprob_pipe.input_data.geohydrologisch_model
    geopackage_filepath = geoprob_pipe.input_data.app_settings.geopackage_filepath
    to_run_vakken_ids = geoprob_pipe.input_data.app_settings.to_run_vakken_ids
    system_builder: BaseSystemBuilder = (
        SYSTEM_CALCULATION_MAPPER[geohydrologisch_model]['system_builder'](
            geopackage_filepath=geopackage_filepath, to_run_vakken_ids=to_run_vakken_ids))

    logger.info("Now building and running calculations...")
    df_unique_combos = system_builder.setup_iteration_df()
    # Bepaal de parameters voor de multiprocessing setup en de logger
    n_threads: int = cpu_count() - 1
    n_calc_totaal: int = len(df_unique_combos)
    # Minimaal 5 berekeningen per chunk en grootte van chunk beperken zodat er gelogd kan worden.
    chunk_size: int = max(math.ceil(n_calc_totaal / (n_threads * 10)), 5)
    logger.info(
        f"Running {n_calc_totaal} calculations in chunks of {chunk_size} with {n_threads} parallel threads.")
    char_len_total = str(n_calc_totaal).__len__()
    logger.info(f"Progress: {0:>{char_len_total}} / {n_calc_totaal} calculations.")

    # Dicts zijn gemakkelijker te pickelen en daardoor sneller te verwerken dan pandas series.
    rows = [dict(zip(df_unique_combos.columns, r)) for r in df_unique_combos.itertuples(index=False, name=None)]

    last_report = time.time()
    done = 0
    results: List[CalcResult] = []
    pool_size = max(min(math.floor(n_calc_totaal / chunk_size), n_threads), 1)

    # Multiprocessing setup
    with Pool(processes=pool_size, initializer=_init_worker, initargs=(
            geohydrologisch_model, geopackage_filepath, to_run_vakken_ids)) as pool:

        for res in pool.imap_unordered(_worker, rows, chunksize=chunk_size):
            results.append(res)
            done += 1

            # Alleen kijken of er gelogd moet worden bij de laatste
            # berekening die uit de chunk komt.
            if done % chunk_size != 0:
                continue

            # Alleen loggen wanneer 30 seconden is gepasseerd
            now = time.time()
            if now - last_report < 30.0:
                continue

            # Log
            logger.info(f"Progress: {done:>{char_len_total}} / {n_calc_totaal} calculations.")
            last_report = now

    return results
