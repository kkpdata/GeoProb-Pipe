from __future__ import annotations
from InquirerPy import inquirer
from typing import TYPE_CHECKING, Optional
import os
import sys
from shapely import Point
from geopandas import GeoDataFrame, read_file
import fiona
from geoprob_pipe.utils.validation_messages import BColors
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings


def added_uittredepunten(app_settings: ApplicationSettings) -> bool:
    layers = fiona.listlayers(app_settings.geopackage_filepath)

    if "uittredepunten" not in layers:
        define_method_of_adding_uittredepunten(app_settings)
        return True

    gdf: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="uittredepunten")
    if gdf.__len__() == 0:
        define_method_of_adding_uittredepunten(app_settings)
        return True

    print(BColors.OKBLUE, f"✔  Uittredepunten al toegevoegd ({gdf.__len__()} in totaal).", BColors.ENDC)
    add_maaiveld_niveau_exit_points()
    return True


def define_method_of_adding_uittredepunten(app_settings: ApplicationSettings):
    choices_list = ["Nu klikken in ArcGIS/QGIS", "Importeren uit GIS-bestand", "Automatische suggestie"]
    choice = inquirer.select(
        message="Er zijn nog geen uittredepunten toegevoegd. Hoe wil je deze toevoegen?",
        choices=choices_list,
        default=choices_list[0],
    ).execute()

    if choice == choices_list[0]:
        create_empty_uittredepunten_layer()
    elif choice == choices_list[1]:
        import_uittredepunten_gis_file(app_settings)
    elif choice == choices_list[2]:
        generate_uittredepunten_suggestions()
    else:
        raise ValueError


def add_maaiveld_niveau_exit_points():
    # sys.exit("Applicatie vroegtijdig afgesloten: Functie 'add_maaiveld_niveau_exit_points' nog niet afgerond.")
    # TODO
    return


def create_empty_uittredepunten_layer():
    raise NotImplementedError("Applicatie vroegtijdig afgesloten: Deze keuze is nog niet geïmplementeerd.")


def import_uittredepunten_gis_file(app_settings: ApplicationSettings):
    request_uittredepunten_filepath(app_settings=app_settings)


def import_from_geodatabase(filepath: str) -> GeoDataFrame:
    layer_name: Optional[str] = None
    layer_name_is_valid = False
    while layer_name_is_valid is False:
        layer_name: str = inquirer.text(
            message="Specificeer de layer waarin met de uittredepunten. Type 'listlayers' om "
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


def import_from_geopackage(filepath: str) -> GeoDataFrame:
    layer_name: Optional[str] = None
    layer_name_is_valid = False
    while layer_name_is_valid is False:
        layer_name: str = inquirer.text(
            message="Specificeer de layer waarin met de uittredepunten. Type 'listlayers' om "
                    "een overzicht te krijgen van de geopackage-layers. ",
        ).execute()

        layer_names = fiona.listlayers(filepath)
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


LEGAL_MODEL_OPTIONS =["Walking Circles", "Walking Circles, tilted"]


def generate_uittredepunten_suggestions():
    choices = inquirer.checkbox(
        message="Welk algoritme wil je gebruiken? Meerdere opties mogelijk.\n"
                "Press <space> to select, Enter when finished. ",
        choices=LEGAL_MODEL_OPTIONS,
    ).execute()
    print(f"{choices=}")

    raise NotImplementedError("Applicatie vroegtijdig afgesloten: Dit is nog niet geïmplementeerd.")


def request_uittredepunten_filepath(app_settings: ApplicationSettings):

    # Request filepath
    filepath: Optional[str] = None
    filepath_is_valid = False
    while filepath_is_valid is False:
        filepath: str = inquirer.text(
            message="Specificeer het volledige bestandspad naar de geopackage/shapefile/geodatabase waarin de "
                    "uittredepunten zitten.",
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
        gdf: GeoDataFrame = read_file(filepath)
    elif filepath.endswith(".gpkg"):
        gdf: GeoDataFrame = import_from_geopackage(filepath=filepath)
    elif filepath.endswith(".gdb"):
        gdf: GeoDataFrame = import_from_geodatabase(filepath=filepath)
    else:
        raise NotImplementedError(
            f"Applicatie vroegtijdig afgesloten: Een {filepath.split(sep='.')[-1]}-bestand is nog niet "
            f"geïmplementeerd.")

    # Confirm all are points
    all_geometries_are_points = gdf.geometry.apply(lambda geom: isinstance(geom, Point)).all()
    if not all_geometries_are_points:
        print(BColors.WARNING, f"Het geïmporteerde bestand bestaat niet (volledig) uit punten, maar ook uit "
                               f"andere typen geometrie. Enkel punten zijn toegestaan.", BColors.ENDC)
        request_uittredepunten_filepath(app_settings=app_settings)

    # Continue questionnaire
    specify_column_with_maaiveld_niveau(app_settings, gdf=gdf)


def specify_column_with_maaiveld_niveau(app_settings: ApplicationSettings, gdf: GeoDataFrame):
    column_name: Optional[str] = None
    column_name_is_valid = False
    while column_name_is_valid is False:
        column_name: str = inquirer.text(
            message="Specificeer de kolom waarin het maaiveld niveau staat. Type 'listcolumns' om "
                    "een overzicht te krijgen van de kolommen. Type 'n.a.' als het maaiveld niveau niet gekoppeld is "
                    "aan de punten, dan zal de applicatie in een volgende stap deze voor je downloaden.",
        ).execute()

        column_names = gdf.columns
        columns_str = ", ".join(column_names)
        if column_name == "listcolumns":
            print(BColors.OKBLUE,
                  f"De volgende kolommen zijn beschikbaar in de spatial layer: {columns_str}", BColors.ENDC)
            continue
        elif column_name == "n.a.":
            gdf_to_add = gdf[["geometry"]]
            gdf_to_add["mv_exit"] = -999.9
            gdf_to_add.to_file(app_settings.geopackage_filepath, layer="uittredepunten", driver="GPKG")
            print(BColors.OKBLUE, f"✅  Uittredepunten toegevoegd.", BColors.ENDC)
            return
        elif column_name not in column_names:
            print(BColors.OKBLUE, f"De kolom naam '{column_name}' bestaat niet. De volgende kolommen zijn beschikbaar "
                                  f"in de spatial layer: {columns_str}", BColors.ENDC)
            continue
        column_name_is_valid = True

    gdf_to_add = gdf[["geometry", column_name]]
    gdf_to_add = gdf_to_add.rename(columns={column_name: "mv_exit"})
    gdf_to_add.to_file(app_settings.geopackage_filepath, layer="uittredepunten", driver="GPKG")
    print(BColors.OKBLUE, f"✅  Uittredepunten toegevoegd.", BColors.ENDC)
