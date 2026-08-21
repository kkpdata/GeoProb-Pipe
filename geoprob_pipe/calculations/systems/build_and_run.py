from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from geoprob_pipe.calculations.systems.mappers.calculations import (
    CALCULATION_MAPPER)
from multiprocessing import Pool, cpu_count
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
import logging
from pandas import DataFrame
import os
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe, SystemCalculation
    from geoprob_pipe.calculations.systems.base_objects\
        .base_system_build import BaseSystemBuilder
    from geoprob_pipe.utils.validation_messages import ValidationMessages


logger = logging.getLogger("geoprob-pipe")


_BUILDER: BaseSystemBuilder
_MODEL: str


@dataclass
class CalcResult:
    """
    Dataclass om de resultaten te verzamelen vanuit de calculation.
    Bevat de volgende attributen:
    Dataframe: df_limit_state bevat resultaten van de afzonderlijke grenstoestandsfuncties (Z_u, Z_h en Z_p)
    Dataframe: df_scenario_rp bevat resultaten van max(Z_u, Z_h, Z_p).
    Dataframe: df_scenario_cp bevat resultaten van de combinatie van de afzonderlijke grenstoestandsfuncties
    Dataframe: df_scenario_final bevat resultaten op basis van beslisregels van de afzonderlijke berekeningsmethoden. Zie construct_dataframes.py voor meer details.
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


def _init_worker(
        geohydrologisch_model: str,
        geopackage_filepath: str,
        to_run_vakken_ids: Optional[List[int]]):
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


def _logging_code():
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

    return log_buffer, buffer_handler, root, prev_level


def _run_calculation(row_unique: dict) -> SystemCalculation:
    debug: bool = os.environ.get("GEOPROB_DEBUG", False)
    if debug: logger.debug("Start berekening voor %s", row_unique)

    # Run calculation
    calc: SystemCalculation = _BUILDER.build_instance(row_unique=row_unique)
    calc.run()
    if debug: logger.debug("SystemCalculation voltooid.")

    # Remainder is logging in case of validation messages or debug modus
    if calc.validation_messages.df: logger.debug(f"Validation messages:\n{calc.validation_messages.df}")

    if debug:
        logger.debug("Limit states print:")
        for lm in calc.results.dps_limit_states:
            lm.print()

        logger.debug("Combine project print:")
        calc.results.combine_project.design_point.print()

        logger.debug("Reliability project print:")
        calc.results.reliability_project.design_point.print()

    return calc


def _collect_results(calc: SystemCalculation) -> CalcResult:
    debug: bool = os.environ.get("GEOPROB_DEBUG", False)
    df_limit_state = collect_df_beta_limit_state(calc)
    if debug: logger.debug(f"df_limit_state:\n{df_limit_state}")
    if any(r == 0 for r in df_limit_state.total_model_runs):
        logger.warning("Limit state with 0 total model runs encountered. Notify developer and re-run calculations. ")

    df_scenario_rp = collect_df_beta_scenario_rp(calc)
    if debug: logger.debug(f"df_scenario_rp:\n{df_scenario_rp}")

    df_scenario_cp = collect_df_beta_scenario_cp(calc)
    if debug: logger.debug(f"df_scenario_cp:\n{df_scenario_cp}")

    df_scenario_final = collect_df_beta_scenario_final(calc)

    df_stochast = collect_stochast_values(calc, df_scenario_final=df_scenario_final)
    if debug: logger.debug(f"df_stochast:\n{df_stochast.to_string()}")

    if df_scenario_cp.converged is True and any(a >= 0.99 for a in df_stochast.alpha):
        logger.warning("Unrealistically dominant (alpha >= 0.99) parameter found in combined project.")
    if df_scenario_rp.converged is True and any(a >= 0.99 for a in df_stochast.alpha):
        logger.warning("Unrealistically dominant (alpha >= 0.99) parameter found in reliability project.")
    df_derived = calculate_derived_values(df_scenarios_final=df_scenario_final, geohydrologisch_model=_MODEL)
    df_scenario_rp = df_scenario_rp.drop(columns=["system_calculation"])
    df_scenario_cp = df_scenario_cp.drop(columns=["system_calculation"])
    df_scenario_final = df_scenario_final.drop(columns=["system_calculation"])

    return CalcResult(
        df_limit_state=df_limit_state, df_scenario_rp=df_scenario_rp, df_scenario_cp=df_scenario_cp,
        df_scenario_final=df_scenario_final, df_stochast=df_stochast, df_derived=df_derived,
        validation_message=calc.validation_messages)


def _worker(row_unique: dict):
    """ De worker functie die op de parallelle rekenkernen wordt gedraaid.

    :param row_unique: Identificatie naar unieke berekening, bijvoorbeeld
        {'uittredepunt_id': 1, 'ondergrondscenario_naam': 'scenario1', 'vak_id': 4}.
    :return: Tuple[Optional[CalcResult], Optional[str], Optional[dict]]
    """
    log_buffer, buffer_handler, root, prev_level = _logging_code()

    # noinspection PyBroadException
    try:
        with redirect_stdout(log_buffer), redirect_stderr(log_buffer):
            # logger = logging.getLogger(__name__)
            calc = _run_calculation(row_unique)
            result = _collect_results(calc)
            return result, log_buffer.getvalue(), row_unique

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


class BuildAndRunCalculations:
    """ In dit object worden de parameters voor de berekeningen verzamelt, aan de workers gegeven en vervolgens de
    resultaten verzameld. """

    def __init__(self, geoprob_pipe: GeoProbPipe):
        """ Init zet dit object op, maar het uitvoeren van de berekeningen gaat via de method .run(). """

        self.geoprob_pipe: GeoProbPipe = geoprob_pipe
        self.geohydrologisch_model: str = geoprob_pipe.input_data.geohydrologisch_model
        self.geopackage_filepath: str = geoprob_pipe.input_data.app_settings.geopackage_filepath
        self.to_run_vakken_ids: str = geoprob_pipe.input_data.app_settings.to_run_vakken_ids

        self._construct_system_builder_and_settings()
        self._setup_calculation_progress_variables()

        # Run logic with method .run()

    def _construct_system_builder_and_settings(self):
        """ Opzetten van de system builder en andere settings voor de berekeningen. """

        logger.info("Now preparing for calculations...")
        self.system_builder: BaseSystemBuilder = CALCULATION_MAPPER[self.geohydrologisch_model]['system_builder'](
                geopackage_filepath=self.geopackage_filepath,
                to_run_vakken_ids=self.to_run_vakken_ids)
        self.df_unique_combos = self.system_builder.setup_iteration_df()

        # Bepaal de parameters voor de multiprocessing setup en de logger
        self.n_threads: int = cpu_count() - 1
        self.n_calc_totaal: int = len(self.df_unique_combos)

        # Minimaal 5 berekeningen per chunk en grootte van chunk beperken zodat er gelogd kan worden.
        self.chunk_size: int = max(math.ceil(self.n_calc_totaal / (self.n_threads * 10)), 5)

    def _setup_calculation_progress_variables(self):
        """ Simpel initiëren van een aantal variabelen die nodig zijn tijdens de berekeningen. """

        self.last_report: float = time.time()
        self.done = 0
        self.log_errors = 0
        self.error_rows = []
        self.char_len_total: int = str(self.n_calc_totaal).__len__()
        self.log_rows = []
        self.results: List[CalcResult] = []

    def _report_calculation_progress_to_user(self):
        """ Gedurende het uitvoeren van de berekening koppelt deze method terug wat de progressie is. """

        # If finished
        error_count_append = ""
        if self.log_errors > 0:
            error_count_append = f" (of which {self.log_errors} failed calculations)"
        if self.n_calc_totaal == self.done:
            logger.info(f"Progress: {self.done:>{self.char_len_total}} / {self.n_calc_totaal} calculations"
                        f"{error_count_append}.")

        # Alleen kijken of er gelogd moet worden bij de laatste berekening die uit de chunk komt.
        if self.done % self.chunk_size != 0:
            return

        # Alleen loggen wanneer 30 seconden is gepasseerd
        now = time.time()
        if now - self.last_report < 30.0:
            return

        logger.info(
            f"Progress: {self.done:>{self.char_len_total}} / {self.n_calc_totaal} calculations{error_count_append}.")
        self.last_report = now

    def _push_resulting_error_messages_to_database(self):
        """ Aan eind van run pushed deze method de errors (if any) naar de database. """

        conn = sqlite3.connect(self.geopackage_filepath)
        table_name = "calculation_logs"
        df_logs = DataFrame(data=self.log_rows)
        df_logs.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.commit()
        conn.close()
        if self.log_errors > 0:
            logger.error(f"There are {self.log_errors} failed calculations. The calculation logs are stored inside the "
                         f"GeoPackage in table '{table_name}'. The following rows are marked:"
                         f"\n{self.error_rows}")

    def run(self) -> List[CalcResult]:

        logger.info(
            f"Running {self.n_calc_totaal} calculations in chunks of {self.chunk_size}"
            f" with {self.n_threads} parallel threads.")
        logger.info(
            f"Progress: {0:>{self.char_len_total}} / {self.n_calc_totaal} calculations.")

        rows = [dict(zip(self.df_unique_combos.columns, r))
                for r in self.df_unique_combos.itertuples(index=False, name=None)]
        pool_size = max(min(math.floor(self.n_calc_totaal / self.chunk_size), self.n_threads), 1)

        # Multiprocessing setup
        with Pool(processes=pool_size, initializer=_init_worker, initargs=(
                self.geohydrologisch_model, self.geopackage_filepath, self.to_run_vakken_ids)) as pool:

            for res, logs, row in pool.imap_unordered(_worker, rows, chunksize=self.chunk_size):
                if isinstance(res, CalcResult):
                    self.results.append(res)
                if isinstance(logs, str):
                    self.log_rows.append({
                        "uittredepunt_id": row["uittredepunt_id"],
                        "ondergrondscenario_naam": row["ondergrondscenario_naam"],
                        "vak_id": row["vak_id"],
                        "logs": logs,
                    })
                    if any(level in logs for level in ("WARNING", "ERROR", "CRITICAL")):
                        self.log_errors += 1
                        self.error_rows.append(row)
                self.done += 1

                self._report_calculation_progress_to_user()

        self._push_resulting_error_messages_to_database()
        return self.results
