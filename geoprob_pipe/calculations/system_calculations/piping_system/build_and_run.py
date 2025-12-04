# from __future__ import annotations
# from geoprob_pipe.calculations.system_calculations.piping_system.reliability_calculation import \
#     PipingSystemReliabilityCalculation
# from geoprob_pipe.calculations.system_calculations.piping_system.system_builder import PipingSystemBuilder
# from typing import List, TYPE_CHECKING
# # noinspection PyPep8Naming
# from geoprob_pipe.utils.loggers import TmpAppConsoleHandler as logger
# if TYPE_CHECKING:
#     from geoprob_pipe import GeoProbPipe
#
#
# def build_and_run_piping_system_calculations(self: GeoProbPipe) -> List[PipingSystemReliabilityCalculation]:
#     logger.info(f"Now building and running calculations...")
#     system_builder = PipingSystemBuilder()
#     df = self.input_data.df_overview_parameters
#     df_constants = df[df["parameter_type"] == "constant"]
#     print("", f"Now building calculations...")
#     calculations =  system_builder.build_instances(
#         vak_collection=self.input_data.vakken,
#         df_settings=self.df_settings,
#         df_constants=df_constants)
#     print("", f"Now running calculations...")
#     for calc in calculations:
#         calc.run()
#     # TODO Nu Could Middel: Uitvoeren van system calculations ombouwen naar Threads.
#     #  Niet directe prio omdat het eigenlijk allemaal al snel doorgerekend wordt.
#     return calculations
