from __future__ import annotations
from geoprob_pipe.cmd_app.spatial_layers.ahn import added_ahn, request_ahn
from typing import TYPE_CHECKING, Optional, Tuple, List
from geoprob_pipe.cmd_app.utils.spatial import load_dijktraject_linestring, load_hydra_nl_as_multipoint
from shapely import LineString, MultiPoint, Polygon, MultiPolygon, Point, unary_union
from shapely.geometry import mapping
import numpy as np
import rasterio.mask
import time
import random
from geopandas import GeoDataFrame
from copy import deepcopy
from geoprob_pipe.utils.validation_messages import BColors
from InquirerPy import inquirer

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def request_buffer_distance() -> int:
    int_distance = 50
    distance_is_valid = False
    while distance_is_valid is False:
        str_distance: str = inquirer.text(
            message="Specificeer de afstand (in meters) waarbinnen gezocht moet worden aan binnendijkse zijde.\n"
                    "Zorg er voor dat deze afstand volledig binnen het toegevoegde raster valt. ",
        ).execute()

        # Validate
        try: int_distance = int(str_distance)
        except ValueError:
            print(f"{BColors.WARNING}Het lukte niet om de invoer om te zetten naar een integer (geheel getal). Weet je "
                  f"zeker dat de invoer correct is? Probeer het opnieuw.{BColors.ENDC}")
            continue
        if int_distance < 50:
            print(f"{BColors.WARNING}De opgegeven afstand moet ten minste 50 meter zijn. "
                  f"Vul opnieuw een waarde in. {BColors.ENDC}")
            continue

        # Valid
        distance_is_valid = True
    return int_distance


def create_buffer_binnendijks(
    app_settings: ApplicationSettings,
) -> Polygon:

    buffer_distance = request_buffer_distance()

    # Load data from geopackage
    ls_dijktraject: LineString = load_dijktraject_linestring(app_settings=app_settings)
    mp_hydra_nl_locaties: MultiPoint = load_hydra_nl_as_multipoint(app_settings=app_settings)

    # Create helper buffers
    buffer_both_sides = ls_dijktraject.buffer(distance=buffer_distance, cap_style='flat')
    buffer_single_side = ls_dijktraject.buffer(distance=buffer_distance, single_sided=True)
    buffer_other_side = buffer_both_sides.difference(buffer_single_side)

    # Determine which side is binnendijks
    buffer_binnendijks = buffer_single_side
    if mp_hydra_nl_locaties.intersects(buffer_binnendijks):
        buffer_binnendijks = buffer_other_side

    return buffer_binnendijks


def random_point_in_polygon(polygon):
    if isinstance(polygon, MultiPolygon):
        polygon = max(polygon.geoms, key=lambda poly: poly.area)

    minx, miny, maxx, maxy = polygon.bounds
    while True:
        p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if polygon.contains(p):
            return p


def walk(walk_id: int, src, radius: float, pnt_walk_start: Point) -> Tuple[List, List, List, List]:
    iteration_id = 0
    distance = 999
    new_rows_circle_mid = []
    new_rows_circle = []
    new_rows_circle_lowest = []
    pnt_lowest: Optional[Point] = None
    while distance > 0.5 and iteration_id <= 99:
        iteration_id += 1

        pnt_center = pnt_lowest
        if pnt_center is None:
            pnt_center = pnt_walk_start
        circle = pnt_center.buffer(distance=radius)
        circle_geojson = [mapping(circle)]

        out_image, out_transform = rasterio.mask.mask(src, circle_geojson, crop=True)
        out_image = out_image[0]  # take first band
        out_image = np.where(out_image == src.nodata, np.nan, out_image)

        if np.all(np.isnan(out_image)):
            return [], [], [], [circle]

        min_val = np.nanmin(out_image)
        min_idx = np.nanargmin(out_image)
        row, col = np.unravel_index(min_idx, out_image.shape)
        rdx, rdy = rasterio.transform.xy(out_transform, int(row), col)
        pnt_lowest = Point(rdx, rdy)
        distance = pnt_center.distance(pnt_lowest)

        new_rows_circle_mid.append({"walk_id": walk_id, "iteration_id": iteration_id, "geometry": pnt_center})
        new_rows_circle.append({"walk_id": walk_id, "iteration_id": iteration_id, "geometry": circle})
        final_iteration = False
        if distance <= 1:
            final_iteration = True
        new_rows_circle_lowest.append(
            {"walk_id": walk_id, "iteration_id": iteration_id, "min_val": round(min_val, 2),
             "geometry": pnt_lowest, "final_iteration": final_iteration})

    circles_searched = [item['geometry'] for item in new_rows_circle]

    return new_rows_circle_mid, new_rows_circle, new_rows_circle_lowest, circles_searched


