"""
Baseclass voor het opvragen van de ruimtelijke invoer voor de parameters.
"""

from __future__ import annotations

import os
import sqlite3
import warnings
from typing import TYPE_CHECKING

import fiona
import geopandas as gpd
import InquirerPy.prompts.input as prompt
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
    ) -> None:
        """
        Class om de opvraag van de ruimteljke invoer van de parameters.

        :param app_settings: `ApplicationSettings` object
        :param param: Parameter die wordt opgevraagd.
        :param scenarios: Lijst met scenarios voor ruimtelike invoer.
        :param specific_shape: Welke soort ruimtelijke invoer acceptabel is, defaults to "".
            Geldige invoer is "lines", "polygons" of "rasters".
        :param include_value: Of er naast de geometrie zelf ook een bepaalde
            waarde moet worden toegevoegd aan de geopackage, defaults to False
        """
        self.app_settings = app_settings
        self.param = param
        self.specific_shape = specific_shape
        self.include_value = include_value
        conn = sqlite3.connect(app_settings.geopackage_filepath)
        cur = conn.cursor()
        cur.execute(
            "SELECT values FROM geoprob_pipe_metadata WHERE metadata = ?",
            ("ruimtelijke_scenarios",),
        )
        self.scenarios = cur.fetchone()[0]

    def request_filepath(self):
        """
        Method voor het opvragen van het filepath.
        """

        filepath_is_valid = False

        while filepath_is_valid is False:
            filepath: str = prompt.InputPrompt(
                message=f"""
                Specificeer het volledige bestandspad naar de geopackage/shapefile/geodatabase
                met de {self.param} geometrieën.
                """
            ).execute()

            filepath = filepath.replace('"', "")

            if not os.path.exists(filepath):
                print(
                    BColors.WARNING,
                    "Het opgegeven bestandspad bestaat niet.",
                    BColors.ENDC,
                )
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
                continue

            filepath_is_valid = True

        # Import data
        gdf = self._import_data(filepath)  # type:ignore

        # Add data to geopackage
        self._add_to_gpkg(gdf)

    def _import_data(self, filepath: str) -> gpd.GeoDataFrame:
        """
        Helper method voor het importeren van de data.

        :param filepath: _description_
        :raises NotImplementedError: _description_
        :return: _description_
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

        :param filepath: _description_
        :return: _description_
        """
        layer_name_is_valid = False
        while layer_name_is_valid is False:
            layer_name: str = prompt.InputPrompt(
                message=f"""
                Specificeer de layer waarin de {self.param} staat. Type 'listlayers' om
                een overzicht te krijgen van de geodatabase-layers. Type 'cancel' om een
                ander bestand op te gaven.
                        """
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
                continue

            layer_name_is_valid = True

        gdf: gpd.GeoDataFrame = gpd.read_file(filepath, layer=layer_name)  # type:ignore
        return gdf

    def _import_from_shp(self, filepath: str) -> gpd.GeoDataFrame:
        """
        Helper method voor het importern vanuit een shapefile.

        :param filepath: _description_
        :return: _description_
        """

        gdf: gpd.GeoDataFrame = gpd.read_file(filepath)
        return gdf

    def _check_shape(self, gdf: gpd.GeoDataFrame):
        """
        Helper method voor het checken of de geometry het juiste type is.

        :param gdf: _description_
        :return: _description_
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

    def _add_to_gpkg(self, gdf: gpd.GeoDataFrame):
        """
        Helper method om de data aan de geopackage toe te voegen.

        :param gdf: _description_
        """
        layer_name = self.param
        if self.include_value and self.scenarios == "":
            column_name_is_valid = False
            while column_name_is_valid is False:
                column_name: str = prompt.InputPrompt(
                    message=f"""
                    Specificeer de kolom waarin {self.param} staat. Type 'listcolumns' om"
                    een overzicht te krijgen van de kolommen. Type 'cancel' om een ander bestand op te geven.
                    """,
                ).execute()

                column_names = gdf.columns
                columns_str = ", ".join(column_names)
                if column_name == "listcolumns":
                    print(
                        BColors.OKBLUE,
                        f"De volgende kolommen zijn beschikbaar in de spatial layer: {columns_str}",
                        BColors.ENDC,
                    )
                    continue

                elif column_name == "cancel":
                    self.request_filepath()

                elif column_name not in column_names:
                    print(
                        BColors.OKBLUE,
                        f"De kolom naam '{column_name}' bestaat niet. De volgende kolommen zijn beschikbaar "
                        f"in de spatial layer: {columns_str}",
                        BColors.ENDC,
                    )
                    continue

                column_name_is_valid = True

            gdf_to_add = gdf[["geometry", column_name]]  # type:ignore
            gdf_to_add.to_file(
                self.app_settings.geopackage_filepath,
                layer=f"{layer_name}",
                driver="GPKG",
            )

        elif self.include_value and self.scenarios != "":
            gdf_to_add = gdf[["geometry", self.scenarios]]
            gdf_to_add.to_file(
                self.app_settings.geopackage_filepath,
                layer=f"{layer_name}",
                driver="GPKG",
            )

        elif not self.include_value and self.scenarios == "":
            gdf_to_add = gdf[["geometry"]]
            gdf_to_add.to_file(
                self.app_settings.geopackage_filepath,
                layer=f"{layer_name}",
                driver="GPKG",
            )

        elif not self.include_value and self.scenarios != "":
            valid_anwser = False
            while not valid_anwser:
                add_layer_per_scenario = prompt.InputPrompt(
                    message=f"""
                    Moeten er lagen per ruimtelijk scenario voor {self.param} worden ingeladen?
                    Er moet een kolom met de naam 'ondergrondscenario' in de attribute tabel
                    staan met de naam van het scenario waar de geometrie bijhoort.
                    (y/n)? O ftype 'cancel' om een ander bestand op te geven.
                    """
                )
                if add_layer_per_scenario == "y":
                    # per shape id of naam?
                    for scenario in self.scenarios:
                        gdf_to_add: gpd.GeoDataFrame = gdf[
                            gdf["ondergrondscenario"] == scenario
                        ][["geometry"]]
                        layer_name = f"{self.param}_{scenario}"
                        gdf_to_add.to_file(
                            self.app_settings.geopackage_filepath,
                            layer=f"{layer_name}",
                            driver="GPKG",
                        )
                    pass
                elif add_layer_per_scenario == "n":
                    gdf_to_add = gdf[["geometry"]]
                    gdf_to_add.to_file(
                        self.app_settings.geopackage_filepath,
                        layer=f"{layer_name}",
                        driver="GPKG",
                    )
                    valid_anwser = True
                elif add_layer_per_scenario == "cancel":
                    self.request_filepath()
                else:
                    continue

        print(BColors.OKBLUE, f"✅ {self.param} toegevoegd.", BColors.ENDC)
