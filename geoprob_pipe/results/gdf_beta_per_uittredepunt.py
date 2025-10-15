from __future__ import annotations
from geoprob_pipe.utils.statistics import convert_failure_probability_to_beta
from geopandas import GeoDataFrame, points_from_xy
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe.results import Results
    from geoprob_pipe import GeoProbPipe


def calculate_gdf_beta_per_uittredepunt(geoprob_pipe: GeoProbPipe, results: Results) -> GeoDataFrame:

    # Sum
    df = results.gdf_beta_scenarios.assign(
        failure_probability=results.gdf_beta_scenarios.apply(
            lambda row: row['failure_probability'] *
                        row['ondergrondscenario'].variables.ondergrondscenario_kans[
                            "value"], axis=1)).groupby('uittredepunt_id', as_index=False)[
        'failure_probability'].sum()
    df["beta"] = df["failure_probability"].apply(lambda failure_prob: convert_failure_probability_to_beta(failure_prob))

    # Add vak id back to it
    df_uittredepunten = geoprob_pipe.input_data.uittredepunten.df
    df_uittredepunten = df_uittredepunten[["uittredepunt_id", "vak_id", "uittredepunt_x_coord", "uittredepunt_y_coord"]]
    df = df.merge(df_uittredepunten, left_on="uittredepunt_id", right_on="uittredepunt_id")
    gdf = GeoDataFrame(
        df, geometry=points_from_xy(df['uittredepunt_x_coord'], df['uittredepunt_y_coord']), crs='EPSG:28992')

    return gdf[["geometry", "uittredepunt_id", "vak_id", "beta", "failure_probability"]]