def search_lowes(app_settings: ApplicationSettings, buffer_binnendijks: Polygon, radius: float = 15.0):
    to_search_buffer = deepcopy(buffer_binnendijks)  #
    with rasterio.open(app_settings.ahn_filepath) as src:
        rows_circle_mid = []
        rows_circle = []
        rows_circle_lowest = []

        start_time = time.time()
        elapsed_time = 0.0
        interval_time = 2.0  # seconds
        next_report_time = elapsed_time + interval_time

        walk_id = 0
        while to_search_buffer.area / buffer_binnendijks.area > 0.05 and walk_id <= 9999:

            walk_id += 1

            # Get random point of largest polygon of multipolygon
            pnt_walk_start = random_point_in_polygon(to_search_buffer)

            # Walk
            new_rows_circle_mid, new_rows_circle, new_rows_circle_lowest, new_circles_searched = walk(
                walk_id=walk_id, src=src, pnt_walk_start=pnt_walk_start, radius=radius)

            # Subtract from buffer
            to_search_buffer = to_search_buffer.difference(unary_union(new_circles_searched))

            rows_circle_mid.extend(new_rows_circle_mid)
            rows_circle.extend(new_rows_circle)
            rows_circle_lowest.extend(new_rows_circle_lowest)

            end_time = time.time()
            elapsed_time = end_time - start_time
            if elapsed_time > next_report_time:
                next_report_time = next_report_time + interval_time
                progress_in_percentage = 100 - round((to_search_buffer.area / buffer_binnendijks.area)*100, 0)
                print(f"Elapsed time walking: {elapsed_time:.2f} seconds. "
                      f"Current walk number: {walk_id}. "
                      f"Searched buffer for {progress_in_percentage}% of buffer")

    progress_in_percentage = 100 - round((to_search_buffer.area / buffer_binnendijks.area) * 100, 0)
    print(f"Completed walking buffer in {elapsed_time:.2f} seconds. "
          f"Total of {walk_id} walks. "
          f"Covered {progress_in_percentage}% of buffer. "
          f"Remainder is considered irrelevant.")

    gdf_circle_lowests = GeoDataFrame(rows_circle_lowest, crs='EPSG:28992')
    gdf_proposed_uittredepunten: GeoDataFrame = gdf_circle_lowests[gdf_circle_lowests['final_iteration'] == True]

    # Filter duplicates
    indices_to_keep = []
    for row in gdf_proposed_uittredepunten.itertuples():
        # noinspection PyUnresolvedReferences
        pnt = row.geometry.buffer(1)
        indices = gdf_proposed_uittredepunten[gdf_proposed_uittredepunten.geometry.intersects(pnt)].index.values
        indices.sort()
        indices_to_keep.append(indices[0])
    gdf_proposed_uittredepunten = gdf_proposed_uittredepunten[gdf_proposed_uittredepunten.index.isin(indices_to_keep)]

    gdf_proposed_uittredepunten: GeoDataFrame = gdf_proposed_uittredepunten[["walk_id", "min_val", "geometry"]]
    print(f"Found {gdf_proposed_uittredepunten.__len__()} proposed exit points.")

    return gdf_proposed_uittredepunten


def algorithm_walking_circles(app_settings: ApplicationSettings):

    if not added_ahn(app_settings=app_settings, display_added_msg=False):
        request_ahn(app_settings=app_settings)

    buffer_binnendijks = create_buffer_binnendijks(app_settings=app_settings)
    gdf_proposed_uittredepunten = search_lowes(app_settings=app_settings, buffer_binnendijks=buffer_binnendijks)

    gdf_to_add = gdf_proposed_uittredepunten[["geometry", "min_val"]]
    gdf_to_add = gdf_to_add.rename(columns={"min_val": "mv_exit"})
    gdf_to_add.to_file(app_settings.geopackage_filepath, layer="uittredepunten", driver="GPKG")
    print(BColors.OKBLUE, f"✅  Uittredepunten toegevoegd.", BColors.ENDC)
