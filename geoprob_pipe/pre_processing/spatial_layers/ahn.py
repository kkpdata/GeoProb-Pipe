from __future__ import annotations
from typing import TYPE_CHECKING
from InquirerPy import inquirer
import sys
from geoprob_pipe.utils.validation_messages import BColors

import os
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings


def added_ahn(app_settings: ApplicationSettings, display_added_msg: bool = False) -> bool:
    # TODO Later Should Middel: Should validate if AHN grid fully overlaps area
    exists = os.path.exists(app_settings.ahn_filepath)

    if exists and display_added_msg:
        print(BColors.OKBLUE, f"✔  AHN-grid al toegevoegd.", BColors.ENDC)
        return True
    if exists and display_added_msg:
        return True

    return False


def request_ahn(app_settings: ApplicationSettings):

    choices_list = ["Ik heb het nu toegevoegd", "Applicatie afsluiten"]
    choice = inquirer.select(
        message=f"Voeg s.v.p. het AHN-grid toe aan de onderstaande map en met deze bestandsnaam. \n"
                f"{app_settings.ahn_filepath}",
        choices=choices_list,
        default=choices_list[0],
    ).execute()

    if choice == choices_list[0]:

        while not os.path.exists(app_settings.ahn_filepath):

            inquirer.select(
                message=f"Voeg s.v.p. het AHN-grid toe aan de map.",
                choices=choices_list,
                default=choices_list[0],
            ).execute()
        print(BColors.OKBLUE, f"✅  AHN-bestand toegevoegd.", BColors.ENDC)
        return True

    elif choice == choices_list[1]:
        sys.exit(f"Applicatie is nu afgesloten.")
    else:
        raise ValueError
