from geopandas import GeoDataFrame
from shapely import LineString, MultiLineString


def convert_mls_geom_column_to_ls(gdf: GeoDataFrame) -> GeoDataFrame:
    """ Converts all MultiLineString geometries with a single line that single LineString. To simplify it. """

    def unwrap_ls_in_mls(geom):
        """ Unwrap a single LineString in a MultiLineString, if it is indeed a single line. """

        if isinstance(geom, LineString):
            return geom

        if isinstance(geom, MultiLineString):
            mls: MultiLineString = geom
            if mls.geoms.__len__() > 1:
                return mls
            elif mls.geoms.__len__() == 0:
                return mls.geoms[0]

        raise NotImplementedError(
            f"This function was built to handle LineStrings or MultiLineStrings. Given geometry "
            f"is of type '{type(geom)}'. Please contact the developer.")

    gdf["geometry"] = gdf["geometry"].apply(unwrap_ls_in_mls)
    return gdf
