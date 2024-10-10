import geopandas as gpd

class SoilLayer:
    
    def __init__(self, gdf_soil_layer: gpd.GeoDataFrame):
        self.kv = gdf_soil_layer....