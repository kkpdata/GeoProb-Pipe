from geoprob_pipe.calculations.systems.single_calc import create_single_calc
from geoprob_pipe.calculations.systems.base_objects.system_calculation import (
        SystemCalculation
        )

calc: SystemCalculation = create_single_calc(
    geopackage_filepath=r"C:\Users\vinji\Python\GEOprob-Pipe\Bestandenuitwisseling\Analyse16-1_V5.geoprob_pipe\Analyse16-1_V5.geoprob_pipe.gpkg",
    uittredepunt_id=160,
    ondergrondscenario_naam="PL",
)
