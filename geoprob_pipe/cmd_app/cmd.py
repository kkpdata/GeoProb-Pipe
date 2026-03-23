import typer
from rich.console import Console
import os
from geoprob_pipe.utils import clear_terminal
from datetime import datetime
from rich.panel import Panel
from geoprob_pipe.cmd_app.questionnaire import start_questionnaire
from typing import Optional, List
from geoprob_pipe.cmd_app.utils.misc import get_geoprob_pipe_version_number
from geoprob_pipe.utils.loggers import setup_base_logging


app = typer.Typer(help="GeoProb-Pipe - CLI applicatie voor probabilistische piping berekeningen.", add_completion=False)


class ApplicationSettings:

    def __init__(self):
        self.workspace_dir: Optional[str] = None
        self.geopackage_filename: Optional[str] = None
        self.datetime_stamp: str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.to_run = "all"
        # -> or vakken:1,2,3,4,5
        self.debug: bool = os.getenv("GEOPROB_DEBUG") == "1"

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


def startup_geoprob_pipe():
    """ Starts up the GeoProb-Pipe console application. """

    app_settings = ApplicationSettings()

    setup_base_logging()

    debug_label: str = ""
    if app_settings.debug:
        debug_label = f", DEBUG=TRUE"

    clear_terminal()
    console = Console()
    console.print(Panel(
        """
Welkom bij GeoProb-Pipe! Deze applicatie voert probabilistische pipingberekeningen uit met de uittredepuntenmethode en
een geohydrologisch model naar keuze (zoals model4a). GeoProb-Pipe maakt gebruik van de probabilistische bibliotheek
van Deltares, die onder de motorkap de PTK-tool aanstuurt. Met de onderstaande interactieve vragenmodule neemt
GeoProb-Pipe je stap voor stap mee door het opzetten van de invoer en het uitvoeren van de berekeningen.
""",
        title=f"GeoProb-Pipe ({get_geoprob_pipe_version_number()}{debug_label})".upper(),
        title_align="left",
        border_style="bright_blue",
        padding=(0, 2)))

    start_questionnaire(app_settings=app_settings)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """ Default entry point for `geoprob-pipe`. Runs when no subcommand is specified. """
    if ctx.invoked_subcommand is None:
        startup_geoprob_pipe()


@app.command()
def debug():
    """ Start GeoProb-Pipe in debug mode. """
    os.environ["GEOPROB_DEBUG"] = "1"
    startup_geoprob_pipe()
