from __future__ import annotations
from pandas import DataFrame
from geopandas import GeoDataFrame, points_from_xy
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def collect_gdf_beta_per_scenario(geoprob_pipe: GeoProbPipe) -> GeoDataFrame:

    def create_row(calc):
        return {
            "uittredepunt_id": calc.metadata["uittredepunt_id"],
            "ondergrondscenario_id": calc.metadata["ondergrondscenario_id"],
            "ondergrondscenario": calc.metadata["ondergrondscenario"],
            "vak_id": calc.metadata["vak_id"],
            "system_calculation": calc,
            "converged": calc.system_design_point.is_converged,
            "beta": round(calc.system_design_point.reliability_index, 2),
            "failure_probability": calc.system_design_point.probability_failure,
            "model_betas": ", ".join([
                str(round(dp.reliability_index, 2)) for dp in calc.model_design_points
            ])
        }

    # Construct df
    df = DataFrame([
        create_row(calc)
        for calc in geoprob_pipe.calculations]
    ).sort_values(by=["uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(drop=True)

    # Attach geometry
    df_uittredepunten = geoprob_pipe.input_data.uittredepunten.df
    df_coords = df_uittredepunten[["uittredepunt_id", "uittredepunt_x_coord", "uittredepunt_y_coord"]]
    df = df.merge(df_coords, left_on="uittredepunt_id", right_on="uittredepunt_id")
    gdf = GeoDataFrame(
        df, geometry=points_from_xy(df['uittredepunt_x_coord'], df['uittredepunt_y_coord']), crs='EPSG:28992')
    return gdf.drop(columns=['uittredepunt_x_coord', 'uittredepunt_y_coord'])
