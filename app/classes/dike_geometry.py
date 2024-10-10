import geopandas as gpd


class DikeGeometry:

    def __init__(self, gdf_dike_geometry: gpd.GeoDataFrame):
        self.buitenteen = ...
        self.binnenteen = ...
        self.voorland = ...
        self.achterland = ...  # TODO: hier ook eigenschappen sloot aan toevoegen?

        self.kwelweglengte = self.calculate_kwelweglengte()

    def calculate_kwelweglengte(self): ...
