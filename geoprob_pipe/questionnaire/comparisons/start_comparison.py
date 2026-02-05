from __future__ import annotations
# noinspection PyPep8Naming
from InquirerPy.prompts.input import InputPrompt as inq_text
import os
from geoprob_pipe.utils.validation_messages import BColors
from geoprob_pipe.questionnaire.comparisons import ComparisonCollector


def specify_dir_for_first_file():
    filepath: str = ""
    filepath_is_valid = False
    while filepath_is_valid is False:
        filepath: str = inq_text(
            message="Specificeer het volledige bestandspad naar het eerste .geoprob_pipe.gpkg-bestand.",
        ).execute()

        filepath = filepath.replace('"', '')

        if not filepath.endswith(".geoprob_pipe.gpkg"):
            print(BColors.WARNING,
                  f"Het bestand moet een .geoprob_pipe.gpkg-bestand zijn. Jouw invoer "
                  f"{os.path.basename(filepath)} eindigt niet op deze extensie.", BColors.ENDC)
            continue
        if not os.path.exists(filepath):
            print(BColors.WARNING, "Het opgegeven bestandspad bestaat niet.",
                  BColors.ENDC)
            continue

        filepath_is_valid = True

    return filepath


def specify_dir_for_second_file():
    filepath: str = ""
    filepath_is_valid = False
    while filepath_is_valid is False:
        filepath: str = inq_text(
            message="Specificeer het volledige bestandspad naar het tweede .geoprob_pipe.gpkg-bestand.",
        ).execute()

        filepath = filepath.replace('"', '')

        if not filepath.endswith(".geoprob_pipe.gpkg"):
            print(BColors.WARNING,
                  f"Het bestand moet een .geoprob_pipe.gpkg-bestand zijn. Jouw invoer "
                  f"{os.path.basename(filepath)} eindigt niet op deze extensie.", BColors.ENDC)
            continue
        if not os.path.exists(filepath):
            print(BColors.WARNING, "Het opgegeven bestandspad bestaat niet.",
                  BColors.ENDC)
            continue

        filepath_is_valid = True

    return filepath


def specify_dir_for_comparison():
    workspace_dir: str = ""
    workspace_dir_is_valid = False
    while workspace_dir_is_valid is False:
        workspace_dir: str = inq_text(
            message="Specificeer het volledige pad naar de map waar je"
            + " de export van de vergelijking wilt opslaan.",
        ).execute()
        workspace_dir = workspace_dir.replace('"', '')

        if not os.path.exists(workspace_dir):
            print(BColors.WARNING, "De opgegeven map bestaat niet.",
                  BColors.ENDC)
            continue
        if not os.path.isdir(workspace_dir):
            print(BColors.WARNING, "De opgegeven locatie is geen map.",
                  BColors.ENDC)
            continue

        workspace_dir_is_valid = True

    return workspace_dir


def run_comparison(filepath1, filepath2, export_dir):
    print(BColors.OKBLUE, "Vergelijking wordt uitgevoerd.", BColors.ENDC)
    comparison = ComparisonCollector(filepath1, filepath2, export_dir)
    comparison.create_and_export_figures()
    print(BColors.OKBLUE,
          f"Vergelijking voltooid en opgeslagen in {comparison.export_dir}.",
          BColors.ENDC)


def start_comparison():
    filepath1 = specify_dir_for_first_file()
    filepath2 = specify_dir_for_second_file()
    export_dir = specify_dir_for_comparison()
    run_comparison(filepath1, filepath2, export_dir)
