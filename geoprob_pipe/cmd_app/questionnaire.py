from __future__ import annotations
from geoprob_pipe.cmd_app.general.project import created_project
from geoprob_pipe.cmd_app.general.geohydrologisch_model import created_model
from geoprob_pipe.cmd_app.spatial_layers import (
    added_dijktraject, added_vakindeling, added_uittredepunten, added_polderpeil, added_binnenteenlijn,
    added_buitenteenlijn, added_intredelijn, added_ahn, added_hrd_fragility_curves)
from geoprob_pipe.cmd_app.spatial_joins import (
    coupled_hrd_to_uittredepunten, coupled_distances_to_uittredepunten, coupled_polderpeil_to_uittredepunten,
    coupled_uittredepunten_to_refline, coupled_uittredepunten_to_vakken, coupled_mv_exit_to_gis_parameter_invoer_table)
from geoprob_pipe.cmd_app.parameter_input.added_input_parameters import added_input_parameter_data
from typing import TYPE_CHECKING
from geoprob_pipe.cmd_app.run_calculations.run import run_calculations
import sys
if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


EARLY_EXIT_MESSAGE = f"Applicatie vroegtijdig afgesloten"


def start_questionnaire(app_settings: ApplicationSettings):
    if not created_project(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    questionnaire(app_settings=app_settings)


def questionnaire(app_settings: ApplicationSettings):
    print(f"\nALGEMEEN")
    if not created_model(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)

    print(f"\nGIS LAGEN")
    if not added_dijktraject(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not added_vakindeling(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not added_hrd_fragility_curves(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    # if not added_hrd(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not added_uittredepunten(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not added_polderpeil(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not added_binnenteenlijn(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not added_buitenteenlijn(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not added_intredelijn(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    added_ahn(app_settings=app_settings, display_added_msg=True)  # AHN may be optional

    print(f"\nGEOGRAFISCHE KOPPELINGEN")
    if not coupled_uittredepunten_to_refline(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not coupled_hrd_to_uittredepunten(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not coupled_distances_to_uittredepunten(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not coupled_polderpeil_to_uittredepunten(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not coupled_uittredepunten_to_vakken(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not coupled_mv_exit_to_gis_parameter_invoer_table(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)

    print(f"\nPARAMETER INVOER")
    if not added_input_parameter_data(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)

    print(f"\nBEREKENINGEN UITVOEREN")
    if not run_calculations(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
