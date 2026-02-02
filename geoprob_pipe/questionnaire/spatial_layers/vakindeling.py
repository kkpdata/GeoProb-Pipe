from __future__ import annotations
from geopandas import read_file
from InquirerPy import inquirer
import warnings
from geoprob_pipe.questionnaire.utils.spatial import load_dijktraject_linestring
from geoprob_pipe.utils.gdf import convert_mls_geom_column_to_ls
import os
from pathlib import Path
from shapely import LineString, MultiLineString
from shapely.ops import substring
from typing import TYPE_CHECKING, Optional
from pandas import DataFrame
from geopandas import GeoDataFrame
import fiona
from geoprob_pipe.utils.validation_messages import BColors
if TYPE_CHECKING:
    from geoprob_pipe.questionnaire.cmd import ApplicationSettings


def added_vakindeling(app_settings: ApplicationSettings) -> bool:
    layers = fiona.listlayers(app_settings.geopackage_filepath)
    if "vakindeling" in layers:
        check_validity_vakindeling(app_settings=app_settings)
        return True
    else:
        request_vakindeling_filepath(app_settings)
        return True


def check_validity_vakindeling(app_settings: ApplicationSettings):
    gdf_dijktraject: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="dijktraject")
    gdf_dijktraject_geom = gdf_dijktraject.iloc[0].geometry
    if isinstance(gdf_dijktraject_geom, MultiLineString):
        assert gdf_dijktraject_geom.geoms.__len__() == 1
        ls_dijktraject: LineString = gdf_dijktraject_geom.geoms[0]
    elif isinstance(gdf_dijktraject_geom, LineString):
        ls_dijktraject = gdf_dijktraject_geom
    else:
        raise NotImplementedError(f"Type of '{type(gdf_dijktraject_geom)} is not yet supported. Please contact the "
                                  f"developer.'")
    dijktraject_length = round(ls_dijktraject.length, 2)

    gdf_vakindeling: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="vakindeling")
    vakindeling_geometries = gdf_vakindeling.geometry.tolist()
    vakindeling_total_length = round(sum([geom.length for geom in vakindeling_geometries]), 2)

    assert dijktraject_length == vakindeling_total_length
    print(BColors.OKBLUE, f"✔  Vakindeling al toegevoegd.", BColors.ENDC)


def import_from_geopackage(filepath: str) -> GeoDataFrame:
    layer_name: Optional[str] = None
    layer_name_is_valid = False
    while layer_name_is_valid is False:
        layer_name: str = inquirer.text(
            message="Specificeer de laag met de vakindeling. "
                    "Type 'listlayers' om een overzicht te krijgen van de geopackage-layers. ",
        ).execute()

        layer_names = fiona.listlayers(filepath)
        layer_names.sort()
        layers_str = ", ".join(layer_names)
        if layer_name == "listlayers":
            print(BColors.OKBLUE, f"De volgende layers zijn beschikbaar in de geopackage: {layers_str}", BColors.ENDC)
            continue
        elif layer_name not in layer_names:
            print(BColors.OKBLUE, f"De laag name '{layer_name}' bestaat niet. De volgende layers zijn beschikbaar in "
                                  f"de geopackage: {layers_str}", BColors.ENDC)
            continue

        layer_name_is_valid = True

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Measured \\(M\\) geometry types are not supported.*")
        gdf: GeoDataFrame = read_file(filepath, layer=layer_name)
    return gdf


def import_from_geodatabase(filepath: str) -> GeoDataFrame:
    layer_name: Optional[str] = None
    layer_name_is_valid = False
    while layer_name_is_valid is False:
        layer_name: str = inquirer.text(
            message="Specificeer de laag met de vakindeling. "
                    "Type 'listlayers' om een overzicht te krijgen van de geodatabase-layers. ",
        ).execute()

        layer_names = fiona.listlayers(filepath)
        layer_names.sort()
        layers_str = ", ".join(layer_names)
        if layer_name == "listlayers":
            print(BColors.OKBLUE, f"De volgende layers zijn beschikbaar in de geodatabase: {layers_str}", BColors.ENDC)
            continue
        elif layer_name not in layer_names:
            print(BColors.OKBLUE, f"De laag name '{layer_name}' bestaat niet. De volgende layers zijn beschikbaar in "
                                  f"de geodatabase: {layers_str}", BColors.ENDC)
            continue

        layer_name_is_valid = True

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Measured \\(M\\) geometry types are not supported.*")
        gdf: GeoDataFrame = read_file(filepath, layer=layer_name)
    return gdf


