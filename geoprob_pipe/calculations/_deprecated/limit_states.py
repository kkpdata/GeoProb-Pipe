# import time
# from concurrent.futures import ThreadPoolExecutor
# from typing import Callable
# import pandas as pd
# from geoprob_pipe.classes.reliability_calculation import ReliabilityCalculation
# from geoprob_pipe.input_data.vak import VakCollection
# import logging
# import threading
# from geoprob_pipe.calculations.system_calculations.piping_system.limit_state_functions import MODEL_NAMES
# from geoprob_pipe.calculations.utils import _result_dict
#
#
# logger = logging.getLogger("geoprob_pipe_logger")


# def start_calculations(
#         list_reliability_calculations: list[ReliabilityCalculation],
#         model_name: str,
# ):
#     """ Starts running the provided calculations through a ThreadPoolExecutor. """
#     total = list_reliability_calculations.__len__()
#     completed = 0
#     start_time = time.time()
#     lock = threading.Lock()
#
#     # Define execution function
#     def run_reliability_calculation(reliability_calculation: ReliabilityCalculation):
#         nonlocal completed
#         try:
#             reliability_calculation.run()
#         except Exception as e:
#             print(f"ERROR: Could not run running reliability calculation {reliability_calculation.id}: {e}")
#         finally:
#             with lock:
#                 completed += 1
#
#     # Define function that reports progress
#     def progress_reporter():
#         while True:
#             with lock:
#                 if completed >= total:
#                     duration = int(time.time() - start_time)
#                     logger.info(f"[{model_name}] Finished all {total} of calculations in under {duration} seconds. "
#                                 f"That is on average under {round(duration/total, 3)} seconds per calculation.")
#                     break
#             time.sleep(1)
#
#     # Start reporting thread
#     reporter_thread = threading.Thread(target=progress_reporter)
#     reporter_thread.start()
#
#     # # Run calculations in parallel
#     # with ThreadPoolExecutor() as executor:
#     #     futures = [executor.submit(run_reliability_calculation, calc) for calc in list_reliability_calculations]
#     #     for _ in as_completed(futures):
#     #         pass  # Just to ensure all tasks complete
#
#
#     # Run calculations in parallel
#     with ThreadPoolExecutor() as executor:
#         executor.map(run_reliability_calculation, list_reliability_calculations)


# def build_and_run_unique_model_calculations(
#         model: Callable,
#         vak_collection: VakCollection,
#         df_overview_parameters: pd.DataFrame,
#         df_settings: pd.DataFrame,
# ) -> pd.DataFrame:
#     """
#
#     Notes:
#       1. Due to limitations in the probabilistic_library, we cannot first set up all calculations and then run them.
#          After setting up calculations for each model (uplift/heave/piping), we need to run them immediately before
#          setting up the next model.
#       2. Not all combinations of uittredepunten and ondergrondscenarios are valid, so we need a helper-loop through the
#          vakken which holds the valid combinations
#       3. Nested for-loops are inefficient but used on purpose since there are no heavy calculations, and it's easily
#          understandable
#
#     :param model:
#     :param vak_collection:
#     :param df_overview_parameters:
#     :param df_settings:
#     :return:
#     """
#
#     # Build calculations
#     list_calculations = []
#     for vak in vak_collection.values():
#         for uittredepunt in vak.uittredepunten:
#             for ondergrond_scenario in vak.ondergrond_scenarios:
#                 list_calculations.append(
#                     ReliabilityCalculation(
#                         uittredepunt=uittredepunt,
#                         ondergrond_scenario=ondergrond_scenario,
#                         model=model,
#                         df_constants=df_overview_parameters[df_overview_parameters["parameter_type"] == "constant"],
#                         df_settings=df_settings
#                     )
#                 )
#
#     # Run calculations
#     start_calculations(list_calculations, model_name=MODEL_NAMES[model.__name__])
#
#     # Return the calculations in a DataFrame for easy access. The DataFrame is sorted by uittredepunt and by
#     # ondergrondscenario
#     return pd.DataFrame([_result_dict(calc) for calc in list_calculations]).sort_values(
#         by=["uittredepunt_id", "ondergrondscenario_id"]).reset_index(drop=True)
#
