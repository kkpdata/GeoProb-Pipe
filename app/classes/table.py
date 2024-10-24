from pathlib import Path

import geopandas as gpd

from app.helper_functions.geodatabase_functions import process_geodatabase


class Table:

    ATTRIBUTE_COLUMN_NAME_PARAMETERS = "PARAMETER"  # Attribute column name containing parameter names
    ATTRIBUTE_COLUMN_NAME_VALUES = "VALUE"  # Attribute column name containing parameter values

    def __init__(self, path_gdb: Path, layer_name: str) -> None:

        LAYER_NAME = layer_name  # Feature class name within .gdb

        self.gdf = process_geodatabase(path_gdb, layer_name=LAYER_NAME, geom_type="table")

        # Check if feature class contains all necessary columns
        for column_name in [Table.ATTRIBUTE_COLUMN_NAME_PARAMETERS, Table.ATTRIBUTE_COLUMN_NAME_VALUES]:
            if not column_name in self.gdf.columns:
                raise ValueError(
                    f"Column '{column_name}' not found in feature class '{LAYER_NAME}' in '{path_gdb.name}'"
                )

        # Check for duplicate parameters
        if self.gdf["PARAMETER"].duplicated().any():
            raise ValueError(
                f"Table '{LAYER_NAME}' contains duplicated parameters:{self.gdf[self.gdf["PARAMETER"].duplicated()]}"
            )

    def get_value(self, parameter_name: str) -> float:

        if not any(self.gdf[Table.ATTRIBUTE_COLUMN_NAME_PARAMETERS].isin([parameter_name])):
            # Check if requested parameter name exists
            raise ValueError(f"Parameter {parameter_name} does not exist")

        value = self.gdf.loc[
            self.gdf[Table.ATTRIBUTE_COLUMN_NAME_PARAMETERS] == parameter_name, Table.ATTRIBUTE_COLUMN_NAME_VALUES
        ]

        if len(value) != 1:
            # Only 1 value should be found
            raise ValueError(f"Couldn't find the value of constant '{parameter_name}'")

        return float(value[0])
