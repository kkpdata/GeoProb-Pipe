from __future__ import annotations
import sqlite3
import json
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def _to_text(v):
    if v is None:
        return None
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, (bool, int, float)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def _upsert_metadata(conn, table, metadata_type, value):
    sql_update = f'UPDATE {table} SET "values" = ? WHERE metadata_type = ?'
    sql_insert = f'INSERT INTO {table} (metadata_type, "values") VALUES (?, ?)'

    with conn:  # transaction
        cur = conn.execute(sql_update, (value, metadata_type))
        if cur.rowcount == 0:
            conn.execute(sql_insert, (metadata_type, value))


def update_metadata(geoprob_pipe: GeoProbPipe):
    gpkg_path = geoprob_pipe.input_data.app_settings.geopackage_filepath
    table = "geoprob_pipe_metadata"

    # tekst setup voor variable values
    if geoprob_pipe.input_data.app_settings.to_run_vakken_ids:
        ran_vakken_ids = geoprob_pipe.input_data.app_settings.to_run_vakken_ids
    else:
        ran_vakken_ids = "all"

    n_calcs: int = len(geoprob_pipe.results.df_beta_scenarios)
    n_points: int = len(geoprob_pipe.results.df_beta_uittredepunten)
    n_vakken: int = len(geoprob_pipe.results.df_beta_vakken)
    ratio_points: float = n_points / len(geoprob_pipe.input_data.uittredepunten.gdf)

    records = [
        {"metadata_type": "last_calculation_run_datetime",
         "values": geoprob_pipe.input_data.app_settings.datetime_stamp},
        {"metadata_type": "last_calculation_rub_in_seconds",
         "values": geoprob_pipe.time_diff.total_seconds()},
        {"metadata_type": "last_calculation_run_vakken_to_run",
         "values": ran_vakken_ids},
        {"metadata_type": "last_calculation_run_nr_of_calculations",
            "values": n_calcs},
        {"metadata_type": "last_calculation_run_nr_of_uittredepunten",
            "values": n_points},
        {"metadata_type": "last_calculation_run_nr_of_vakken",
            "values": n_vakken},
        {"metadata_type": "last_calculation_run_percentage_of_uittredepunten",
            "values": ratio_points * 100}
    ]

    conn = sqlite3.connect(gpkg_path)

    for r in records:
        _upsert_metadata(conn=conn, table=table,
                         metadata_type=r["metadata_type"],
                         value=_to_text(r["values"]))
    conn.commit()
    conn.close()
