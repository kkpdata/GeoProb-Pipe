from __future__ import annotations
from typing import TYPE_CHECKING
from shapely import MultiLineString, LineString
from geoprob_pipe.utils.validation_messages import BColors
from geopandas import GeoDataFrame, read_file
from pathlib import Path
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings


def coupled_uittredepunten_to_refline(app_settings: ApplicationSettings) -> bool:
    """ Controleert of de metrering al gekoppeld is aan de uittredepunten. Indien dit niet het geval is, doet deze
    functie dat automatisch. """

    # Read uittredepunten
    gdf_exit_points: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="uittredepunten")

    # Check if already added
    if "metrering" in gdf_exit_points.columns and "afstand_reflijn" in gdf_exit_points.columns:
        print(BColors.OKBLUE, f"✔  Afstand en metrering tot reflijn al gekoppeld aan uittredepunten.", BColors.ENDC)
        return True  # Assuming already added

    gdf_dijktraject: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="dijktraject")
    gdf_dijktraject_geom = gdf_dijktraject.iloc[0].geometry
    if isinstance(gdf_dijktraject_geom, MultiLineString):
        assert gdf_dijktraject_geom.geoms.__len__() == 1
        ls_dijktraject: LineString = gdf_dijktraject_geom.geoms[0]
    elif isinstance(gdf_dijktraject_geom, LineString):
        ls_dijktraject: LineString = gdf_dijktraject_geom
    else:
        raise NotImplementedError(f"Type of {type(gdf_dijktraject_geom)} is not yet implemented.")

    # Spatial analyses
    gdf_exit_points['metrering'] = gdf_exit_points.geometry.apply(
        lambda pnt: round(ls_dijktraject.project(pnt), 1))
    gdf_exit_points['afstand_reflijn'] = gdf_exit_points.geometry.apply(
        lambda pnt: round(ls_dijktraject.distance(pnt), 1))

    # Add uittredepunt id
    gdf_exit_points = gdf_exit_points.sort_values(by=["metrering"])
    gdf_exit_points['uittredepunt_id'] = range(1, len(gdf_exit_points) + 1)

    # Store back in geopackage
    gdf_exit_points.to_file(Path(app_settings.geopackage_filepath), layer="uittredepunten", driver="GPKG")
    print(BColors.OKBLUE,
          f"✅  Afstand en metrering tot reflijn zijn nu gekoppeld aan de uittredepunten.", BColors.ENDC)
    return True
