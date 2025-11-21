import typer
from rich.console import Console
import os
import platform
from datetime import datetime
from rich.panel import Panel
from geoprob_pipe.questionnaire.questionnaire import start_questionnaire
from typing import Optional, List


app = typer.Typer(help="GeoProb-Pipe - CLI applicatie voor probabilistische piping berekeningen.")


class ApplicationSettings:

    workspace_dir: Optional[str] = None
    geopackage_filename: Optional[str] = None
    datetime_stamp: str = datetime.now().strftime("%Y-%m-%d_%H%M")
    to_run = "all"
    # -> or vakken:1,2,3,4,5

    @property
    def geopackage_filepath(self) -> str:
        return os.path.join(self.workspace_dir, self.geopackage_filename)

    @property
    def hrd_dir(self):
        path_to_hrd_dir = os.path.join(self.workspace_dir, "hrd_files")
        os.makedirs(path_to_hrd_dir, exist_ok=True)
        return path_to_hrd_dir

    @property
    def hrd_file_path(self) -> str:
        for file in os.listdir(self.hrd_dir):
            filename = os.fsdecode(file)
            if filename.endswith(".config.sqlite"):
                continue
            if filename.endswith("hlcd.sqlite"):
                continue
            return os.path.join(self.hrd_dir, filename)
        raise ValueError

    @property
    def ahn_filepath(self) -> str:
        return os.path.join(self.workspace_dir, "ahn", "ahn.tif")

    @property
    def to_run_vakken_ids(self) -> Optional[List[int]]:
        if self.to_run == "all":
            return None
        vak_ids_str: List[str] = self.to_run.replace("vakken:", "").split(sep=",")
        return [int(vak_id_str) for vak_id_str in vak_ids_str]


def clear_terminal():
    if platform.system() == "Windows":
        os.system("cls")
        return
    os.system("clear")


@app.command()
def startup_geoprob_pipe():
    """ Starts up the GeoProb-Pipe console application. """
    clear_terminal()

    console = Console()
    console.print(Panel(
        """
Welkom bij GeoProb-Pipe! Deze applicatie voert probabilistische pipingberekeningen uit met de uittredepuntenmethode en 
een geohydrologisch model naar keuze (zoals model4a). GeoProb-Pipe maakt gebruik van de probabilistische bibliotheek 
van Deltares, die onder de motorkap de PTK-tool aanstuurt. Met de onderstaande interactieve vragenmodule neemt 
GeoProb-Pipe je stap voor stap mee door het opzetten van de invoer en het uitvoeren van de berekeningen. 
""",
        title="GeoProb-Pipe".upper(),
        title_align="left",
        border_style="bright_blue",
        padding=(0, 2),
    ))

    start_questionnaire(ApplicationSettings())


if __name__ == "__main__":
    startup_geoprob_pipe()
