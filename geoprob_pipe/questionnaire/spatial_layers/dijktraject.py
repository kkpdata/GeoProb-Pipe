from __future__ import annotations
from InquirerPy import inquirer
import warnings
from typing import Optional, TYPE_CHECKING
import importlib.resources
import os
from geopandas import GeoDataFrame, read_file
import fiona
from geoprob_pipe.utils.validation_messages import BColors
if TYPE_CHECKING:
    from geoprob_pipe.questionnaire.cmd import ApplicationSettings


def added_dijktraject(app_settings: ApplicationSettings) -> bool:
    layers = fiona.listlayers(app_settings.geopackage_filepath)

    if "dijktraject" in layers:
        print(BColors.OKBLUE, f"✔  Dijktraject al toegevoegd.", BColors.ENDC)
        return True
    else:
        question_trajectory_source(app_settings)
        # TODO Later Should Middel: We vragen nu filepath, we kunnen daarnaast de optie geven voor normtrajecten direct.
        return True


def question_trajectory_source(app_settings: ApplicationSettings):
    choices_list = ["Waterveiligheidsportaal (primaire keringen)", "Lokaal GIS bestand (geopackage/shapefile/geodatabase)"]

    choice = inquirer.select(
        message="Van waaruit wil je de referentielijn van de dijk inladen?",
        choices=choices_list,
        default=choices_list[0],
    ).execute()

    if choice == choices_list[0]:
        with importlib.resources.path(
                'geoprob_pipe.misc.dijktrajecten', 'dijktrajecten.shp') as shp_path:
            gdf: GeoDataFrame = read_file(shp_path)
        specify_single_trajectory(app_settings, gdf=gdf, column_name="TRAJECT_ID")
    elif choice == choices_list[1]:
        request_trajectory_filepath(app_settings)
    return False


