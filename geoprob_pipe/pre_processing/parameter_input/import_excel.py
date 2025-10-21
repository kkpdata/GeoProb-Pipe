from __future__ import annotations
from InquirerPy import inquirer
from typing import Optional, TYPE_CHECKING
import os
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings
from geoprob_pipe.utils.validation_messages import BColors
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings

class ImportInputExcel:

    def __init__(self, app_settings: ApplicationSettings):
        self.app_settings: ApplicationSettings = app_settings

        # Perform logic
        self._request_file_path_or_use_saved_version()
        self._initial_validation_input_excel()
        self._inquire_to_export_parameter_input_figures()
        self._expand_parameter_input_per_uittredepunt_and_scenario()
        self._validate_expanded_parameter_input()
        self._inquire_if_user_wishes_to_save_input_excel()

    def _request_file_path_or_use_saved_version(self):
        """ File path is not always necessary, as the input Excel will eventually also be stored in the GeoPacakge.
        When it is stored in the GeoPackage, this class is meant for validating before continuing in the pre-processing
        questionnaire. """

        # Check if already saved version
        # TODO

        #

        pass

    def _initial_validation_input_excel(self):
        """ Validates if each row in the input Excel.

        There is secondary validation that is not part of this method. This validation first requires some
        dataprocessing before it can be executed. For instance, if the input can be expanded over all uittredepunten
        and scenarios. """
        pass

    def _inquire_to_export_parameter_input_figures(self):
        """ From the input Excel, i.c.w. the spatially referenced input, graphs can be created that display how
        the input covers the entire trajectory. This method asks the user if he/she wished to export those figures
        for inspection. """
        pass

    def _expand_parameter_input_per_uittredepunt_and_scenario(self):
        """ From the input Excel, i.c.w. the spatially referenced input, the input can be expanded/exploded to each
        uittredepunt and scenario. This makes it directly usable for the reliability calculations, but also, especially
        for this stage to validate if all necessary info is provided. """
        pass

    def _validate_expanded_parameter_input(self):
        """ Setting up the input is considered an iterative process, and part of that process is the guide the user
        through validation """
        pass

    def _inquire_if_user_wishes_to_save_input_excel(self):
        """ Asks the user if he/she wished to save the input Excel. The user can do this both for a valid or an invalid
        input Excel. For the latter case, the user will later on be requested to first correct the Excel, before
        calculations can be executed. That the user can still save the Excel, offers him/her the possibility to
        continue later on with the input process. """
        pass



def import_excel(app_settings: ApplicationSettings):
    # Benodigde identifiers ophalen voor invoer per scenario opzetten
    #   - df_uittredepunt met 'uittredepunt_id' en 'vak_id'
    #   - mergen met df_ondergrondscenarios:
    #       - explodeert df_uittredepunt naar rij per scenario
    #       - voeg kolom ondergrondscenario_id toe
    # Merge per parameter op uittredepunt-niveau met de 'Parameter invoer'-Excel sheet
    # Voor de lege cellen, merge per parameter op scenario en vakniveau-niveau met de 'Parameter invoer'-Excel sheet
    # Voor de lege cellen, merge per parameter op vakniveau-niveau met de 'Parameter invoer'-Excel sheet
    # Voor de lege cellen, merge per parameter op traject-niveau met de 'Parameter invoer'-Excel sheet
    # Voor overige lege cellen, geeft validatie error terug.

    filepath: Optional[str] = None
    filepath_is_valid = False
    while filepath_is_valid is False:
        filepath: str = inquirer.text(
            message="Specificeer het volledige bestandspad naar het .geoprob_pipe.gpkg-bestand.",
        ).execute()

        filepath = filepath.replace('"', '')

        if not filepath.endswith(".geoprob_pipe.gpkg"):
            print(BColors.WARNING, f"Het bestand moet een .geoprob_pipe.gpkg-bestand zijn. Jouw invoer "
                                   f"{os.path.basename(filepath)} eindigt niet op deze extensie.", BColors.ENDC)
            continue
        if not os.path.exists(filepath):
            print(BColors.WARNING, f"Het opgegeven bestandspad bestaat niet.", BColors.ENDC)
            continue

        filepath_is_valid = True

    app_settings.workspace_dir = os.path.dirname(filepath)
    app_settings.geopackage_filename = os.path.basename(filepath)

    pass
