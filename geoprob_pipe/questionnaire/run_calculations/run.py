from __future__ import annotations
from InquirerPy import inquirer
from geoprob_pipe import GeoProbPipe
import sys
from geoprob_pipe.utils.validation_messages import BColors
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from geoprob_pipe.questionnaire.cmd import ApplicationSettings


def run_calculations(app_settings: ApplicationSettings) -> bool:
    choices_list = ["Ja", "Nee (applicatie sluit af)"]
    choice = inquirer.select(
        message="Wil je de berekeningen uitvoeren? ", choices=choices_list, default=choices_list[0],
    ).execute()

    if choice == choices_list[0]:
        geoprob_pipe = GeoProbPipe(app_settings)
        geoprob_pipe.export_archive()
        print(BColors.OKBLUE, f"✅  Berekeningen zijn uitgevoerd.", BColors.ENDC)
    elif choice == choices_list[1]:
        sys.exit(f"Applicatie is afgesloten.")
    else:
        raise ValueError
    return True
