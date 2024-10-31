from pathlib import Path

import geopandas as gpd

from app.classes.table import Table
from app.helper_functions.geodatabase_functions import process_geodatabase


class Subsoil(Table):

    def __init__(self, path_gdb: Path, layer_name: str) -> None:
        super().__init__(path_gdb, layer_name)

        for soil_layer in self.gdf["soil_layer"].unique():
            

#         self.deklaag = SoilLayer(gdf_subsoil.iloc[0,:])
#         self.watervoerende_laag = SoilLayer(gdf_subsoil.iloc[1,:])

class SoilLayer:

    def __init__(self, gdf_soil_layer: gpd.GeoDataFrame):
        self.kv = gdf_soil_layer....
        self.is_aquifer = Yes/No
        self.is_deklaag = Yes/No