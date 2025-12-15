from __future__ import annotations
from InquirerPy import inquirer
from geoprob_pipe import GeoProbPipe
import sys
from geoprob_pipe.utils.validation_messages import BColors
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from geoprob_pipe.questionnaire.cmd import ApplicationSettings


def request_vakken_to_run() -> str:
    list_vak_nummers_int: List[int] = []
    vakken_input_is_valid = False
    while vakken_input_is_valid is False:
        vakken_input: str = inquirer.text(
            message="Specificeer welke vakken je wilt doorrekenen. Doe dit door comma-separated de vak nummers (id) "
                    "op te geven. Bijvoorbeeld '4,5,6,7'.",
        ).execute()

        # Convert to integers
        vakken_input = vakken_input.replace(" ", "")
        list_vak_nummers_str = vakken_input.split(sep=",")
        try:
            list_vak_nummers_int = [int(vak_id) for vak_id in list_vak_nummers_str]
        except ValueError:
            print(f"{BColors.WARNING}Het bestand moet of een geopackage, shapefile of geodatabase zijn. Jouw invoer "
                  f"eindigt op de extensie .{vakken_input.split(sep='.')[-1]}.{BColors.ENDC}")
            continue

        # Assure more than one vak id is given
        if list_vak_nummers_int.__len__() == 0:
            print(f"{BColors.WARNING}Het bestand moet of een geopackage, shapefile of geodatabase zijn. Jouw invoer "
                  f"eindigt op de extensie .{vakken_input.split(sep='.')[-1]}.{BColors.ENDC}")
            continue

        vakken_input_is_valid = True

    return f"vakken:{','.join([str(item) for item in list_vak_nummers_int])}"


def run_calculations(app_settings: ApplicationSettings) -> bool:
    choices_list = [
        "Ja, alles",
        "Ja, specifieke vakken",
        "Nee (applicatie sluit af)"
    ]
    choice = inquirer.select(
        message="Wil je de berekeningen uitvoeren? \n"
                "Let op: Indien je al rekenresultaten hebt, zullen deze verwijderd worden, alvorens de nieuwe "
                "resultaten worden opgeslagen. ", choices=choices_list, default=choices_list[0],
    ).execute()

    if choice == choices_list[0]:
        geoprob_pipe = GeoProbPipe(app_settings)
        geoprob_pipe.export_archive()
        print(BColors.OKBLUE, f"✅  Berekeningen zijn uitgevoerd.", BColors.ENDC)
    elif choice == choices_list[1]:
        vakken_str: str = request_vakken_to_run()
        app_settings.to_run = vakken_str
        geoprob_pipe = GeoProbPipe(app_settings)
        geoprob_pipe.export_archive()
        print(BColors.OKBLUE, f"✅  Berekeningen zijn uitgevoerd, voor vakken "
                              f"{app_settings.to_run.replace("vakken:", "")}.", BColors.ENDC)
    elif choice == choices_list[2]:
        sys.exit(f"Applicatie is afgesloten.")
    else:
        raise ValueError
    return True
