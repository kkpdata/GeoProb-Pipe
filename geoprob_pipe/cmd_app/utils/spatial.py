from __future__ import annotations
from geopandas import read_file
from shapely import LineString, MultiLineString, MultiPoint
from typing import TYPE_CHECKING
from geopandas import GeoDataFrame
if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def load_dijktraject_linestring(app_settings: ApplicationSettings) -> LineString:
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
    return ls_dijktraject


def load_hydra_nl_as_multipoint(app_settings: ApplicationSettings) -> MultiPoint:
    gdf_hrd_locaties: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="hrd_locaties")
    return MultiPoint(gdf_hrd_locaties.geometry.values)
