from __future__ import annotations

import sqlite3
import sys
from typing import TYPE_CHECKING

import fiona
from InquirerPy.prompts.input import InputPrompt
from InquirerPy.prompts.list import ListPrompt

from geoprob_pipe.cmd_app.spatial_layers import valid_parameter_list
from geoprob_pipe.utils.validation_messages import BColors
from geoprob_pipe.cmd_app.utils.batch_input import update_batch_metadata

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


class SpatialUpdateMenu:
    restart_flag: bool = False
    
    def __init__(
        self,
        app_settings: ApplicationSettings,
    ) -> None:
        """
        Class voor alle submenus onder het aanpassen vaan de ruimtelijke invoer.

        :param app_settings: Object met de instellingen van de applicatie
        """        
        self.app_settings = app_settings

    def inquire_spatial_update(
        self,
    ) -> None:
        """
        Keuzemenu voor het updaten van de ruimtelijke invoer van de .gpkg.

        :param app_settings: Object met de instellingen van de applicatie
        """
        

        while True:
            choices_list = [
                "Vervang ingevoerde lagen",
                "Voeg parameters toe voor ruimtelijke invoer",
                "Verwijder parameters voor ruimtelijke invoer",
                "Voeg scenarios toe voor ruimtelijke invoer",
                "Verwijder scenarios voor ruimtelijke invoer",
            ]
        
            if self.restart_flag:
                choices_list.append("Applicatie afsluiten na aanpassingen")
            else:
                choices_list.append("Ga terug naar het parameter invoer menu")
                
            choice = ListPrompt(
                message="Maak een keuze voor het aanpassen van de ruimtelijke invoer.",
                choices=choices_list,
                default=choices_list[0],
            ).execute()

            match choice:
                case "Vervang ingevoerde lagen":
                    self.inquire_replace_layers()
                    continue

                case "Voeg parameters toe voor ruimtelijke invoer":
                    self.add_parameters()
                    continue

                case "Verwijder parameters voor ruimtelijke invoer":
                    self.remove_parameters()
                    continue

                case "Voeg scenarios toe voor ruimtelijke invoer":
                    self.add_scenarios()
                    continue

                case "Verwijder scenarios voor ruimtelijke invoer":
                    self.remove_scenarios()
                    continue
                
                case "Applicatie afsluiten na aanpassingen":
                    sys.exit("Applicatie is afgesloten.")
                    
                case "Ga terug naar het parameter invoer menu":
                    return

    def inquire_replace_layers(self) -> None:
        """
        Verwijder tabellen die opnieuw moeten worden ingeladen om de geopackage te
        updaten.
        """
        conn = sqlite3.connect(self.app_settings.geopackage_filepath)

        # Haal ruimtelijke parameters op vanuit de metadata
        cursor = conn.cursor()
        cursor.execute(
            "SELECT metadata_value FROM geoprob_pipe_metadata WHERE metadata_type = ?",
            ("ruimtelijke_parameters",),
        )
        parameters: list[str] = cursor.fetchone()[0].split(", ")

        conn.commit()
        conn.close()

        valid_list = valid_parameter_list(self.app_settings)

        while True:
            parameter_input: str = InputPrompt(
                message=f"""
De volgende parameters zijn nu aangemerkt voor ruimtelijke invoer:
{", ".join(parameters)}
Welke parameters wil je updaten? Geef deze met comma's gescheiden op.
De tabellen worden verwijderd uit de geopackage zodat deze opnieuw worden ingelezen.
Als er niets wordt opgegeven wordt je terug gestuurd naar het keuzemenu.
"""
            ).execute()

            if parameter_input == "":
                print(
                    BColors.OKBLUE,
                    "Geen tabellen verwijderd.",
                    BColors.ENDC,
                )
                return

            valid_input = all(
                [
                    param
                    for param in parameter_input.split(",")
                    if param in valid_list
                ]
            )
            if not valid_input:
                print(
                    BColors.OKBLUE,
                    f"Geen parameters toegevoegd. '{parameter_input}' bevat een ongeldige parameter.",
                    BColors.ENDC,
                )
                continue

            break

        # Verwijder uit geopackage
        layers: list[str] = fiona.listlayers(
            self.app_settings.geopackage_filepath
        )
        table_list = [
            layer
            for layer in layers
            if layer.split("__")[0] in parameter_input
        ]
        self.remove_tables(table_list)
        self.completed_update()

    def add_parameters(self) -> None:
        """
        Voeg extra parameters toe voor de ruimtelijke invoer. De aanpassingen
        kunnen pas verwerkt worden nadat de applicatie opnieuw is opgestart.
        """

        conn = sqlite3.connect(self.app_settings.geopackage_filepath)

        # Haal ruimtelijke parameters op vanuit de metadata
        cursor = conn.cursor()
        cursor.execute(
            "SELECT metadata_value FROM geoprob_pipe_metadata WHERE metadata_type = ?",
            ("ruimtelijke_parameters",),
        )
        current_parameters: list[str] = cursor.fetchone()[0].split(", ")

        conn.commit()
        conn.close()

        # Haal lijst met geldige parameters op.
        valid_list = valid_parameter_list(self.app_settings)

        # Vraag gebruiker voor toevoegingen.
        while True:
            parameter_input: str = InputPrompt(
                message=f"""
De volgende parameters zijn nu aangemerkt voor ruimtelijke invoer:
{", ".join(current_parameters)}
De volgende parameters kunnen worden toegevoegd:
{[param for param in valid_list if param not in current_parameters]}
Welke parameters wil je hieraan toevoegen? Geef deze met comma's gescheiden op.
Als er niets wordt opgegeven wordt je terug gestuurd naar het keuzemenu.
"""
            ).execute()

            if parameter_input == "":
                print(
                    BColors.OKBLUE,
                    "Geen nieuwe parameters toegevoegd.",
                    BColors.ENDC,
                )
                return

            valid_input = all(
                [
                    param
                    for param in parameter_input.split(",")
                    if param in valid_list
                ]
            )

            if not valid_input:
                print(
                    BColors.OKBLUE,
                    f"Geen parameters toegevoegd. '{parameter_input}' bevat een ongeldige parameter.",
                    BColors.ENDC,
                )
                continue

            break

        # Update metadata
        parameters = current_parameters + parameter_input.split(",")
        parameters = list(set(parameters))  # Verwijder dubbele waardes
        parameters = ", ".join(parameters)
        self.update_metadata_parameters(parameters)

        self.completed_update()

    def remove_parameters(self) -> None:
        conn = sqlite3.connect(self.app_settings.geopackage_filepath)

        # Haal ruimtelijke parameters op vanuit de metadata
        cursor = conn.cursor()
        cursor.execute(
            "SELECT metadata_value FROM geoprob_pipe_metadata WHERE metadata_type = ?",
            ("ruimtelijke_parameters",),
        )
        parameters: list[str] = cursor.fetchone()[0].split(", ")

        conn.commit()
        conn.close()

        valid_list = valid_parameter_list(self.app_settings)

        while True:
            parameter_input: str = InputPrompt(
                message=f"""
De volgende parameters zijn nu aangemerkt voor ruimtelijke invoer:
{", ".join(parameters)}
Welke parameters wil je verwijderen? Geef deze met comma's gescheiden op.
Als er niets wordt opgegeven wordt je terug gestuurd naar het keuzemenu.
"""
            ).execute()

            if parameter_input == "":
                print(
                    BColors.OKBLUE,
                    "Geen parameters verwijderd.",
                    BColors.ENDC,
                )
                return

            valid_input = all(
                [
                    param
                    for param in parameter_input.split(",")
                    if param in valid_list
                ]
            )

            if not valid_input:
                print(
                    BColors.OKBLUE,
                    f"Geen parameters toegevoegd. '{parameter_input}' bevat een ongeldige parameter.",
                    BColors.ENDC,
                )
                continue

            break

        # Update metadata
        for parameter in parameter_input.split(","):
            parameters.remove(parameter)

        updated_parameters = ", ".join(parameters)
        self.update_metadata_parameters(updated_parameters)
        # Verwijder uit geopackage
        layers: list[str] = fiona.listlayers(
            self.app_settings.geopackage_filepath
        )
        table_list = [
            layer
            for layer in layers
            if layer.split("__")[0] in updated_parameters
        ]
        self.remove_tables(table_list)
        self.completed_update()

    def add_scenarios(self) -> None:
        """
        Voeg ondergrondscenarios toe aan de lijst. Dit betekent dat alle
        ruimtelijke invoer opnieuw moet worden ingeladen.
        """
        # Haal de huidige scenarios op.
        conn = sqlite3.connect(self.app_settings.geopackage_filepath)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT metadata_value FROM geoprob_pipe_metadata WHERE metadata_type = ?",
            ("ruimtelijke_scenarios",),
        )
        current_scenarios: list[str] = cursor.fetchone()[0].split(", ")

        conn.commit()
        conn.close()

        # Vraag gebruiker voor toevoegingen.
        while True:
            scenario_input = InputPrompt(
                message=f"""
De volgende scenario zijn nu toegevoegd:
{", ".join(current_scenarios)}
Welke scenarios wil je hieraan toevoegen? Geef deze met comma's gescheiden op.
Als er niets wordt opgegeven wordt je terug gestuurd naar het keuzemenu.
"""
            ).execute()

            if scenario_input == "":
                print(
                    BColors.OKBLUE,
                    "Geen nieuwe scenarios toegevoegd.",
                    BColors.ENDC,
                )
                return

            # Update metadata
            updated_scenarios = current_scenarios + scenario_input
            self.update_metadata_scenarios(", ".join(updated_scenarios))

            # Remove tables to recollect data.
            self.remove_tables()

    def remove_scenarios(self) -> None:
        """
        Verwijder ondergrondscenarios uit de lijst. Dit betekent dat alle
        ruimtelijke invoer opnieuw moet worden ingeladen.
        """
        # Haal de huidige scenarios op.
        conn = sqlite3.connect(self.app_settings.geopackage_filepath)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT metadata_value FROM geoprob_pipe_metadata WHERE metadata_type = ?",
            ("ruimtelijke_scenarios",),
        )
        current_scenarios: list[str] = cursor.fetchone()[0].split(", ")

        conn.commit()
        conn.close()

        # Vraag gebruiker voor toevoegingen.
        while True:
            scenario_input = InputPrompt(
                message=f"""
De volgende scenario zijn nu toegevoegd:
{", ".join(current_scenarios)}
Welke scenarios wil je verwijderen? Geef deze met comma's gescheiden op.
Als er niets wordt opgegeven wordt je terug gestuurd naar het keuzemenu.
"""
            ).execute()

            if scenario_input == "":
                print(
                    BColors.OKBLUE,
                    "Geen scenarios verwijderd.",
                    BColors.ENDC,
                )
                return

            # Update metadata
            for scenario in scenario_input.split(","):
                if scenario in current_scenarios:
                    current_scenarios.remove(scenario)
                else:
                    print(
                        BColors.WARNING,
                        f"Scenario {scenario} niet gevonden.",
                        BColors.ENDC,
                    )

            self.update_metadata_scenarios(", ".join(current_scenarios))

            # Remove tables to recollect data.
            self.remove_tables()

    def update_metadata_scenarios(self, scenarios: str) -> None:
        """
        Update de ondergrondscenarios in de metadata.
        :param scenarios: Nieuwe versie van de scenariios string voor in de metadata.
        """
        conn = sqlite3.connect(self.app_settings.geopackage_filepath)

        sql_update = "UPDATE geoprob_pipe_metadata SET metadata_value = ? WHERE metadata_type = ?"

        with conn:  # transaction
            conn.execute(sql_update, (scenarios, "ruimtelijke_scenarios"))

        conn.commit()
        conn.close()

    def update_metadata_parameters(self, parameters: str) -> None:
        """
        Update de parameters voor ruimtelijke invoer in de metadata.
        
        :param parameters: nieuwe versie van de parameters string voor in de metadata
        """
        conn = sqlite3.connect(self.app_settings.geopackage_filepath)

        sql_update = "UPDATE geoprob_pipe_metadata SET metadata_value = ? WHERE metadata_type = ?"
        sql_insert = "INSERT INTO geoprob_pipe_metadata (metadata_type, metadata_value) VALUES (?, ?)"

        with conn:  # transaction
            cur = conn.execute(
                sql_update, (parameters, "ruimtelijke_parameters")
            )  # type:ignore
            if cur.rowcount == 0:
                conn.execute(
                    sql_insert, ("ruimtelijke_parameters", parameters)
                )  # type:ignore

        conn.commit()
        conn.close()

    def remove_tables(self, table_list: list[str] = []) -> None:
        """
        Verwijder de tabellen uit de geopackage en de metadata zodat deze opnieuw
        kunnen worden ingeladen. Als de lijst leeg is worden alle tabellen met
        ruimtelijke invoer verwijderd.

        :param table_list: Lijst met tabellen om te verwijderen, defaults to []
        """
        update_batch_metadata(self.app_settings, value=True)
        # Voor vervangen, nieuwe scenarios of verwijderen van parameters.
        conn = sqlite3.connect(self.app_settings.geopackage_filepath)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT metadata_value FROM geoprob_pipe_metadata WHERE metadata_type = ?",
            ("ruimtelijke_parameters",),
        )

        parameters: list[str] = cursor.fetchone()[0].split(", ")
        parameters.append("intredelijn")
        layers: list[str] = fiona.listlayers(
            self.app_settings.geopackage_filepath
        )

        if table_list == []:  # Remove all spatial input
            for layer in layers:
                if layer.split("__")[0] in parameters:
                    cursor.execute(f"DROP TABLE IF EXISTS {layer}")
                    cursor.execute(
                        "DELETE FROM gpkg_contents WHERE table_name = ?",
                        (layer,),
                    )
                    cursor.execute(
                        "DELETE FROM gpkg_geometry_columns WHERE table_name = ?",
                        (layer,),
                    )
                    cursor.execute(
                        "DELETE FROM gpkg_tile_matrix_set WHERE table_name = ?",
                        (layer,),
                    )
                    cursor.execute(
                        "DELETE FROM gpkg_tile_matrix WHERE table_name = ?",
                        (layer,),
                    )

        else:
            for layer in table_list:
                if layer in layers:
                    cursor.execute(f"DROP TABLE IF EXISTS {layer}")
                    cursor.execute(
                        "DELETE FROM gpkg_contents WHERE table_name = ?",
                        (layer,),
                    )
                    cursor.execute(
                        "DELETE FROM gpkg_geometry_columns WHERE table_name = ?",
                        (layer,),
                    )
                    cursor.execute(
                        "DELETE FROM gpkg_tile_matrix_set WHERE table_name = ?",
                        (layer,),
                    )
                    cursor.execute(
                        "DELETE FROM gpkg_tile_matrix WHERE table_name = ?",
                        (layer,),
                    )

        conn.commit()
        conn.close()

    def completed_update(self) -> None:
        """
        Na aanpassing van de opties moet de applicatie opnieuw opstarten. Bied
        de optie om meerdere aanpassingen te doen voordat de applicatie wordt
        afgesloten.
        """
        choices_list = ["Andere aanpassing uitvoeren", "Applicatie afsluiten"]
        while True:
            choice = ListPrompt(
                message=(
                    "Om de aanpassingen te verwerken moet de applicatie opnieuw worden gestart. "
                    "Het is mogelijk om meerdere aanpassingen in een keer te doen."
                ),
                choices=choices_list,
                default=choices_list[0],
            ).execute()

            match choice:
                case "Andere aanpassing uitvoeren":
                    self.restart_flag = True
                    return

                case "Applicatie afsluiten":
                    sys.exit("Applicatie is afgesloten.")