def request_trajectory_filepath(app_settings: ApplicationSettings):
    filepath: Optional[str] = None
    filepath_is_valid = False
    while filepath_is_valid is False:
        filepath: str = inquirer.text(
            message="Specificeer het volledige bestandspad naar de geopackage/shapefile/geodatabase waarin de "
                    "referentielijn van de dijk zit.",
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

    if filepath.endswith(".gdb"):
        specify_geodatabase_layer(app_settings, filepath)
    elif filepath.endswith(".gpkg"):
        specify_geopackage_layer(app_settings, filepath)
    elif filepath.endswith(".shp"):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Measured \\(M\\) geometry types are not supported.*")
            gdf: GeoDataFrame = read_file(filepath)
        specify_column_with_trajectory_name(app_settings, gdf=gdf)
    else:
        raise NotImplementedError(f"File with extension {filepath.split(sep='.')[-1]} is not yet supported. "
                                  f"Please make a request.")


def specify_geodatabase_layer(app_settings: ApplicationSettings, filepath: str):
    layer_name: Optional[str] = None
    layer_name_is_valid = False
    while layer_name_is_valid is False:
        layer_name: str = inquirer.text(
            message="Specificeer de layer waarin met de referentielijn van het dijktraject. Type 'listlayers' om "
                    "een overzicht te krijgen van de geodatabase-layers. ",
        ).execute()

        layer_names = fiona.listlayers(filepath)
        layer_names.sort()
        layers_str = ", ".join(layer_names)
        if layer_name == "listlayers":
            print(BColors.OKBLUE, f"De volgende layers zijn beschikbaar in de geodatabase: {layers_str}", BColors.ENDC)
            continue
        elif layer_name not in layer_names:
            print(BColors.OKBLUE, f"De layer name '{layer_name}' bestaat niet. De volgende layers zijn beschikbaar in "
                                  f"de geodatabase: {layers_str}", BColors.ENDC)
            continue
        # TODO Later Must Klein: Check dat een LineString-laag wordt opgegeven.

        layer_name_is_valid = True

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Measured \\(M\\) geometry types are not supported.*")
        gdf: GeoDataFrame = read_file(filepath, layer=layer_name)
    specify_column_with_trajectory_name(app_settings, gdf)


def specify_geopackage_layer(app_settings: ApplicationSettings, filepath: str):
    layer_name: Optional[str] = None
    layer_name_is_valid = False
    while layer_name_is_valid is False:
        layer_name: str = inquirer.text(
            message="Specificeer de layer waarin met de referentielijn van het dijktraject. Type 'listlayers' om "
                    "een overzicht te krijgen van de geopackage-layers. ",
        ).execute()

        layer_names = fiona.listlayers(filepath)
        layer_names.sort()
        layers_str = ", ".join(layer_names)
        if layer_name == "listlayers":
            print(BColors.OKBLUE, f"De volgende layers zijn beschikbaar in de geopackage: {layers_str}", BColors.ENDC)
            continue
        elif layer_name not in layer_names:
            print(BColors.OKBLUE, f"De layer name '{layer_name}' bestaat niet. De volgende layers zijn beschikbaar in "
                                  f"de geopackage: {layers_str}", BColors.ENDC)
            continue
        # TODO Later Must Klein: Check dat een LineString-laag wordt opgegeven.

        layer_name_is_valid = True

    gdf: GeoDataFrame = read_file(filepath, layer=layer_name)
    specify_column_with_trajectory_name(app_settings, gdf)


def specify_column_with_trajectory_name(app_settings: ApplicationSettings, gdf: GeoDataFrame):
    column_name: Optional[str] = None
    column_name_is_valid = False
    while column_name_is_valid is False:
        column_name: str = inquirer.text(
            message="Specificeer de kolom waarin de naam van het dijktraject staat. Type 'listcolumns' om "
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
    specify_single_trajectory(app_settings, gdf, column_name)


def specify_single_trajectory(app_settings: ApplicationSettings, gdf: GeoDataFrame, column_name: str):

    # Single item in gdf? Then we know enough
    if gdf.__len__() == 1:
        gdf = gdf[[column_name, gdf.geometry.name]]
        gdf = gdf.rename(columns={
            column_name: "traject_naam",
            gdf.geometry.name: "geometry",
        })
        gdf.to_file(app_settings.geopackage_filepath, layer="dijktraject", driver="GPKG")

        print(BColors.OKBLUE, f"✅  Trajectlijn toegevoegd.", BColors.ENDC)
        return

    # Multiple items in gdf? Make user select single one
    trajectory_name: Optional[str] = None
    trajectory_name_is_valid = False
    while trajectory_name_is_valid is False:
        trajectory_name: str = inquirer.text(
            message=f"Er zijn {gdf.__len__()} opties. Type hier welke de juiste referentielijn is. Type "
                    f"'listoptions' om een overzicht te krijgen van de opties.",
        ).execute()

        trajectory_names = gdf[column_name].values.tolist()
        trajectory_names.sort()
        trajectories_str = ", ".join(trajectory_names)
        if trajectory_name == "listoptions":
            print(BColors.OKBLUE,
                  f"De volgende opties zijn beschikbaar: {trajectories_str}", BColors.ENDC)
            continue
        elif trajectory_name not in trajectory_names:
            print(BColors.OKBLUE, f"De keuze '{trajectory_name}' bestaat niet. De volgende opties zijn beschikbaar: "
                                  f"{trajectories_str}", BColors.ENDC)
            continue

        trajectory_name_is_valid = True

    gdf = gdf[gdf[column_name] == trajectory_name]
    gdf = gdf[[column_name, gdf.geometry.name]]
    gdf = gdf.rename(columns={
        column_name: "traject_naam",
        gdf.geometry.name: "geometry",
    })
    gdf.to_file(app_settings.geopackage_filepath, layer="dijktraject", driver="GPKG")
    print(BColors.OKBLUE, f"✅  Trajectlijn toegevoegd.", BColors.ENDC)
    return
