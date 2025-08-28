from __future__ import annotations
from geoprob_pipe.pre_processing.general import created_project, created_model
from geoprob_pipe.pre_processing.spatial_layers import (
    added_dijktraject, added_vakindeling, added_uittredepunten, added_hrd, added_polderpeil, added_binnenteenlijn,
    added_buitenteenlijn, added_intredelijn)
from geoprob_pipe.pre_processing.spatial_joins import coupled_hrd_to_uittredepunten
from typing import TYPE_CHECKING
import sys
if TYPE_CHECKING:
    from geoprob_pipe.cmd import ApplicationSettings


def start_pre_processing_questionnaire(app_settings: ApplicationSettings):
    early_exit_message = f"Applicatie vroegtijdig afgesloten"

    if not created_project(app_settings=app_settings): sys.exit(early_exit_message)

    print(f"\nALGEMEEN")
    if not created_model(app_settings=app_settings): sys.exit(early_exit_message)

    print(f"\nGIS LAGEN")
    if not added_dijktraject(app_settings=app_settings): sys.exit(early_exit_message)
    if not added_vakindeling(app_settings=app_settings): sys.exit(early_exit_message)
    if not added_hrd(app_settings=app_settings): sys.exit(early_exit_message)
    if not added_uittredepunten(app_settings=app_settings): sys.exit(early_exit_message)
    if not added_polderpeil(app_settings=app_settings): sys.exit(early_exit_message)
    if not added_binnenteenlijn(app_settings=app_settings): sys.exit(early_exit_message)
    if not added_buitenteenlijn(app_settings=app_settings): sys.exit(early_exit_message)
    if not added_intredelijn(app_settings=app_settings): sys.exit(early_exit_message)

    print(f"\nGEOGRAFISCHE KOPPELINGEN")
    if not coupled_hrd_to_uittredepunten(app_settings=app_settings): sys.exit(early_exit_message)
    # if not calculated_intrede_distance(app_settings=app_settings): sys.exit(early_exit_message)
    # if not calculated_but_distance(app_settings=app_settings): sys.exit(early_exit_message)
    # if not calculated_bit_distance(app_settings=app_settings): sys.exit(early_exit_message)
    # if not calculated_exit_distance(app_settings=app_settings): sys.exit(early_exit_message)
