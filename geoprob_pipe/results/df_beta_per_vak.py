from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe.results import Results
    from geoprob_pipe import GeoProbPipe


def construct_df_beta_per_vak(results: Results):
    gdf = results.gdf_beta_uittredepunten
    gdf = gdf.loc[gdf.groupby('vak_id')['beta'].idxmin()]
    return gdf.drop(columns=["geometry"])
