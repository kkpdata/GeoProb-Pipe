from __future__ import annotations
from geopandas import read_file
from InquirerPy import inquirer
import warnings
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
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings


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
    else:
        raise NotImplementedError
    dijktraject_length = round(ls_dijktraject.length, 2)

    gdf_vakindeling: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="vakindeling")
    vakindeling_geometries = gdf_vakindeling.geometry.tolist()
    vakindeling_total_length = round(sum([geom.length for geom in vakindeling_geometries]), 2)

    assert dijktraject_length == vakindeling_total_length
    print(BColors.OKBLUE, f"✔  Vakindeling al toegevoegd.", BColors.ENDC)
    # TODO: Next step


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
        specify_column_with_vaknaam(app_settings, gdf=gdf)
    else:
        raise NotImplementedError(f"File with extension {filepath.split(sep='.')[-1]} is not yet supported. "
                                  f"Please make a request.")


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
    align_vak_shp_to_dijktraject(app_settings, gdf_vakindeling=gdf, kolom_vaknaam=column_name)


def align_vak_shp_to_dijktraject(
        app_settings: ApplicationSettings, gdf_vakindeling: GeoDataFrame , kolom_vaknaam: str
):

    # Get dijktraject linestring
    gdf_dijktraject: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="dijktraject")
    gdf_dijktraject_geom = gdf_dijktraject.iloc[0].geometry
    if isinstance(gdf_dijktraject_geom, MultiLineString):
        assert gdf_dijktraject_geom.geoms.__len__() == 1
        ls_dijktraject: LineString = gdf_dijktraject_geom.geoms[0]
    else:
        raise NotImplementedError

    # Data verzamelen uit provided vak shp
    rows = []
    for index, row in gdf_vakindeling.iterrows():
        pnt1 = row.geometry.boundary.geoms[0]
        pnt2 = row.geometry.boundary.geoms[1]
        m_pnt1 = round(ls_dijktraject.project(pnt1), 1)
        m_pnt2 = round(ls_dijktraject.project(pnt2), 1)
        m_start = min(m_pnt1, m_pnt2)
        new_row = {"naam": row[kolom_vaknaam], "m_start": m_start,}
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
        rows.append(new_row)
    gdf_new_vakindeling = GeoDataFrame(rows, crs='EPSG:28992')
    gdf_new_vakindeling['id'] = gdf_new_vakindeling.index
    gdf_new_vakindeling: GeoDataFrame = gdf_new_vakindeling[["id", "naam", "m_start", "m_end", "geometry"]]

    # Add to geopackage
    gdf_new_vakindeling.to_file(Path(app_settings.geopackage_filepath), layer="vakindeling", driver="GPKG")
    print(BColors.OKBLUE, f"✅  Vakindeling toegevoegd.", BColors.ENDC)
