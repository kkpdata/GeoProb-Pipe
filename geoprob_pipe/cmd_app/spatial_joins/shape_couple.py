from __future__ import annotations

import datetime
import sqlite3
from typing import TYPE_CHECKING

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Polygon

from geoprob_pipe.cmd_app.spatial_layers import LIST_PARAMS

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


class ShapeCouple:
    def __init__(self, app_settings: ApplicationSettings, param: str) -> None:
        """
        Class om de uittredepunten te koppelen aan een gis-laag vanuit de geopackage.
        De gekoppelde waarden worden weggeschreven in de tabel 'gis_join_invoer_parameters'.

        :param app_settings: `ApplicationSettings` object.
        :param param: Parameter die gekoppeled moet worden.
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
        Voeg een laag toe via koppeling, met de uitredepunten als er geen
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
        if (gdf.geom_types == (LineString or MultiLineString)).all():
            if "line" in LIST_PARAMS[self.param]["shape"]:
                self._join_to_line(gdf, scenario)
            else:
                raise KeyError(
                    "Deze parameter is niet geschikt om aan een lijn gekoppeld te worden."
                )
        elif (gdf.geom_types == (Polygon or MultiPolygon)).all():
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
        # TODO filter mogelijk dubble waarden
        join_df = self.gdf_exit_points.sjoin_nearest(gdf, how="left")
        df_to_add = self._create_df(join_df, scenario)

        self._upsert_to_gpkg(df_to_add)

    def _join_to_polygon(self, gdf: gpd.GeoDataFrame, scenario: str):
        """
        Maak een spatial join van de uittredepunten met een polygon.

        :param gdf: GeoDataFrame met de ruimtelijke invoer.
        :param scenario: Ondergrondscenario_naam voor in de dataframe. Kan "" zijn.
        """
        join_df = self.gdf_exit_points.sjoin(gdf, how="left")
        df_to_add = self._create_df(join_df, scenario)

        self._upsert_to_gpkg(df_to_add)

    # TODO add option for rasters
    def _join_to_raster(self):
        pass

    def _create_df(self, join_df: pd.DataFrame, scenario: str) -> pd.DataFrame:
        """
        Maak de dataframe die moet worden toegevoedg aan de geopackage.

        :param join_df: DataFrame met de data uit de join.
        :param scenario: Ondergrondscenario_naam voor in de dataframe. Kan "" zijn.
        :return: Dataframe met juiste kolommen.
        """
        df = join_df[["uittredepunt_id"]].copy()
        df = df.rename(columns={"uittredepunt_id": "scope_referentie"})
        df["parameter"] = self.param
        df["scope"] = "uittredepunt"
        df["ondergrondscenario_naam"] = scenario
        df["distribution_type"] = join_df.get(f"{self.param}_dist", "")
        df["mean"] = join_df.get(f"{self.param}_mean", "")
        df["variation"] = join_df.get(f"{self.param}_var", "")
        df["deviation"] = join_df.get(f"{self.param}_dev", "")
        df["minimum"] = join_df.get(f"{self.param}_min", "")
        df["maximum"] = join_df.get(f"{self.param}_max", "")
        df["fragility_values_ref"] = ""
        df["bronnen"] = ""
        df["opmerking"] = ""

        # Sort columns
        df = df[
            [
                "parameter",
                "scope",
                "scope_referentie",
                "ondergrondscenario_naam",
                "distribution_type",
                "mean",
                "variation",
                "deviation",
                "minimum",
                "maximum",
                "fragility_values_ref",
                "bronnen",
                "opmerking",
            ]
        ]
        return df

    def _upsert_to_gpkg(self, df: pd.DataFrame):
        """
        Voeg de dataframe toe aan de tabel. Als de tabel nog niet bestaat
        wordt deze op de correcte manier opgezet. Met een unique verzameling
        waarden of te kunnen overschrijven. Om te zorgen dat de tabel geschikt
        is voor een upsert moet er een set van kolommen uniek zijn. Dit is
        lastiger om automatisch te doen met `.to_sql`. Hier wordt de tabel
        ook handmatig toegevoegd aan gpkg_contents.

        :param df: DataFrame met juiste kolommen.
        """
        conn = sqlite3.connect(self.app_settings.geopackage_filepath)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS gis_join_parameter_invoer (
                parameter TEXT,
                scope TEXT,
                scope_referentie INTEGER,
                ondergrondscenario_naam TEXT,
                distribution_type TEXT,
                mean REAL,
                variation REAL,
                deviation REAL,
                minimum REAL,
                maximum REAL,
                fragility_values_ref TEXT,
                bronnen TEXT,
                opmerking TEXT,
                UNIQUE(parameter, scope, scope_referentie, ondergrondscenario_naam)
            )
            """
        )
        data = [tuple(row) for row in df.to_numpy()]
        placeholders = ", ".join(["?"] * len(data))
        # UPSERT naar tabel
        cursor.executemany(
            f"""
            INSERT INTO gis_join_parameter_invoer (
                parameter,
                scope,
                scope_referentie,
                ondergrondscenario_naam,
                distribution_type,
                mean,
                variation,
                deviation,
                minimum,
                maximum,
                fragility_values_ref,
                bronnen,
                opmerking,
            )
            VALUES ({placeholders})
            ON CONFLICT (
                parameter, scope, scope_referentie, ondergrondscenario_naam
                ) DO UPDATE SET
                distribution_type = excluded.distribution_type,
                mean = excluded.mean,
                variation = excluded.variation,
                deviation = excluded.deviation,
                minimum = excluded.minimum,
                maximum = excluded.maximum,
                fragility_values_ref = excluded.fragility_values_ref,
                bronnen = excluded.bronnen,
                opmerking = excluded.opmerking
            """,
            data,
        )
        # UPSERT naar gpkg_contents
        content = (
            "gis_join_parameter_invoer",
            "attributes",
            "gis_join_parameter_invoer",
            "",
            datetime.datetime.now(),
            0,
        )
        cursor.execute(
            """
            INSERT INTO gpkg_contents (
                table_name,
                data_type,
                identifier,
                description,
                last_change,
                srs_id
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (indentifier) DO UPDATE SET
                table_name = excluded.table_name,
                data_type = excluded.data_type,
                description = excluded.description,
                last_change = excluded.last_change,
                srs_id = excluded.srs_id
            """,
            content
        )

        conn.commit()
        conn.close()
