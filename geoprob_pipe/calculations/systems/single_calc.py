from __future__ import annotations
import sqlite3
from geoprob_pipe.calculations.systems.mappers.calculation_mapper\
    import CALCULATION_MAPPER
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe.calculations.systems.base_objects.base_system_build import BaseSystemBuilder
    from geoprob_pipe.calculations.systems.base_objects.system_calculation import SystemCalculation


EXAMPLE_SCRIPT_REPRODUCING_SINGLE_CALCULATION = r"""
from geoprob_pipe import (
    reproduce_single_calculation, ParallelSystemReliabilityCalculation)

calc: ParallelSystemReliabilityCalculation = reproduce_single_calculation(
    geopackage_filepath=r"/pad/naar/het/bestand/geoprob_pipe.gpkg",
    uittredepunt_id=1234,            # Replace with id of interest
    ondergrondscenario_naam="PL",    # Replace with scenario name of interest
)
"""


EXPLANATION_REPRODUCING_SINGLE_CALCULATION = """
Met de onderstaande code kun je in de Python console een enkele berekening reproduceren en inspecteren. Dit is 
bijvoorbeeld handig wanneer je de Python objecten wilt vergelijken met de gegenereerde in- en uitvoer. Of wanneer je 
een vergelijk maakt met de PTK-tool.

Om dit te doen kopieer je de onderstaande code naar de Python console. Zorg er voor dat je de Python console gebruikt 
waarin je GeoProb-Pipe ook hebt geïnstalleerd. Vervang eveneens het uittredepunt id met het id wat je wilt bekijken. 
Hetzelfde doe je voor de ondergrondscenario_naam.

Het reproduceren en herberekenen duurt slechts enkele seconden. Daarna kun je de objecten inspecteren.

Let op: Deze feature vergt enige ervaring met Python.
"""


def reproduce_single_calculation(
        geopackage_filepath: str, uittredepunt_id: int, ondergrondscenario_naam: str,
) -> SystemCalculation:

    # Fetch geohydrological model
    conn = sqlite3.connect(geopackage_filepath)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT "values" FROM geoprob_pipe_metadata WHERE metadata_type = ?',
        ("geohydrologisch_model",))
    geohydrologisch_model: str = cursor.fetchone()[0]

    # Fetch vak id
    cursor.execute(
        'SELECT vak_id FROM uittredepunten WHERE uittredepunt_id = ?',
        (uittredepunt_id,))
    vak_id: int = int(cursor.fetchone()[0])
    conn.close()

    # Construct calculation builder
    builder: BaseSystemBuilder = (
        CALCULATION_MAPPER[geohydrologisch_model]["system_builder"](
            geopackage_filepath=geopackage_filepath, to_run_vakken_ids=None))

    # Construct calculation
    row = {"uittredepunt_id": uittredepunt_id,
           "ondergrondscenario_naam": ondergrondscenario_naam,
           "vak_id": vak_id}
    calc = builder.build_instance(row_unique=row)
    calc.run()

    return calc