def request_vakindeling_filepath(app_settings: ApplicationSettings):
    filepath: Optional[str] = None
    filepath_is_valid = False
    while filepath_is_valid is False:
        filepath: str = inquirer.text(
            message="Specificeer het volledige bestandspad naar de geopackage/shapefile/geodatabase waarin de "
                    "vakindeling van de dijk zit.",
        ).execute()

        filepath = filepath.replace('"', '')

        if not (filepath.endswith(".gpkg") or filepath.endswith(".shp") or filepath.endswith(".gdb")):
            print(BColors.WARNING, f"Het bestand moet of een geopackage, shapefile of geodatabase zijn. Jouw invoer "
                                   f"eindigt op de extensie .{filepath.split(sep='.')[-1]}.", BColors.ENDC)
            continue
        if not os.path.exists(filepath):
            print(BColors.WARNING, f"Het opgegeven bestandspad bestaat niet.", BColors.ENDC)
            continue

        filepath_is_valid = True

    if filepath.endswith(".shp"):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Measured \\(M\\) geometry types are not supported.*")
            gdf: GeoDataFrame = read_file(filepath)
        validate_vakindeling(app_settings, gdf=gdf)
    elif filepath.endswith(".gpkg"):
        gdf: GeoDataFrame = import_from_geopackage(filepath=filepath)
        validate_vakindeling(app_settings, gdf=gdf)
    elif filepath.endswith(".gdb"):
        gdf: GeoDataFrame = import_from_geodatabase(filepath=filepath)
        validate_vakindeling(app_settings, gdf=gdf)
    else:
        raise NotImplementedError(f"File with extension {filepath.split(sep='.')[-1]} is not yet supported. "
                                  f"Please make a request.")


def validate_vakindeling(app_settings: ApplicationSettings, gdf: GeoDataFrame):
    """ Validates the vakindeling shape, with some conversions if they can applied safely. """
    gdf = convert_mls_geom_column_to_ls(gdf=gdf)
    assert gdf.geometry.apply(lambda geom: isinstance(geom, LineString)).all(), \
        "De opgegeven vakindeling heeft niet voor elk vak een geometry. De applicatie sluit nu af."
    specify_column_with_vaknaam(app_settings, gdf=gdf)


def specify_column_with_vaknaam(app_settings: ApplicationSettings, gdf: GeoDataFrame):
    column_name: Optional[str] = None
    column_name_is_valid = False
    while column_name_is_valid is False:
        column_name: str = inquirer.text(
            message="Specificeer de kolom waarin de vaknaam staat. Type 'listcolumns' om "
                    "een overzicht te krijgen van de kolommen. ",
        ).execute()

        column_names = gdf.columns
        columns_str = ", ".join(column_names)
        if column_name == "listcolumns":
            print(BColors.OKBLUE,
                  f"De volgende kolommen zijn beschikbaar in de spatial layer: {columns_str}", BColors.ENDC)
            continue
        elif column_name not in column_names:
            print(BColors.OKBLUE, f"De kolom naam '{column_name}' bestaat niet. De volgende kolommen zijn beschikbaar "
                                  f"in de spatial layer: {columns_str}", BColors.ENDC)
            continue

        column_name_is_valid = True

    column_name: str
    specify_column_with_vak_id(app_settings, gdf=gdf, kolom_vak_naam=column_name)


def is_numeric_integer(val):
    try:
        return float(val) % 1 == 0
    except (ValueError, TypeError):
        return False


