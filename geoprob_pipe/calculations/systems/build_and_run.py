from __future__ import annotations
from typing import TYPE_CHECKING, List
from geoprob_pipe.calculations.systems.mappers.calculation_mapper import (
    CALCULATION_MAPPER)
from multiprocessing import Pool, cpu_count
import logging
from io import StringIO
import sqlite3
import traceback
from contextlib import redirect_stdout, redirect_stderr
import time
import math
from dataclasses import dataclass
from geoprob_pipe.results.construct_dataframes import (
    collect_df_beta_limit_state, collect_df_beta_scenario_rp, collect_df_beta_scenario_cp,
    collect_df_beta_scenario_final)
from geoprob_pipe.results.alphas_and_physical_values import (
    collect_stochast_values, calculate_derived_values)
# noinspection PyPep8Naming
from geoprob_pipe.utils.loggers import TmpAppConsoleHandler as logger
from pandas import DataFrame

if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe
    from geoprob_pipe.calculations.systems.base_objects\
        .base_system_build import BaseSystemBuilder
    from geoprob_pipe.utils.validation_messages import ValidationMessages

_BUILDER: BaseSystemBuilder
_MODEL: str


@dataclass
class CalcResult:
    """
    Dataclass om de resultaten te verzamelen vanuit de calculation.
    Bevat de volgende attributen:
    Dataframe: df_limit_state,
    Dataframe: df_scenario_rp,
    Dataframe: df_scenario_cp,
    Dataframe: df_scenario_final,
    Dataframe: df_stochast,
    Dataframe: df_derived,
    ValidationMessages: validation_message
    """
    df_limit_state: DataFrame
    df_scenario_rp: DataFrame
    df_scenario_cp: DataFrame
    df_scenario_final: DataFrame
    df_stochast: DataFrame
    df_derived: DataFrame
    validation_message: ValidationMessages


def _init_worker(geohydrologisch_model, geopackage_filepath,
                 to_run_vakken_ids):
    """ Initiator voor de worker, dit zorgt ervoor dat de tijdrovende
    stappen een keer per worker worden uitgevoerd en dan beschikbaar blijven
    voor iedere run.
    """
    global _BUILDER, _MODEL
    _MODEL = geohydrologisch_model
    _BUILDER = (
        CALCULATION_MAPPER[geohydrologisch_model]["system_builder"](
            geopackage_filepath=geopackage_filepath,
            to_run_vakken_ids=to_run_vakken_ids))


def _worker(row_unique: dict):
    """ De worker functie die op de parallelle rekenkernen wordt gedraaid.
    """
    log_buffer = StringIO()
    buffer_handler = logging.StreamHandler(log_buffer)
    buffer_handler.setLevel(logging.DEBUG)

    buffer_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(processName)s %(levelname)s] %(name)s: %(message)s",
        "%Y-%m-%d %H:%M:%S",
    ))

    root = logging.getLogger()
    prev_level = root.level
    root.setLevel(logging.DEBUG)
    root.addHandler(buffer_handler)
    logging.captureWarnings(True)

    # noinspection PyBroadException
    try:
        with redirect_stdout(log_buffer), redirect_stderr(log_buffer):
            # Build and run calculations
            calc = _BUILDER.build_instance(row_unique=row_unique)
            calc.run()

            # Collect results
            df_limit_state = collect_df_beta_limit_state(calc)
            df_scenario_rp = collect_df_beta_scenario_rp(calc)
            df_scenario_cp = collect_df_beta_scenario_cp(calc)
            df_scenario_final = collect_df_beta_scenario_final(calc)
            df_stochast = collect_stochast_values(calc, df_scenario_final=df_scenario_final)
            df_derived = calculate_derived_values(df_scenarios_final=df_scenario_final, geohydrologisch_model=_MODEL)
            df_scenario_rp = df_scenario_rp.drop(columns=["system_calculation"])
            df_scenario_cp = df_scenario_cp.drop(columns=["system_calculation"])
            df_scenario_final = df_scenario_final.drop(columns=["system_calculation"])

            # Return results (without calculation object)
            return CalcResult(
                df_limit_state=df_limit_state, df_scenario_rp=df_scenario_rp, df_scenario_cp=df_scenario_cp,
                df_scenario_final=df_scenario_final, df_stochast=df_stochast, df_derived=df_derived,
                validation_message=calc.validation_messages
            ), None, None

    except Exception:
        tb = traceback.format_exc()
        log_buffer.write(tb)
        buffer_handler.flush()
        return None, log_buffer.getvalue(), row_unique
    finally:
        # Handler altijd verwijderen
        logging.captureWarnings(False)
        root.removeHandler(buffer_handler)
        root.setLevel(prev_level)
        buffer_handler.close()


