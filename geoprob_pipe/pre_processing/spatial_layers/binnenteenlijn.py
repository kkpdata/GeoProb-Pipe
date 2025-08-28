"""
TODO Later Should Klein: Controleer of de binnenteenlijn ook echt aan de binnenzijde is.

"""

from __future__ import annotations
from InquirerPy import inquirer
from typing import TYPE_CHECKING, Optional
import os
import sys
from shapely import LineString, MultiLineString
from geopandas import GeoDataFrame, read_file
import fiona
from geoprob_pipe.utils.other import BColors
if TYPE_CHECKING:
    from geoprob_pipe.cmd import ApplicationSettings


def added_binnenteenlijn(app_settings: ApplicationSettings) -> bool:
    layers = fiona.listlayers(app_settings.geopackage_filepath)

    if "binnenteenlijn" in layers:
        print(BColors.OKBLUE, f"✔  Binnenteenlijn al toegevoegd.", BColors.ENDC)
        return True

    request_binnenteenlijn_filepath(app_settings=app_settings)
    return True


def request_binnenteenlijn_filepath(app_settings: ApplicationSettings):

    # Request filepath
    filepath: Optional[str] = None
    filepath_is_valid = False
    while filepath_is_valid is False:
        filepath: str = inquirer.text(
            message="Specificeer het volledige bestandspad naar de geopackage/shapefile/geodatabase waarin de "
                    "binnenteen lijnen zitten.",
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
        sys.exit("Applicatie vroegtijdig afgesloten: shp wordt nog niet ondersteund.")
    elif filepath.endswith(".gpkg"):
        sys.exit("Applicatie vroegtijdig afgesloten: gpkg wordt nog niet ondersteund.")
    elif filepath.endswith(".gdb"):
        gdf: GeoDataFrame = import_from_geodatabase(filepath=filepath)
    else:
        sys.exit(f"Applicatie vroegtijdig afgesloten: Een {filepath.split(sep='.')[-1]}-bestand is niet "
                 f"geïmplementeerd.")

    # Confirm all are points
    all_geometries_are_points = gdf.geometry.apply(
        lambda geom: isinstance(geom, LineString) or isinstance(geom, MultiLineString)).all()
    if not all_geometries_are_points:
        print(BColors.WARNING, f"Het geïmporteerde bestand bestaat niet (volledig) uit lijnen, maar ook uit "
                               f"andere typen geometrie. Enkel lijnen zijn toegestaan.", BColors.ENDC)
        request_binnenteenlijn_filepath(app_settings=app_settings)

    # Add binnenteenlijn
    gdf_to_add = gdf[["geometry"]]
    gdf_to_add.to_file(app_settings.geopackage_filepath, layer="binnenteenlijn", driver="GPKG")
    print(BColors.OKBLUE, f"✅  Binnenteenlijn toegevoegd.", BColors.ENDC)


def import_from_geodatabase(filepath: str) -> GeoDataFrame:
    layer_name: Optional[str] = None
    layer_name_is_valid = False
    while layer_name_is_valid is False:
        layer_name: str = inquirer.text(
            message="Specificeer de layer waarin de binnenteenlijn staat. Type 'listlayers' om "
                    "een overzicht te krijgen van de geodatabase-layers. ",
        ).execute()

        layer_names = fiona.listlayers(filepath)
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
