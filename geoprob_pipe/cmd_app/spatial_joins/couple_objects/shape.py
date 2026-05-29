from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

import geopandas as gpd

from geoprob_pipe.cmd_app.spatial_layers import LIST_PARAMS
from geoprob_pipe.utils.validation_messages import BColors

from .base import BaseCouple

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


class ShapeCouple(BaseCouple):
    def __init__(self, app_settings: ApplicationSettings, param: str) -> None:
        """
        Class om de uittredepunten te koppelen aan een gis-laag vanuit de geopackage.
        De gekoppelde waarden worden weggeschreven in de tabel 'gis_join_parameter_invoer'.

        :param app_settings: `ApplicationSettings` object.
        :param param: Parameter die gekoppeld moet worden.
        """
        self.app_settings = app_settings
        self.param = param
        conn = sqlite3.connect(app_settings.geopackage_filepath)
        cursor = conn.cursor()
        # Get scenarios to add
        cursor.execute(
            "SELECT metadata_value FROM geoprob_pipe_metadata WHERE metadata_type = ?",
            ("ruimtelijke_scenarios",),
        )
        self.scenarios: list[str] = cursor.fetchone()[0].split(", ")

        # Get table names
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type=?;", ("table",)
        )
        self.tables_names: list[str] = [row[0] for row in cursor.fetchall()]
        conn.close()

    def couple_exit_points(self):
        """
        Lees de uittredepunten uit de geopackage en bepaal of er meerdere scenarios
        zijn om toe te voegen.

        :raises KeyError: Als de parameter tabel niet wordt gevonden.
        """
        # Read uittredepunten
        self.gdf_exit_points: gpd.GeoDataFrame = gpd.read_file(
            self.app_settings.geopackage_filepath, layer="uittredepunten"
        )

        self.param_tables = [
            table
            for table in self.tables_names
            if table.split("_")[0] == self.param
        ]

        if len(self.param_tables) == 0:
            raise KeyError(
                f"{self.param} niet gevonden in de tabellen van de geopackage."
            )

        elif len(self.param_tables) == 1:
            # Geen invoer per scenario
            self._add_single_layer()

        else:
            # Invoer per scenario
            self._add_multiple_layers()

    def _add_single_layer(self):
        """
        Voeg een laag toe via koppeling, met de uittredepunten als er geen
        ruimtelijke scenarios zijn voor de parameter.
        """
        gdf_parameter: gpd.GeoDataFrame = gpd.read_file(
            self.app_settings.geopackage_filepath, layer=f"{self.param}"
        )
        self._check_shape(gdf_parameter)

    def _add_multiple_layers(self):
        """
        Voeg de lagen een voor een toe als er ruimtelijke scenarios zijn voor
        de parameter.
        """
        for scenario in self.param_tables:
            gdf_parameter: gpd.GeoDataFrame = gpd.read_file(
                self.app_settings.geopackage_filepath,
                layer=f"{self.param}_{scenario}",
            )
            self._check_shape(gdf_parameter, scenario)

    def _check_shape(self, gdf: gpd.GeoDataFrame, scenario: str = ""):
        """
        Bepaal welke shapes er in de laag zitten en of deze een geaccepteerde
        optie zijn.

        :param gdf: GeoDataFrame met de ruimtelijke invoer.
        :param scenario: Ondergrondscenario_naam als invoer per scenario voor
            deze parameters is gekozen, defaults to ""
        :raises KeyError: Lijn niet geaccepteerd bij deze parameter.
        :raises KeyError: Polygon niet geaccepteerd bij deze parameter.
        :raises ImportError: De laag bestaat uit verschillende geometrie types.
        """

        if (gdf.geom_type.isin(["LineString", "MultiLineString"])).all():
            if "line" in LIST_PARAMS[self.param]["shape"]:
                self._join_to_line(gdf, scenario)
            else:
                raise KeyError(
                    "Deze parameter is niet geschikt om aan een lijn gekoppeld te worden."
                )
        elif (gdf.geom_type.isin(["Polygon", "MultiPolygon"])).all():
            if "polygon" in LIST_PARAMS[self.param]["shape"]:
                self._join_to_polygon(gdf, scenario)
            else:
                raise KeyError(
                    "Deze parameter is niet geschikt om aan een polygon gekoppeld te worden."
                )
        else:
            raise ImportError(
                "De geïmporteerde laag bestaat niet uit alleen lijnen of uit alleen polygonen."
            )

    def _join_to_line(self, gdf: gpd.GeoDataFrame, scenario: str):
        """
        Maak een spatial join van de uittredepunten met een lijn.

        :param gdf: GeoDataFrame met de ruimtelijke invoer.
        :param scenario: Ondergrondscenario_naam voor in de dataframe. Kan "" zijn.
        """
        join_gdf = self.gdf_exit_points.sjoin_nearest(gdf, how="left").drop_duplicates("uittredepunt_id")
        df_to_add = self._create_df(join_gdf, scenario)

        self._upsert_to_gpkg(df_to_add)

    def _join_to_polygon(self, gdf: gpd.GeoDataFrame, scenario: str):
        """
        Maak een spatial join van de uittredepunten met een polygon.

        :param gdf: GeoDataFrame met de ruimtelijke invoer.
        :param scenario: Ondergrondscenario_naam voor in de dataframe. Kan "" zijn.
        """
        join_gdf = self.gdf_exit_points.sjoin(gdf, how="left")
        outside = join_gdf[join_gdf.index_right.isna()]
        if len(outside) != 0:
            print(
                BColors.WARNING,
                f"{len(outside)} uittredepunten vallen buiten de polygonen bij {self.param}.",
                BColors.ENDC
            )
        join_gdf = join_gdf[join_gdf.index_right.notna()]
        df_to_add = self._create_df(join_gdf, scenario)

        self._upsert_to_gpkg(df_to_add)

    # TODO Later Should: Add option for raster import and coupling.
    def _join_to_raster(self):
        raise NotImplementedError("Toevoegen van parameters via raster is nog niet mogelijk.")
