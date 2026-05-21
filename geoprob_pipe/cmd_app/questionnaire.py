from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from geoprob_pipe.cmd_app.general.geohydrologisch_model import created_model
from geoprob_pipe.cmd_app.general.project import created_project
from geoprob_pipe.cmd_app.general.traject_parameters import (
    added_traject_parameters,
)
from geoprob_pipe.cmd_app.parameter_input.added_input_parameters import (
    added_input_parameter_data,
)
from geoprob_pipe.cmd_app.run_calculations.run import run_calculations
from geoprob_pipe.cmd_app.spatial_joins import (
    coupled_distances_to_uittredepunten,
    coupled_hrd_to_uittredepunten,
    coupled_mv_exit_to_gis_parameter_invoer_table,
    coupled_parameters_to_uittredepunten,
    coupled_uittredepunten_to_refline,
    coupled_uittredepunten_to_vakken,
)
from geoprob_pipe.cmd_app.spatial_layers import (
    added_ahn,
    added_binnenteenlijn,
    added_buitenteenlijn,
    added_dijktraject,
    added_hrd_fragility_curves,
    added_intredelijn,
    added_parameters,
    added_ruimtelijke_input,
    added_scenarios,
    added_uittredepunten,
    added_vakindeling,
    check_batch_input,
)

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


EARLY_EXIT_MESSAGE = "Applicatie vroegtijdig afgesloten"


def start_questionnaire(app_settings: ApplicationSettings):
    if not created_project(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)
    questionnaire(app_settings=app_settings)


def questionnaire(app_settings: ApplicationSettings):
    print("\nALGEMEEN")
    if not created_model(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)
    if not added_scenarios(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)
    if not added_parameters(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)
    # TODO Vincent: batch invoer bestand mogelijk maken
    if not check_batch_input(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)

    print("\nGIS LAGEN")
    if not added_dijktraject(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)
    if not added_vakindeling(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)
    if not added_hrd_fragility_curves(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)
    if not added_traject_parameters(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)
    if not added_uittredepunten(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)
    if not added_binnenteenlijn(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)
    if not added_buitenteenlijn(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)
    if not added_intredelijn(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)
    
    print("\nRUIMTELIJKE INPUT")
    # Loop voor alle parameters
    if not added_ruimtelijke_input(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)
    added_ahn(
        app_settings=app_settings, display_added_msg=True
    )  # AHN may be optional

    print("\nGEOGRAFISCHE KOPPELINGEN")
    # TODO Vincent: maak coupleling for raster
    if not coupled_parameters_to_uittredepunten(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)
    if not coupled_uittredepunten_to_refline(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)
    if not coupled_distances_to_uittredepunten(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)
    if not coupled_uittredepunten_to_vakken(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)
    if not coupled_hrd_to_uittredepunten(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)
    if not coupled_mv_exit_to_gis_parameter_invoer_table(
        app_settings=app_settings
    ):
        sys.exit(EARLY_EXIT_MESSAGE)

    print("\nPARAMETER INVOER")
    # TODO Vincent: Optie om GIS invoer te vervangen.
    # TODO Vincent: Check validation correct blijft werken.
    # TODO Vincent: verwijder traject waardes als gis_join al waardes heeft.
    # Misschien checken of de orde van overschrijven wel logisch is?
    # Excel over gis maar wel gis-uittredepunt over excel-traject?
    if not added_input_parameter_data(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)

    print("\nBEREKENINGEN UITVOEREN")
    if not run_calculations(app_settings=app_settings):
        sys.exit(EARLY_EXIT_MESSAGE)
