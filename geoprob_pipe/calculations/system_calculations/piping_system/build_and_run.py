from __future__ import annotations
from geoprob_pipe.calculations.system_calculations.piping_system.reliability_calculation import \
    PipingSystemReliabilityCalculation
from geoprob_pipe.calculations.system_calculations.piping_system.system_builder import PipingSystemBuilder
from typing import List, TYPE_CHECKING
from multiprocessing import Pool, cpu_count
from itertools import product
# noinspection PyPep8Naming
from geoprob_pipe.utils.loggers import TmpAppConsoleHandler as logger
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


# Worker functie for the parallel processing executor.
# In the worker a single calculation is set up and run based on the inputs.
# After running the results are split off the calculation,
# pickled and send to the main process.
def _worker(build_input):
    """ Rebuild and run the calculation in the subprocess. """

    # Split the parameter from the input (only one argument can be sent to the worker)
    vak, uittredepunt, ondergrond_scenario, df_settings, df_constants = build_input
    system_builder = PipingSystemBuilder()

    # Build the single calculation
    calc: PipingSystemReliabilityCalculation = system_builder.build_single_instance(
        vak=vak,
        uittredepunt=uittredepunt,
        ondergrond_scenario=ondergrond_scenario,
        df_settings=df_settings,
        df_constants=df_constants)
    calc.run()
    result = calc.export_result()

    # Test to make sure al the alpha value are pickled properly.
    # To be removed
    # for dp in calc.model_design_points:
    #     print(dp.identifier, "live alphas:", len(dp.alphas))
    # print("system live alphas:", len(calc.system_design_point.alphas))

    return result


def build_and_run_piping_system_calculations(
        geoprob_pipe: GeoProbPipe
        ) -> List[PipingSystemReliabilityCalculation]:
    logger.info("Now building and running calculations...")

    df_settings = geoprob_pipe.df_settings
    df = geoprob_pipe.input_data.df_overview_parameters
    df_constants = df[df["parameter_type"] == "constant"]

    system_builder = PipingSystemBuilder()

    # Instead of building full instances here, extract build parameters
    build_inputs = []
    for vak in geoprob_pipe.input_data.vakken.values():
        uittredepunten = vak.uittredepunten
        ondergrond_scenarios = vak.ondergrond_scenarios
        for uittredepunt, ondergrond_scenario in product(uittredepunten, ondergrond_scenarios):
            build_inputs.append((vak, uittredepunt, ondergrond_scenario, df_settings, df_constants))

    # Perform calculations
    with Pool(processes=min(len(build_inputs), cpu_count()-1)) as pool:
        results = pool.map(_worker, build_inputs)

    # Remake the calculation classes for further use in the code
    calculations = system_builder.build_instances(geoprob_pipe.input_data.vakken, df_settings, df_constants)

    # Add the results from the worker to the remade calculations
    for result, calculation in zip(results, calculations):
        calculation.import_results(result)
        # print("rehydrated model alphas:", [len(dp.alphas) for dp in calculation.model_design_points])
        # print("rehydrated system alphas:", len(calculation.system_design_point.alphas))
    return calculations
