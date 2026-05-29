from __future__ import annotations

import datetime
import sqlite3
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


class BaseCouple:
    """
    Base class voor het koppelen van GIS-kagen aan de uittredepunten en deze op
    de correcte manier toe te voegen aan de geopackage.
    """    
    
    # Placeholders
    app_settings: ApplicationSettings
    param: str
    
    def _create_df(self, join_df: pd.DataFrame, scenario: str) -> pd.DataFrame:
        """
        Maak de dataframe die moet worden toegevoegd aan de geopackage.

        :param join_df: DataFrame met de data uit de join.
        :param scenario: Ondergrondscenario_naam voor in de dataframe. Kan "" zijn.
        :return: Dataframe met juiste kolommen.
        """
        df = join_df[["uittredepunt_id"]].copy()
        df = df.rename(columns={"uittredepunt_id": "scope_referentie"})
        df["parameter"] = self.param
        df["scope"] = "uittredepunt"
        df["ondergrondscenario_naam"] = scenario
        df["distribution_type"] = join_df.get(f"{self.param}_dist", "deterministic")
        df["mean"] = join_df.get(f"{self.param}_mean", np.nan)
        df["variation"] = join_df.get(f"{self.param}_var", np.nan)
        df["deviation"] = join_df.get(f"{self.param}_dev", np.nan)
        df["minimum"] = join_df.get(f"{self.param}_min", np.nan)
        df["maximum"] = join_df.get(f"{self.param}_max", np.nan)
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
        placeholders = ", ".join(["?"] * 13)
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
                opmerking
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
            ON CONFLICT (identifier) DO UPDATE SET
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