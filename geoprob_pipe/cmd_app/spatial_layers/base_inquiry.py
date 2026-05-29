"""
Class voor het opvragen van de ruimtelijke invoer voor de parameters
vanuit GIS lagen. Shapefiles, geodatabases en geopackages worden ondersteund.

Er zijn vier mogelijke invoer situaties:
-GEEN ruimtelijke scenarios en GEEN ruimtelijke data invoer
-GEEN ruimtelijke scenarios en WEL ruimtelijke data invoer
-WEL ruimtelijke scenarios en GEEN ruimtelijke data invoer
-WEL ruimtelijke scenarios en WEL ruimtelijke data invoer

Daarnaast is er nog onderscheid in invoer met verschillende shapes per scenario
of twee sets met invoer data.
"""

from __future__ import annotations

import os
import sqlite3
import warnings
from typing import TYPE_CHECKING

import fiona
import geopandas as gpd
import InquirerPy.prompts.input as prompt
import numpy as np
from shapely import LineString, MultiLineString

from geoprob_pipe.utils.validation_messages import BColors

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


class BaseInquiry:
    def __init__(
        self,
        app_settings: ApplicationSettings,
        param: str,
        specific_shape: str = "",
        include_value: bool = False,
        single_geometry: bool = False,
    ) -> None:
        """
        Class voor de opvraag van de ruimtelijke invoer van de parameters.

        :param app_settings: `ApplicationSettings` object.
        :param param: Parameter die wordt opgevraagd. Deze wordt ook gebruikt
            voor de naam van de tabel in de geopackage.
        :param specific_shape: Welke soort ruimtelijke invoer acceptabel is, defaults to "".
            Geldige invoer is "lines", "polygons" of "rasters".
        :param include_value: Of er naast de geometrie zelf ook een bepaalde
            waarde moet worden toegevoegd aan de geopackage, defaults to False
        """
        self.app_settings = app_settings
        self.param = param
        self.specific_shape = specific_shape
        self.include_value = include_value
        self.single_geometry = single_geometry
        conn = sqlite3.connect(app_settings.geopackage_filepath)
        cur = conn.cursor()
        cur.execute(
            "SELECT metadata_value FROM geoprob_pipe_metadata WHERE metadata_type = ?",
            ("ruimtelijke_scenarios",),
        )
        self.scenarios: list[str] = cur.fetchone()[0].split(", ")
        conn.close()

    def request_filepath(self):
        """
        Method voor het opvragen van het filepath.
        """
        skip_batch = False  # Als batch input faalt ga over op handmatig
        while True:
            if self.app_settings.batch_input and not skip_batch:
                filepath = self.app_settings.input_config.get(
                    f"{self.param}", "filepath"
                )
            else:
                filepath: str = prompt.InputPrompt(
                    message=(
                        f"""
Specificeer het volledige bestandspad naar de geopackage/shapefile/geodatabase
met de {self.param} geometrieën.
                        """
                    )
                ).execute()

            filepath = filepath.replace('"', "")

            if not os.path.exists(filepath):
                print(
                    BColors.WARNING,
                    "Het opgegeven bestandspad bestaat niet.",
                    BColors.ENDC,
                )
                skip_batch = True
                continue

            if not (
                filepath.endswith(".gpkg")
                or filepath.endswith(".shp")
                or filepath.endswith(".gdb")
            ):
                print(
                    BColors.WARNING,
                    f"""
                    Het bestand moet of een geopackage, shapefile of geodatabase zijn.
                    Jouw invoer eindigt op de extensie .{filepath.split(sep=".")[-1]}.
                    """,
                    BColors.ENDC,
                )
                skip_batch = True
                continue

            # Import data
            gdf = self._import_data(filepath)  # type:ignore

            # Add data to geopackage
            if self._add_to_gpkg(gdf):
                break

            print(BColors.OKBLUE, f"✅ {self.param} toegevoegd.", BColors.ENDC)

    def _import_data(self, filepath: str) -> gpd.GeoDataFrame:
        """
        Helper method voor het importeren van de data.

        :param filepath: Bestandspad van de shapefile of database met de GIS lagen.
        :raises NotImplementedError: Wanneer het bestand iets anders is dan wordt ondersteund.
        :return: GeoDataFrame met de uitgelezen data.
        :rtype GeoDataFrame:
        """
        if filepath.endswith(".shp"):
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message="Measured \\(M\\) geometry types are not supported.*",
                )
                gdf: gpd.GeoDataFrame = gpd.read_file(filepath)

        elif filepath.endswith(".gpkg"):
            gdf: gpd.GeoDataFrame = self._import_from_db(filepath)

        elif filepath.endswith(".gdb"):
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message="Measured \\(M\\) geometry types are not supported.*",
                )
                gdf: gpd.GeoDataFrame = self._import_from_db(filepath)

        else:
            raise NotImplementedError(
                f"Applicatie vroegtijdig afgesloten: Een {filepath.split(sep='.')[-1]}-bestand is niet geïmplementeerd."
            )

        return gdf

    def _import_from_db(self, filepath: str) -> gpd.GeoDataFrame:
        """
        Helper method voor het importeren vanuit een gbd of een geopackage.

        :param filepath: Bestandspad van de database.
        :return: GeoDataFrame met de uitgelezen data.
        """
        skip_batch = False  # Als batch input faalt ga over op handmatig
        while True:
            if self.app_settings.batch_input and not skip_batch:
                layer_name = self.app_settings.input_config.get(
                    f"{self.param}", "database_layer"
                )
            else:
                layer_name: str = prompt.InputPrompt(
                    message=(
                        f"""
Specificeer de layer waarin de {self.param} staat. Type 'listlayers' om
een overzicht te krijgen van de geodatabase-layers. Type 'cancel' om een
ander bestand op te gaven.
                        """
                    )
                ).execute()

            layer_names = fiona.listlayers(filepath)
            layer_names.sort()
            layers_str = ", ".join(layer_names)
            if layer_name == "listlayers":
                print(
                    f"{BColors.OKBLUE}De volgende layers zijn beschikbaar in de geodatabase: {layers_str}{BColors.ENDC}"
                )
                continue

            if layer_name == "cancel":
                self.request_filepath()

            elif layer_name not in layer_names:
                print(
                    f"{BColors.OKBLUE} De laag name '{layer_name}' bestaat niet. De volgende layers zijn beschikbaar in "
                    f"de geodatabase: {layers_str}{BColors.ENDC}"
                )
                skip_batch = True
                continue

            break

        gdf: gpd.GeoDataFrame = gpd.read_file(filepath, layer=layer_name)  # type:ignore
        return gdf

    def _import_from_shp(self, filepath: str) -> gpd.GeoDataFrame:
        """
        Helper method voor het importeren vanuit een shapefile.

        :param filepath: Bestandspad van de shapefile.
        :return: GeoDataFrame met de uitgelezen data.
        """

        gdf: gpd.GeoDataFrame = gpd.read_file(filepath)
        return gdf

    def _check_shape(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame | None:
        """
        Helper method voor het checken of de geometry het juiste type is.

        :param gdf: GeoDataFrame met de uitgelezen data.
        :return: GeoDataFrame of None als check faalt.
        """

        if self.specific_shape == "":
            return gdf

        if self.specific_shape == "lines":
            all_lines = gdf.geometry.apply(
                lambda geom: (
                    isinstance(geom, LineString)
                    or isinstance(geom, MultiLineString)
                )
            ).all()

            if not all_lines:
                print(
                    BColors.WARNING,
                    """
                    Het geïmporteerde bestand bestaat niet (volledig) uit lijnen,
                    maar ook uit andere typen geometrie. Enkel lijnen zijn toegestaan.
                    """,
                    BColors.ENDC,
                )
                self.request_filepath()

            return gdf

    def _add_to_gpkg(self, gdf: gpd.GeoDataFrame) -> bool:
        """
        Helper method om de data aan de geopackage toe te voegen.
        Start een apart inquiry als en waarden moeten worden toegevoegd aan de
        shape of als er meerdere shapes moeten worden toegevoegd. De kolommen
        moeten van te voren met de juiste suffix in de shape staan.

        De mogelijke suffixen zijn:
        *_mean voor het gemiddelde of deterministische waarde.
        *_dist voor het distributie type.
        *_var voor de variatie.
        *_dev voor de deviatie.
        *_min voor het minimum.
        *_max voor het maximum.

        Als er meerdere scenarios zijn moeten deze als aparte kolommen worden
        toegevoegd met een prefix. Bijvoorbeeld scenario1_*.

        Of als de scenarios als aparte shapes worden ingevoerd, moet er een kolom
        met de naam "ondergrondscenario" zijn toegevoegd.

        :param gdf: GeoDataFrame met de uitgelezen data van de laag.
        :return: bool voor valid_input in while-loop.
        :rtype: bool
        """
        self.suffix_list = ["mean", "dist", "var", "dev", "min", "max"]

        if self.include_value and self.scenarios == "":
            # Case: Alleen suffix, alle kolommen worden met de geometrie weggeschreven.
            return self._add_with_suffix(gdf)

        elif self.include_value and self.scenarios != "":
            # Case: beide affixes, per scenario worden alle kolommen met de
            # geometrieën weggeschreven.
            # Of verschillende geometrieën per scenario
            column_list = gdf.columns.to_list()
            if True in [
                len(column.split("_")) == 3 and self.param in column.split("_")
                for column in column_list
            ]:
                return self._add_with_affixes(gdf)
            else:
                return self._add_separate_with_suffix(gdf)

        elif (
            not self.include_value
            and (
                self.scenarios == ""  # Geen scenarios opgegeven.
                or self.single_geometry  # Vang hier als scenario's niet relevant zijn.
                or not self._scenario_check(
                    gdf.columns.to_list()
                )  # Scenario's niet gekoppeld aan deze laag.
            )
        ):
            # Case: geen affixes alleen de geometrie wordt geschreven.
            gdf_to_add = gdf[["geometry"]]
            gdf_to_add.to_file(
                self.app_settings.geopackage_filepath,
                layer=f"{self.param}",
                driver="GPKG",
            )
            return True

        elif not self.include_value and self.scenarios != "":
            # Case: Alleen losse shapes, de geometrieën worden per scenario geschreven.
            return self._add_with_separate_geometry(gdf)

        else:
            raise ImportError(
                "De laag kan niet worden verwerkt. Controleer of de juiste kolommen aanwezig zijn."
            )

    # Methods voor het controleren van de geodataframes.
    def _scenario_check(self, column_list: list[str]):
        """
        Check of het scenario in de 'ondergrondscenario' kolom voorkomt.

        :param list[str] column_list: Lijst met kolomnamen uit de GeoDataFrame.
        :return: Check of het scenario voorkomt.
        :rtype: bool
        """
        if "ondergrondscenario" not in column_list:
            print(
                BColors.WARNING,
                "Geen kolom met de naam 'ondergrondscenario' gevonden.\n",
                "De volgende kolommen zijn gevonden:\n",
                f"{column_list}",
                BColors.ENDC,
            )

            return False
        else:
            return True

    def _distribution_check(
        self,
        column_list: list[str],
        add_list: list[str],
        gdf: gpd.GeoDataFrame,
    ) -> bool:
        """
        Check of de kolommen de juiste inputs hebben voor de gekozen distributie.
        Als een var of std nodig is, deze aanwezig is. En niet beide aanwezig zijn.

        :param list[sts] column_list: Lijst met kolomnamen.
        :param list[str] add_list: Lijst met geselecteerde kolomnamen voor toe te voegen.
        :param gpd.GeaDataFrame gdf: GeoDataFrame van uitgelezen data.
        :return: Check of de kolommen goed zijn.
        :rtype: bool
        """
        if len(add_list) == 0:
            print(
                BColors.WARNING,
                "De parameter is niet gevonden in de attributen van de laag.",
                f"Alleen deze kolommen zijn gevonden: {', '.join(column_list)}",
                BColors.ENDC,
            )

            return False

        # Check var or std if not deterministic.
        for _, row in gdf.iterrows():
            if row[f"{self.param}_dist"] == "deterministic":
                continue  # Overslaan

            if f"{self.param}_var" in add_list:
                var_bool = row[f"{self.param}_var"] != np.nan or ""
            else:
                var_bool = False

            if f"{self.param}_dev" in add_list:
                dev_bool = row[f"{self.param}_dev"] != np.nan or ""
            else:
                dev_bool = False

            if var_bool and dev_bool:
                print(
                    BColors.WARNING,
                    "Er is zowel een waarde voor de variatie als de standaard deviatie.",
                    BColors.ENDC,
                )
                return False

            if not var_bool and not dev_bool:
                print(
                    BColors.WARNING,
                    "Er is geen waarde voor de variatie of de standaard deviatie.",
                    BColors.ENDC,
                )
                return False

        return True

    # Methods voor het toevoegen aan de database

    def _add_with_separate_geometry(self, gdf: gpd.GeoDataFrame) -> bool:
        """
        Method voor het toevoegen van lagen met meerdere shapes voor
        verschillende scenarios.

        :param gdf: GeoDataFrame met de uitgelezen data.
        :return: bool voor valid_input in while-loop.
        :rtype: bool
        """
        column_list = gdf.columns.to_list()
        if not self._scenario_check(column_list):
            return False

        for scenario in self.scenarios:
            mask = gdf["ondergrondscenario"] == scenario
            gdf_to_add = gdf[mask][["geometry"]]

            if len(gdf_to_add) == 0:
                print(
                    BColors.WARNING,
                    f"Geen geometrieën gevonden met de ondergrondscenarionaam: {scenario}",
                    BColors.ENDC,
                )
                continue

            gdf_to_add.to_file(
                self.app_settings.geopackage_filepath,
                layer=f"{self.param}_{scenario}",
                driver="GPKG",
            )

        return True

    def _add_with_suffix(self, gdf: gpd.GeoDataFrame) -> bool:
        """
        Method voor het schrijven naar de geopackage voor een case met
        parameter invoer en geen scenarios.

        :param gdf: GeoDataFrame met de uitgelezen data.
        :return: bool voor valid_input in while-loop.
        :rtype: bool
        """
        column_list = gdf.columns.to_list()
        add_list = [
            f"{self.param}_{param}"
            for param in self.suffix_list
            if f"{self.param}_{param}" in column_list
        ]

        if not self._distribution_check(column_list, add_list, gdf):
            return False

        gdf_to_add = gdf[["geometry", add_list]]

        gdf_to_add.to_file(
            self.app_settings.geopackage_filepath,
            layer=f"{self.param}",
            driver="GPKG",
        )

        return True

    def _add_with_affixes(self, gdf: gpd.GeoDataFrame) -> bool:
        """
        Voeg de data toe apart per scenario als deze als aparte kolommen in de
        laag staan.

        :param gdf: GeoDataFrame met de uitgelezen data.
        :return: bool voor valid_input in while-loop
        :rtype: bool
        """
        column_list = gdf.columns.to_list()

        for scenario in self.scenarios:
            filter_list = [
                column for column in column_list if column.split("_")[0] == scenario
            ]

            if len(filter_list) == 0:
                print(
                    BColors.WARNING,
                    f"Geen geometrieën gevonden met de ondergrondscenarionaam: {scenario}",
                    BColors.ENDC,
                )
                continue

            filter_list = [
                column.split("_")[1:] for column in filter_list
            ]  # Strip scenario van kolomnaam.

            add_list = [
                f"{self.param}_{suffix}"
                for suffix in self.suffix_list
                if f"{self.param}_{suffix}" in filter_list
            ]

            if not self._distribution_check(column_list, add_list, gdf):
                return False

            gdf_to_add = gdf[["geometry", add_list]]

            gdf_to_add.to_file(
                self.app_settings.geopackage_filepath,
                layer=f"{self.param}_{scenario}",
                driver="GPKG",
            )

        return True

    def _add_separate_with_suffix(self, gdf: gpd.GeoDataFrame) -> bool:
        """
        Voeg de lagen toe los van elkaar per scenario.

        :param gdf: GeoDataFrame met de uitgelezen data.
        :return: bool voor valid_input in while-loop
        """
        column_list = gdf.columns.to_list()
        
        if not self._scenario_check(column_list):
            return False

        for scenario in self.scenarios + [
            None
        ]:  # als er geen scenario zijn opgegeven in de kolom
            if scenario is None:
                mask = gdf["ondergrondscenario"].isna()
            else:
                mask = gdf["ondergrondscenario"] == scenario

            if not mask.any():
                continue

            add_list = [
                f"{self.param}_{suffix}"
                for suffix in self.suffix_list
                if f"{self.param}_{suffix}" in column_list
            ]

            if not self._distribution_check(column_list, add_list, gdf):
                return False

            gdf_to_add = gdf.loc[mask, ["geometry"] + add_list]

            if scenario is None:
                gdf_to_add.to_file(
                    self.app_settings.geopackage_filepath,
                    layer=f"{self.param}",
                    driver="GPKG",
                )

            else:
                gdf_to_add.to_file(
                    self.app_settings.geopackage_filepath,
                    layer=f"{self.param}_{scenario}",
                    driver="GPKG",
                )

        return True
