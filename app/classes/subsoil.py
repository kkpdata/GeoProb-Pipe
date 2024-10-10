import geopandas as gpd


class Subsoil:
    
    def __init__(self, gdf_subsoil: gpd.GeoDataFrame):
        self.deklaag = SoilLayer(gdf_subsoil.iloc[0,:])
        self.watervoerende_laag = SoilLayer(gdf_subsoil.iloc[1,:])
        
class SoilLayer:
    
    def __init__(self, gdf_soil_layer: gpd.GeoDataFrame):
        self.kv = gdf_soil_layer....