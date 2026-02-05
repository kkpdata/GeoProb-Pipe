from __future__ import annotations
from importlib.metadata import version, PackageNotFoundError
from typing import TYPE_CHECKING
import sqlite3
if TYPE_CHECKING:
    from geoprob_pipe.questionnaire.cmd import ApplicationSettings


def get_geoprob_pipe_version_number() -> str:
    geoprob_pipe_version_number = "DEV"
    try: geoprob_pipe_version_number = version('geoprob_pipe')
    except PackageNotFoundError: pass
    return geoprob_pipe_version_number


def get_geohydrological_model(app_settings: ApplicationSettings) -> str:
    # Get geohydrological model
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT geoprob_pipe_metadata."values" 
        FROM geoprob_pipe_metadata 
        WHERE metadata_type='geohydrologisch_model';
    """)
    result = cursor.fetchone()
    if not result:
        raise ValueError
    model_string = result[0]
    conn.close()

    return model_string

