from __future__ import annotations
import sqlite3
from geoprob_pipe.calculations.system_calculations.system_calculation_mapper\
    import SYSTEM_CALCULATION_MAPPER
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe.calculations.system_calculations.system_base_objects\
        .base_system_build import BaseSystemBuilder
    from geoprob_pipe.calculations.system_calculations.system_base_objects\
        .parallel_system_reliability_calculation import (
            ParallelSystemReliabilityCalculation
            )


def reproduce_single_calc(
        geopackage_filepath: str,
        uittredepunt_id: int,
        ondergrondscenario_naam: str,
        ) -> ParallelSystemReliabilityCalculation:

    conn = sqlite3.connect(geopackage_filepath)
    cursor = conn.cursor()

    # cursor.execute('SELECT "values" FROM geoprob_pipe_metadata WHERE metadata_type = ?', ("last_calculation_run_vakken_to_run",))
    # temp: str = cursor.fetchone()[0]
    # temp_list: list[str] = temp.strip("[]").split(",")
    # to_run_vakken_ids: list[int] = []
    # for item in temp_list:
    #     to_run_vakken_ids.append(int(item))

    cursor.execute('SELECT "values" FROM geoprob_pipe_metadata WHERE metadata_type = ?', ("geohydrologisch_model",))
    geohydrologisch_model: str = cursor.fetchone()[0]

    cursor.execute('SELECT vak_id FROM uittredepunten WHERE uittredepunt_id = ?', (uittredepunt_id,))
    vak_id: int = int(cursor.fetchone()[0])
    conn.close()

    builder: BaseSystemBuilder = (
        SYSTEM_CALCULATION_MAPPER[geohydrologisch_model]["system_builder"](
            geopackage_filepath=geopackage_filepath,
            to_run_vakken_ids=None)
        )

    row = {"uittredepunt_id": uittredepunt_id,
           "ondergrondscenario_naam": ondergrondscenario_naam,
           "vak_id": vak_id}

    calc = builder.build_instance(row_unique=row)
    calc.run()
    return calc
