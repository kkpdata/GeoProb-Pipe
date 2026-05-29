from geopandas import GeoDataFrame
from shapely import LineString, MultiLineString
from typing import List, Tuple


def validate_geometry_types(gdf: GeoDataFrame, allowed_types=None) -> Tuple[bool, List[str]]:
    """ Controleert of alle geometrieën van een valide type zijn.

    :param gdf:
    :param allowed_types:
    :return:
        1st item: Boolean if valid
        2nd item: Invalid geometry types
    """

    # Mutable arguments
    if allowed_types is None:
        allowed_types = {"LineString", "MultiLineString"}

    # Validate
    geom_types = gdf.geometry.geom_type  # of gdf.geom_type
    mask_invalid = ~geom_types.isin(allowed_types)
    invalid_gdf = gdf.loc[mask_invalid]
    is_valid = not mask_invalid.any()

    return is_valid, list(invalid_gdf.geometry.geom_type.unique())


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
