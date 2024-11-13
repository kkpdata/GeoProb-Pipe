import geopandas as gpd

class Constants:
    
    def __init__(self, gdf_constants: gpd.GeoDataFrame):
        self.faalkans_traject = gdf_constants....
        self.omega_faalkansbudget = gdf_constants....
        self.lengte_effect = gdf_constants...
        
        self.faalkans_stph = self.calculate_faalkans_stph()
        
    def calculate_faalkans_stph(self):
        return self.faalkans_traject * self.omega_faalkansbudget / self.lengte_effect
    

    