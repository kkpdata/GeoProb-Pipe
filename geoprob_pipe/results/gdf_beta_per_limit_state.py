from __future__ import annotations
from pandas import DataFrame
from geopandas import GeoDataFrame, points_from_xy
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def collect_gdf_beta_per_limit_state(geoprob_pipe: GeoProbPipe) -> GeoDataFrame:

    def create_row(calc, dp, model_name):
        return {
            "uittredepunt_id": calc.metadata["uittredepunt_id"],
            "ondergrondscenario_id": calc.metadata["ondergrondscenario_id"],
            "vak_id": calc.metadata["vak_id"],
            "limit_state": model_name,
            "converged": dp.is_converged,
            "beta": round(dp.reliability_index, 2),
            "failure_probability": dp.probability_failure,
        }

    # Construct df
    rows = []
    for calculation in geoprob_pipe.calculations:
        for design_point, model in zip(calculation.model_design_points, calculation.given_system_models):
            rows.append(create_row(calc=calculation, dp=design_point, model_name=model.__name__))
    df = DataFrame(rows).sort_values(by=["uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(drop=True)

    # Attach geometry
    df_uittredepunten = geoprob_pipe.input_data.uittredepunten.df
    df_coords = df_uittredepunten[["uittredepunt_id", "uittredepunt_x_coord", "uittredepunt_y_coord"]]
    df = df.merge(df_coords, left_on="uittredepunt_id", right_on="uittredepunt_id")
    gdf = GeoDataFrame(
        df, geometry=points_from_xy(df['uittredepunt_x_coord'], df['uittredepunt_y_coord']), crs='EPSG:28992')
    return gdf.drop(columns=['uittredepunt_x_coord', 'uittredepunt_y_coord'])
