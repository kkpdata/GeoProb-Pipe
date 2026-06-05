from __future__ import annotations

import sys
from typing import TYPE_CHECKING, List, Tuple

from InquirerPy.prompts.input import InputPrompt
from InquirerPy.prompts.list import ListPrompt

from geoprob_pipe import GeoProbPipe
from geoprob_pipe.utils.validation_messages import BColors

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def _convert_vak_ids_str_to_ints(input_str: str) -> Tuple[List[int], List[str]]:
    input_str = input_str.replace(" ", "")
    list_vak_ids_str = input_str.split(sep=",")

    list_vak_ids_int: List[int] = []
    unknown_inputs: List[str] = []
    for item in list_vak_ids_str:
        if "-" in item:
            try:
                left_bound = int(item.split(sep="-")[0])
            except ValueError:
                unknown_inputs.append(item)
                continue
            try:
                right_bound = int(item.split(sep="-")[1])
            except ValueError:
                unknown_inputs.append(item)
                continue
            ids = list(range(left_bound, right_bound+1))
            list_vak_ids_int.extend(ids)
        else:
            try:
                item_int = int(item)
            except ValueError:
                unknown_inputs.append(item)
                continue
            list_vak_ids_int.append(item_int)

    return list(set(list_vak_ids_int)), unknown_inputs

def request_vakken_to_run() -> str:
    while True:
        vakken_input: str = InputPrompt(
            message="Specificeer welke vakken je wilt doorrekenen. Doe dit door comma-separated de vak nummers (id) "
                    "op te geven. Bijvoorbeeld '4,5,6,7,10-15'.",
        ).execute()

        # Convert string input to integer values
        list_vak_ids_int, unknown_inputs = _convert_vak_ids_str_to_ints(input_str=vakken_input)
        if unknown_inputs.__len__() > 0:
            print(f"{BColors.WARNING}De applicatie heeft enkele niet valide items in je invoer geconstateerd. "
                  f"Pas deze aan. Je invoer is '{vakken_input}'. De niet valide items zijn '{unknown_inputs}'."
                  f"{BColors.ENDC}")
            continue

        # Assure more than one valid vak id is given
        if list_vak_ids_int.__len__() == 0:
            print(f"{BColors.WARNING}Er zijn geen vak identificatie nummers opgegeven. Je invoer is '{vakken_input}'. "
                  f"Probeer opnieuw.{BColors.ENDC}")
            continue

        break

    return f"vakken:{','.join([str(item) for item in list_vak_ids_int])}"


def run_calculations(app_settings: ApplicationSettings) -> bool:
    choices_list = [
        "Ja, alles",
        "Ja, specifieke vakken",
        "Nee (applicatie sluit af)"
    ]
    choice = ListPrompt(
        message="Wil je de berekeningen uitvoeren? \n"
                "Let op: Indien je al rekenresultaten hebt, zullen deze verwijderd worden, alvorens de nieuwe "
                "resultaten worden opgeslagen. ", choices=choices_list, default=choices_list[0],
    ).execute()

    if choice == choices_list[0]:
        geoprob_pipe = GeoProbPipe(app_settings)
        geoprob_pipe.export_archive()
        print(BColors.OKBLUE, "✅  Berekeningen zijn uitgevoerd.", BColors.ENDC)
    elif choice == choices_list[1]:
        vakken_str: str = request_vakken_to_run()
        app_settings.to_run = vakken_str
        geoprob_pipe = GeoProbPipe(app_settings)
        geoprob_pipe.export_archive()
        print(BColors.OKBLUE, f"✅  Berekeningen zijn uitgevoerd, voor vakken "
                              f"{app_settings.to_run.replace("vakken:", "")}.", BColors.ENDC)
    elif choice == choices_list[2]:
        sys.exit("Applicatie is afgesloten.")
    else:
        raise ValueError
    return True
