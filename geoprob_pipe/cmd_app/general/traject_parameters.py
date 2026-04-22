from __future__ import annotations
from geoprob_pipe.utils.validation_messages import BColors
from InquirerPy import inquirer
from typing import TYPE_CHECKING, Optional
from geopandas import read_file
import sqlite3
from pandas import DataFrame
if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def _append_to_db(app_settings: ApplicationSettings, key: str, value):
    file_path = app_settings.geopackage_filepath
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO geoprob_pipe_metadata (metadata_type, "values") VALUES (?, ?);
        """,
        (key, value))
    conn.commit()
    cursor.close()


def _specify_traject_id(app_settings: ApplicationSettings):
    traject_id: Optional[str] = None
    traject_id_is_valid = False
    while traject_id_is_valid is False:
        traject_id: str = inquirer.text(
            message="Specificeer een tekstuele identificatie van het dijktraject die je graag gebruikt. ",
        ).execute()
        traject_id = traject_id.strip()

        if traject_id is "":
            print(BColors.OKBLUE, f"Je hebt geen traject_id gespecificeerd. Je invoer is leeg. ", BColors.ENDC)
            continue

        traject_id_is_valid = True

    _append_to_db(app_settings=app_settings, key='traject_id', value=traject_id)


def is_integer(s: str) -> bool:
    try:
        return float(s.replace('_', '')) % 1 == 0
    except ValueError:
        return False


def _specify_signaleringswaarde(app_settings: ApplicationSettings):
    signaleringswaarde_int: Optional[int] = None
    signaleringswaarde_is_valid = False
    while signaleringswaarde_is_valid is False:
        signaleringswaarde: str = inquirer.text(
            message="Specificeer de signaleringswaarde (geheel getal boven 10). ",
        ).execute()
        signaleringswaarde = signaleringswaarde.strip()

        if signaleringswaarde is "":
            print(BColors.OKBLUE, f"Je hebt geen signaleringswaarde gespecificeerd. Je invoer is leeg. ", BColors.ENDC)
            continue

        if not is_integer(s=signaleringswaarde):
            print(BColors.OKBLUE, f"Je ingevoerde signaleringswaarde is geen geheel getal.", BColors.ENDC)
            continue
        signaleringswaarde_int = int(signaleringswaarde)

        if signaleringswaarde_int < 10:
            print(BColors.OKBLUE, f"Je ingevoerde signaleringswaarde is kleiner dan 10. ", BColors.ENDC)
            continue

        signaleringswaarde_is_valid = True

    _append_to_db(app_settings=app_settings, key='signaleringswaarde', value=signaleringswaarde_int)


def _specify_ondergrens(app_settings: ApplicationSettings, signaleringswaarde: int):
    ondergrens_int: Optional[int] = None
    ondergrens_is_valid = False
    while ondergrens_is_valid is False:
        ondergrens: str = inquirer.text(
            message="Specificeer de ondergrens (geheel getal boven 10). ",
        ).execute()
        ondergrens = ondergrens.strip()

        if ondergrens is "":
            print(BColors.OKBLUE, f"Je hebt geen ondergrens gespecificeerd. Je invoer is leeg. ", BColors.ENDC)
            continue

        if not is_integer(s=ondergrens):
            print(BColors.OKBLUE, f"Je ingevoerde ondergrens is geen geheel getal.", BColors.ENDC)
            continue
        ondergrens_int = int(ondergrens)

        if ondergrens_int < 10:
            print(BColors.OKBLUE, f"Je ingevoerde ondergrens is kleiner dan 10. ", BColors.ENDC)
            continue

        if ondergrens_int > signaleringswaarde:
            print(BColors.OKBLUE, f"Je ingevoerde ondergrens ({ondergrens_int}) is groter dan "
                                  f"de signaleringswaarde {signaleringswaarde}. Deze moet gelijk of kleiner zijn. ",
                  BColors.ENDC)
            continue

        ondergrens_is_valid = True

    _append_to_db(app_settings=app_settings, key='ondergrens', value=ondergrens_int)


def _get_signaleringswaarde(app_settings: ApplicationSettings) -> int:
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT geoprob_pipe_metadata."values" 
        FROM geoprob_pipe_metadata 
        WHERE metadata_type='signaleringswaarde';
    """)
    result = cursor.fetchone()
    if not result:
        raise ValueError
    signaleringswaarde = result[0]
    conn.close()

    return int(signaleringswaarde)


def is_float(s: str) -> bool:
    try:
        _ = float(s.replace('_', ''))
        return True
    except ValueError:
        return False


def _specify_w(app_settings: ApplicationSettings):
    w_float: Optional[float] = None
    w_is_valid = False
    while w_is_valid is False:
        w: str = inquirer.text(
            message="Specificeer de w (decimaal getal tussen 0.0 en 1.0). Gebruikelijke waarde is 0.24.",
        ).execute()
        w = w.strip()

        if w is "":
            print(BColors.OKBLUE, f"Je hebt geen w gespecificeerd. Je invoer is leeg. ", BColors.ENDC)
            continue

        if not is_float(s=w):
            print(BColors.OKBLUE, f"Je ingevoerde w is geen decimaal getal.", BColors.ENDC)
            continue
        w_float = float(w)

        if w_float > 1.0:
            print(BColors.OKBLUE, f"Je ingevoerde w is groter dan 1.0. Het hoort een getal tussen 0.0 en 1.0 te zijn.",
                  BColors.ENDC)
            continue

        if w_float <= 0.0:
            print(BColors.OKBLUE, f"Je ingevoerde w is kleiner of gelijk aan 0.0. "
                                  f"Het hoort een getal tussen 0.0 en 1.0 te zijn. ", BColors.ENDC)
            continue

        w_is_valid = True

    _append_to_db(app_settings=app_settings, key='w', value=w_float)


def _specify_is_bovenrivierengebied(app_settings: ApplicationSettings):
    choices_list = ["Ja", "Nee"]
    choice = inquirer.select(
        message=f"Is dit traject in het bovenrivierengebied?", choices=choices_list, default=choices_list[0]).execute()
    choice_bool = False
    if choice == "Ja":
        choice_bool = True
    _append_to_db(app_settings=app_settings, key='is_bovenrivierengebied', value=choice_bool)


def added_traject_parameters(app_settings: ApplicationSettings) -> bool:
    df: DataFrame = read_file(app_settings.geopackage_filepath, layer="geoprob_pipe_metadata")
    metadata_types = [str(value) for value in df['metadata_type'].values.tolist()]

    if "traject_id" not in metadata_types:
        _specify_traject_id(app_settings=app_settings)

    if "signaleringswaarde" not in metadata_types:
        _specify_signaleringswaarde(app_settings=app_settings)

    signaleringswaarde = _get_signaleringswaarde(app_settings=app_settings)
    if "ondergrens" not in metadata_types:
        _specify_ondergrens(app_settings=app_settings, signaleringswaarde=signaleringswaarde)

    if "w" not in metadata_types:
        _specify_w(app_settings=app_settings)

    if "is_bovenrivierengebied" not in metadata_types:
        _specify_is_bovenrivierengebied(app_settings=app_settings)

    return True
