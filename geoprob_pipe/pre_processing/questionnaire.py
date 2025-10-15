from __future__ import annotations
from geoprob_pipe.pre_processing.general import created_project, created_model
from geoprob_pipe.pre_processing.spatial_layers import (
    added_dijktraject, added_vakindeling, added_uittredepunten, added_hrd, added_polderpeil, added_binnenteenlijn,
    added_buitenteenlijn, added_intredelijn, added_ahn)
from geoprob_pipe.pre_processing.spatial_joins import (
    coupled_hrd_to_uittredepunten, coupled_distances_to_uittredepunten, coupled_polderpeil_to_uittredepunten,
    coupled_uittredepunten_to_refline, coupled_uittredepunten_to_vakken)
from geoprob_pipe.pre_processing.parameter_input import added_input_parameter_data
from typing import TYPE_CHECKING
import sys
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings


EARLY_EXIT_MESSAGE = f"Applicatie vroegtijdig afgesloten"


def start_pre_processing_questionnaire(app_settings: ApplicationSettings):
    if not created_project(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    pre_processing_questionnaire(app_settings=app_settings)


def pre_processing_questionnaire(app_settings: ApplicationSettings):
    print(f"\nALGEMEEN")
    if not created_model(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)

    print(f"\nGIS LAGEN")
    if not added_dijktraject(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not added_vakindeling(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not added_hrd(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not added_uittredepunten(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not added_polderpeil(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not added_binnenteenlijn(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not added_buitenteenlijn(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not added_intredelijn(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    added_ahn(app_settings=app_settings, display_added_msg=True)  # AHN may be optional

    print(f"\nGEOGRAFISCHE KOPPELINGEN")
    if not coupled_hrd_to_uittredepunten(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not coupled_distances_to_uittredepunten(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not coupled_polderpeil_to_uittredepunten(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not coupled_uittredepunten_to_refline(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    if not coupled_uittredepunten_to_vakken(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)

    print(f"\nPARAMETER INVOER")
    if not added_input_parameter_data(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    # if not expanded_input_parameter_data(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
    # if not input_parameter_data_covers_all(app_settings=app_settings): sys.exit(EARLY_EXIT_MESSAGE)