def build_and_run_system_calculations(geoprob_pipe: GeoProbPipe) -> List[CalcResult]:
    """ In deze functie worden de parameters voor de berekeningen verzamelt,
    aan de workers gegeven en vervolgens de resultaten verzameld.
    """
    geohydrologisch_model = geoprob_pipe.input_data.geohydrologisch_model
    geopackage_filepath = (
        geoprob_pipe.input_data.app_settings.geopackage_filepath)
    to_run_vakken_ids = geoprob_pipe.input_data.app_settings.to_run_vakken_ids
    system_builder: BaseSystemBuilder = (
        CALCULATION_MAPPER[geohydrologisch_model]['system_builder'](
            geopackage_filepath=geopackage_filepath,
            to_run_vakken_ids=to_run_vakken_ids))

    logger.info("Now building and running calculations...")
    df_unique_combos = system_builder.setup_iteration_df()
    # Bepaal de parameters voor de multiprocessing setup en de logger
    n_threads: int = cpu_count() - 1
    n_calc_totaal: int = len(df_unique_combos)
    # Minimaal 5 berekeningen per chunk en grootte van chunk beperken
    # zodat er gelogd kan worden.
    chunk_size: int = max(math.ceil(n_calc_totaal / (n_threads * 10)), 5)
    logger.info(
        f"Running {n_calc_totaal} calculations in chunks of {chunk_size}"
        f" with {n_threads} parallel threads.")
    char_len_total = str(n_calc_totaal).__len__()
    logger.info(
        f"Progress: {0:>{char_len_total}} / {n_calc_totaal} calculations.")

    # Dicts zijn gemakkelijker te pickelen en daardoor sneller te
    # verwerken dan pandas series.
    rows = [dict(zip(df_unique_combos.columns, r))
            for r in df_unique_combos.itertuples(index=False, name=None)]

    last_report = time.time()
    done = 0
    results: List[CalcResult] = []
    pool_size = max(min(math.floor(n_calc_totaal / chunk_size), n_threads), 1)

    # Multiprocessing setup
    error_rows = []
    with Pool(processes=pool_size, initializer=_init_worker, initargs=(
            geohydrologisch_model, geopackage_filepath, to_run_vakken_ids
            )) as pool:

        for res, error_logs, row in pool.imap_unordered(_worker, rows, chunksize=chunk_size):
            if isinstance(res, CalcResult):
                results.append(res)
            if isinstance(error_logs, str):
                error_rows.append({
                    "uittredepunt_id": row["uittredepunt_id"],
                    "ondergrondscenario_naam": row["ondergrondscenario_naam"],
                    "vak_id": row["vak_id"],
                    "error_logs": error_logs,
                })
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
            error_count_append = ""
            if error_rows.__len__() > 0:
                error_count_append = f" (of which {error_rows.__len__()} failed calculations)"
            logger.info(f"Progress: {done:>{char_len_total}} / {n_calc_totaal} calculations{error_count_append}.")
            last_report = now

    # Push errors to database (if any)
    conn = sqlite3.connect(geoprob_pipe.input_data.app_settings.geopackage_filepath)
    table_name = "calculation_error_logs"
    if error_rows.__len__() > 0:
        df_errors = DataFrame(data=error_rows)
        df_errors.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()
        logger.error(f"There are {error_rows.__len__()} failed calculations. Error logs are stored inside the "
                     f"GeoPacakge in table '{table_name}'.")
    else:
        # Remove old table (if exists)
        cur = conn.cursor()
        cur.execute(f"DROP TABLE IF EXISTS {table_name};")
        conn.commit()
        conn.close()

    return results
