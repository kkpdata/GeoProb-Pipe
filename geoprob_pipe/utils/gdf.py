from geopandas import GeoDataFrame
from shapely import LineString, MultiLineString
from typing import List, Tuple
from shapely import unary_union, line_merge


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


def validate_vakindeling_merges_to_single_linestring(gdf: GeoDataFrame) -> Tuple[bool, type]:
    """ Controleert of alle LineStrings aaneengesloten zijn. """
    merged = line_merge(unary_union(gdf.geometry))
    return isinstance(merged, LineString), type(merged)


def validate_unique_point_locations(
        gdf: GeoDataFrame, id_column: str | None = None, return_coords: bool = False) -> Tuple[bool, str]:
    """ Validates if the given GeoDataFrame has only unique point-locations. If not, it returns a failure message
    with in there the non-unique ids.

    :param gdf:
    :param id_column: Specifies which column identifies each point. If None, index will be used as identifiers.
    :param return_coords: If True, the failure message will also include the RD-coordinates of the points.
    :return:
    """

    filter_duplicate_geometries = gdf.geometry.duplicated(keep=False)
    gdf_duplicates = gdf[filter_duplicate_geometries]

    if gdf_duplicates.__len__() == 0:
        return True, ""

    # Collect ids
    ids_of_non_unique_pnts = gdf_duplicates.index.tolist()
    if id_column is not None:
        ids_of_non_unique_pnts = gdf_duplicates[id_column].values.tolist()
    failure_msg = f"Identifiers {ids_of_non_unique_pnts} have non-unique geometries."

    # Collect coordinates
    if return_coords:
        coords = [f"{pnt.x}, {pnt.y}" for pnt in gdf_duplicates.geometry.values.tolist()]
        id_coord_list = [f"{identifier} ({pnt})" for identifier, pnt in zip(ids_of_non_unique_pnts, coords)]
        failure_msg = f"Identifiers {id_coord_list} have non-unique geometries."

    return False, failure_msg
