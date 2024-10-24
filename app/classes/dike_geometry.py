from pathlib import Path

import geopandas as gpd

from app.helper_functions.geodatabase_functions import process_geodatabase


class DikeGeometry:

    def __init__(self, path_gdb: Path) -> None:

        LAYER_NAME = "dike_geometry"  # Feature class name within .gdb
        ATTRIBUTE_COLUMN_NAME = "SOORT"  # Attribute column name that defines the type of line (e.g. "Buitenteenlijn")

        # TODO check: maakt het uit in welke richting de keringslijnen lopen? Zo ja: checks inbouwen
        self.gdf = process_geodatabase(path_gdb, layer_name=LAYER_NAME, geom_type="line")

        try:
            self.buitenteen = self.gdf[self.gdf[ATTRIBUTE_COLUMN_NAME] == "Buitenteenlijn"]
            self.binnenteen = self.gdf[self.gdf[ATTRIBUTE_COLUMN_NAME] == "Binnenteenlijn"]
        except KeyError:
            raise ValueError(
                f"Feature class '{LAYER_NAME}' in '{path_gdb.name}' should contain attribute column '{ATTRIBUTE_COLUMN_NAME}' which indicates the type of line (e.g. 'Buitenteenlijn' or 'Binnenteenlijn')"
            )

        if self.buitenteen.empty:
            raise ValueError(
                f"Feature class '{LAYER_NAME}' in '{path_gdb.name}' should contain at least one geometry for which attribute column {ATTRIBUTE_COLUMN_NAME}='Buitenteenlijn'"
            )

        if self.binnenteen.empty:
            raise ValueError(
                f"Feature class '{LAYER_NAME}' in '{path_gdb.name}' should contain at least one geometry for which attribute column {ATTRIBUTE_COLUMN_NAME}='Binnenteenlijn'"
            )

        self.kwelweglengte = self.calculate_kwelweglengte()

    def calculate_kwelweglengte(self): ...
