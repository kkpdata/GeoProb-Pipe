import geopandas as gpd
from pathlib import Path

from app.helper_functions.geodatabase_functions import process_geodatabase
class Subsoil:
    
    def __init__(self, path_gdb: Path):
        process_geodatabase(path_gdb, layer_name="SUBSOIL", geom_type="polygon")
        
#         self.deklaag = SoilLayer(gdf_subsoil.iloc[0,:])
#         self.watervoerende_laag = SoilLayer(gdf_subsoil.iloc[1,:])
        
# class SoilLayer:
    
#     def __init__(self, gdf_soil_layer: gpd.GeoDataFrame):
#         self.kv = gdf_soil_layer....