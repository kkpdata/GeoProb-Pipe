import geopandas as gpd
from soil_layer import SoilLayer


class Subsoil:

    def __init__(self, gdf_subsoil: gpd.GeoDataFrame):
        self.deklaag = SoilLayer(gdf_subsoil.iloc[0, :])
        self.watervoerende_laag = SoilLayer(gdf_subsoil.iloc[1, :])
