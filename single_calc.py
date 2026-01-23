from geoprob_pipe.calculations.system_calculations.single_calc import create_single_calc
from geoprob_pipe.calculations.system_calculations.system_base_objects.parallel_system_reliability_calculation import (
        ParallelSystemReliabilityCalculation
        )

calc: ParallelSystemReliabilityCalculation = create_single_calc(
    geopackage_filepath=r"C:\Users\vinji\Python\GEOprob-Pipe\Bestandenuitwisseling\Analyse16-1_V5.geoprob_pipe\Analyse16-1_V5.geoprob_pipe.gpkg",
    uittredepunt_id=160,
    ondergrondscenario_naam="PL",
)
