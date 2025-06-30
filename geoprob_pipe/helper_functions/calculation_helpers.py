import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable
import pandas as pd
from probabilistic_library import CombineProject, CombinerMethod, CombineType
from geoprob_pipe.classes.ondergrond_scenario import OndergrondScenario
from geoprob_pipe.classes.reliability_calculation import CombinedReliabilityCalculation, ReliabilityCalculation
from geoprob_pipe.classes.uittredepunt import Uittredepunt
from geoprob_pipe.classes.vak import VakCollection
import logging
import threading

from geoprob_pipe.helper_functions.z_functions import MODEL_NAMES

logger = logging.getLogger("geoprob_pipe_logger")


def _result_dict(reliability_calculation: CombinedReliabilityCalculation|ReliabilityCalculation) -> dict:
    """ Helper function to convert a ReliabilityCalculation instance to a dictionary for easy access. """
    return {
        "uittredepunt_id": reliability_calculation.id["uittredepunt"],
        "uittredepunt": reliability_calculation.uittredepunt,
        "ondergrondscenario_id": reliability_calculation.id["ondergrondscenario"],
        "ondergrondscenario": reliability_calculation.ondergrond_scenario,
        "reliability_calculation": reliability_calculation,
        "converged": reliability_calculation.is_converged,
        "beta": reliability_calculation.beta,
        "failure_probability": reliability_calculation.reliability_project.design_point.probability_failure,
        "alphas": reliability_calculation.alphas,
        "influence_factors": reliability_calculation.influence_factors,
    }


def start_calculations(
        list_reliability_calculations: list[ReliabilityCalculation],
        model_name: str,
):
    """ Starts running the provided calculations through a ThreadPoolExecutor. """
    total = list_reliability_calculations.__len__()
    completed = 0
    start_time = time.time()
    lock = threading.Lock()

    # Define execution function
    def run_reliability_calculation(reliability_calculation: ReliabilityCalculation):
        nonlocal completed
        try:
            reliability_calculation.run()
        except Exception as e:
            print(f"ERROR: Could not run running reliability calculation {reliability_calculation.id}: {e}")
        finally:
            with lock:
                completed += 1

    # Define function that reports progress
    def progress_reporter():
        while True:
            with lock:
                if completed >= total:
                    duration = int(time.time() - start_time)
                    logger.info(f"[{model_name}] Finished all {total} of calculations in under {duration} seconds. "
                                f"That is on average under {round(duration/total, 3)} seconds per calculation.")
                    break
            time.sleep(1)

    # Start reporting thread
    reporter_thread = threading.Thread(target=progress_reporter)
    reporter_thread.start()

    # # Run calculations in parallel
    # with ThreadPoolExecutor() as executor:
    #     futures = [executor.submit(run_reliability_calculation, calc) for calc in list_reliability_calculations]
    #     for _ in as_completed(futures):
    #         pass  # Just to ensure all tasks complete


    # Run calculations in parallel
    with ThreadPoolExecutor() as executor:
        executor.map(run_reliability_calculation, list_reliability_calculations)


def build_and_run_unique_model_calculations(
        model: Callable,
        vak_collection: VakCollection,
        df_overview_parameters: pd.DataFrame,
        df_settings: pd.DataFrame,
) -> pd.DataFrame:
    """

    Notes:
      1. Due to limitations in the probabilistic_library, we cannot first set up all calculations and then run them.
         After setting up calculations for each model (uplift/heave/piping), we need to run them immediately before
         setting up the next model.
      2. Not all combinations of uittredepunten and ondergrondscenarios are valid, so we need a helper-loop through the
         vakken which holds the valid combinations
      3. Nested for-loops are inefficient but used on purpose since there are no heavy calculations and it's easily
         understandable

    :param model:
    :param vak_collection:
    :param df_overview_parameters:
    :param df_settings:
    :return:
    """

    model_name = {}

    # Build calculations
    list_calculations = []
    for vak in vak_collection.values():
        for uittredepunt in vak.uittredepunten:
            for ondergrond_scenario in vak.ondergrond_scenarios:
                list_calculations.append(
                    ReliabilityCalculation(
                        uittredepunt=uittredepunt,
                        ondergrond_scenario=ondergrond_scenario,
                        model=model,
                        df_constants=df_overview_parameters[df_overview_parameters["parameter_type"] == "constant"],
                        df_settings=df_settings
                    )
                )

    # Run calculations
    start_calculations(list_calculations, model_name=MODEL_NAMES[model.__name__])

    # Return the calculations in a DataFrame for easy access. The DataFrame is sorted by uittredepunt and by
    # ondergrondscenario
    return pd.DataFrame([_result_dict(calc) for calc in list_calculations]).sort_values(
        by=["uittredepunt_id", "ondergrondscenario_id"]).reset_index(drop=True)


def build_and_run_combined_calculation(
        df_group: pd.DataFrame,
        uittredepunt: Uittredepunt,
        ondergrond_scenario: OndergrondScenario
) -> pd.Series:
    """

    :param df_group: All three models (uplift/heave/piping) for a unique combination of uittredepunt and
        ondergrondscenario
    :param uittredepunt:
    :param ondergrond_scenario:
    :return: Series containing the combined reliability calculation result for the unique combination of uittredepunt
        and ondergrondscenario
    """

    # Extract the model results of uplift/heave/piping from the DataFrame group
    models = {row["model"]: row["reliability_calculation"] for _, row in df_group.iterrows()}

    # Set up and run combined project
    combined_project = CombineProject()
    combined_project.design_points.append(models["uplift"].design_point)
    combined_project.design_points.append(models["heave"].design_point)
    combined_project.design_points.append(models["piping"].design_point)
    combined_project.settings.combine_type = CombineType.parallel
    combined_project.settings.combiner_method = CombinerMethod.importance_sampling
    combined_project.run()
    # TODO Nu Should Middel: Implementeer ThreadPoolExecutor voor 'run combined'.
    
    return pd.Series(_result_dict(CombinedReliabilityCalculation(combined_project, uittredepunt, ondergrond_scenario)))