def specify_column_with_vak_id(app_settings: ApplicationSettings, gdf: GeoDataFrame, kolom_vak_naam: str):
    kolom_vak_id: Optional[str] = None
    column_name_is_valid = False
    while column_name_is_valid is False:
        kolom_vak_id: str = inquirer.text(
            message="Specificeer de kolom waarin het vak id staat. Indien onnodig, type 'nvt'. Type 'listcolumns' om "
                    "een overzicht te krijgen van de kolommen. ",
        ).execute()

        column_names = gdf.columns
        columns_str = ", ".join(column_names)
        if kolom_vak_id.lower() == "nvt":
            align_vak_shp_to_dijktraject(
                app_settings, gdf_vakindeling=gdf, kolom_vak_naam=kolom_vak_naam, kolom_vak_id=None)
            return
        elif kolom_vak_id == "listcolumns":
            print(BColors.OKBLUE,
                  f"De volgende kolommen zijn beschikbaar in de spatial layer: {columns_str}", BColors.ENDC)
            continue
        elif kolom_vak_id not in column_names:
            print(BColors.OKBLUE, f"De kolom naam '{kolom_vak_id}' bestaat niet. De volgende kolommen zijn beschikbaar "
                                  f"in de spatial layer: {columns_str}", BColors.ENDC)
            continue

        # Ensure column values are unique and integers
        if gdf[kolom_vak_id].__len__() != gdf[kolom_vak_id].unique().__len__():
            print(BColors.OKBLUE, f"De waarden in deze kolom zijn niet uniek. Corrigeer de dubbelingen, of kies een "
                                  f"andere kolom.", BColors.ENDC)
            continue

        elif not gdf[kolom_vak_id].apply(is_numeric_integer).all():
            print(BColors.OKBLUE, f"De waarden in deze kolom zijn niet allen volledige getallen (integers). "
                                  f"Corrigeer de kolom, of kies een andere.", BColors.ENDC)
            continue

        column_name_is_valid = True

    kolom_vak_id: str
    align_vak_shp_to_dijktraject(
        app_settings, gdf_vakindeling=gdf, kolom_vak_naam=kolom_vak_naam, kolom_vak_id=kolom_vak_id)


def align_vak_shp_to_dijktraject(
        app_settings: ApplicationSettings, gdf_vakindeling: GeoDataFrame , kolom_vak_naam: str, kolom_vak_id: Optional[str] = None
):

    # Get dijktraject linestring
    ls_dijktraject = load_dijktraject_linestring(app_settings=app_settings)

    # Data verzamelen uit provided vak shp
    rows = []
    for index, row in gdf_vakindeling.iterrows():
        pnt1 = row.geometry.boundary.geoms[0]
        pnt2 = row.geometry.boundary.geoms[1]
        m_pnt1 = round(ls_dijktraject.project(pnt1), 1)
        m_pnt2 = round(ls_dijktraject.project(pnt2), 1)
        m_start = min(m_pnt1, m_pnt2)
        new_row = {"naam": row[kolom_vak_naam], "m_start": m_start}
        if kolom_vak_id:
            new_row['id'] = int(row[kolom_vak_id])
        rows.append(new_row)
    df = DataFrame(rows)
    df = df.sort_values(by=["m_start"], ignore_index=True)
    df['m_end'] = df['m_start'].shift(periods=-1)

    # Add zero and final dijktraject length to first and last vak
    df.loc[0, 'm_start'] = 0
    df.loc[max(df.index), 'm_end'] = ls_dijktraject.length

    # Align vak geometry to dijktraject by retrieving substring
    rows = []
    for index, row in df.iterrows():
        new_row = {
            "naam": row["naam"],
            "m_start": row["m_start"],
            "m_end": row["m_end"],
            "geometry": substring(ls_dijktraject, row["m_start"], row["m_end"])
        }
        if kolom_vak_id:
            new_row["id"] = row['id']
        rows.append(new_row)
    gdf_new_vakindeling = GeoDataFrame(rows, crs='EPSG:28992')
    if not kolom_vak_id:
        gdf_new_vakindeling['id'] = gdf_new_vakindeling.index + 1
    gdf_new_vakindeling: GeoDataFrame = gdf_new_vakindeling[["id", "naam", "m_start", "m_end", "geometry"]]

    # Add to geopackage
    gdf_new_vakindeling.to_file(Path(app_settings.geopackage_filepath), layer="vakindeling", driver="GPKG")
    print(BColors.OKBLUE, f"✅  Vakindeling toegevoegd.", BColors.ENDC)
