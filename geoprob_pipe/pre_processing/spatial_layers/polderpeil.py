from __future__ import annotations
from InquirerPy import inquirer
from typing import TYPE_CHECKING, Optional
import os
from shapely import Polygon, MultiPolygon
from geopandas import GeoDataFrame, read_file
import fiona
from geoprob_pipe.utils.validation_messages import BColors
import warnings
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings


def added_polderpeil(app_settings: ApplicationSettings) -> bool:
    layers = fiona.listlayers(app_settings.geopackage_filepath)

    if "polderpeil" in layers:
        print(BColors.OKBLUE, f"✔  Polderpeil al toegevoegd.", BColors.ENDC)
        return True

    request_polderpeil_filepath(app_settings=app_settings)
    return True


def request_polderpeil_filepath(app_settings: ApplicationSettings):

    # Request filepath
    filepath: Optional[str] = None
    filepath_is_valid = False
    while filepath_is_valid is False:
        filepath: str = inquirer.text(
            message="Specificeer het volledige bestandspad naar de geopackage/shapefile/geodatabase waarin de "
                    "polderpeilen zitten.",
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

    # Import data
    if filepath.endswith(".shp"):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Measured \\(M\\) geometry types are not supported.*")
            gdf: GeoDataFrame = read_file(filepath)
    elif filepath.endswith(".gpkg"):
        gdf: GeoDataFrame = import_from_geopackage(filepath=filepath)
    elif filepath.endswith(".gdb"):
        gdf: GeoDataFrame = import_from_geodatabase(filepath=filepath)
    else:
        raise NotImplementedError(
            f"Applicatie vroegtijdig afgesloten: Een {filepath.split(sep='.')[-1]}-bestand is niet geïmplementeerd.")

    # Confirm all are points
    all_geometries_are_points = gdf.geometry.apply(
        lambda geom: isinstance(geom, Polygon) or isinstance(geom, MultiPolygon)).all()
    if not all_geometries_are_points:
        print(BColors.WARNING, f"Het geïmporteerde bestand bestaat niet (volledig) uit vlakken/polygonen, maar ook uit "
                               f"andere typen geometrie. Enkel vlakken/polygonen zijn toegestaan.", BColors.ENDC)
        request_polderpeil_filepath(app_settings=app_settings)

    # Continue questionnaire
    specify_column_with_polderpeil_niveau(app_settings, gdf=gdf)


def import_from_geodatabase(filepath: str) -> GeoDataFrame:
    layer_name: Optional[str] = None
    layer_name_is_valid = False
    while layer_name_is_valid is False:
        layer_name: str = inquirer.text(
            message="Specificeer de layer waarin met het polderpeil. Type 'listlayers' om "
                    "een overzicht te krijgen van de geodatabase-layers. ",
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

    gdf: GeoDataFrame = read_file(filepath, layer=layer_name)
    return gdf


def import_from_geopackage(filepath: str) -> GeoDataFrame:
    layer_name: Optional[str] = None
    layer_name_is_valid = False
    while layer_name_is_valid is False:
        layer_name: str = inquirer.text(
            message="Specificeer de laag met de polderpeilen. Type 'listlayers' om "
                    "een overzicht te krijgen van de geopackage-layers. ",
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

    gdf: GeoDataFrame = read_file(filepath, layer=layer_name)
    return gdf


def specify_column_with_polderpeil_niveau(app_settings: ApplicationSettings, gdf: GeoDataFrame):
    column_name: Optional[str] = None
    column_name_is_valid = False
    while column_name_is_valid is False:
        column_name: str = inquirer.text(
            message="Specificeer de kolom waarin het polderpeil staat. Type 'listcolumns' om "
                    "een overzicht te krijgen van de kolommen.",
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

    gdf_to_add = gdf[["geometry", column_name]]
    gdf_to_add = gdf_to_add.rename(columns={column_name: "polderpeil"})
    gdf_to_add.to_file(app_settings.geopackage_filepath, layer="polderpeil", driver="GPKG")
    print(BColors.OKBLUE, f"✅  Polderpeilen toegevoegd.", BColors.ENDC)
