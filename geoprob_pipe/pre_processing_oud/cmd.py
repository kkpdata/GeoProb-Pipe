import typer
from rich.console import Console
import os
import platform
from rich.panel import Panel
from geoprob_pipe.pre_processing.questionnaire import start_pre_processing_questionnaire
from typing import Optional


app = typer.Typer(help="GeoProb-Pipe - CLI applicatie voor probabilistische piping berekeningen.")


class ApplicationSettings:

    workspace_dir: Optional[str] = None
    geopackage_filename: Optional[str] = None

    @property
    def geopackage_filepath(self) -> str:
        return os.path.join(self.workspace_dir, self.geopackage_filename)

    @property
    def hrd_dir(self):
        path_to_hrd_dir = os.path.join(self.workspace_dir, "hrd_files")
        os.makedirs(path_to_hrd_dir, exist_ok=True)
        return path_to_hrd_dir


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
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean nec tincidunt arcu. Sed risus metus, pharetra at mi sed, 
egestas suscipit quam. Ut sed tellus vel justo congue placerat id ac nunc. Suspendisse maximus, ex non lacinia 
vestibulum, nunc mauris tincidunt urna, nec consectetur sem nunc vel lectus. Vivamus auctor pellentesque mattis. Integer 
nec scelerisque urna. Aenean sit amet nunc auctor mauris facilisis aliquet. Donec facilisis ipsum in felis sollicitudin 
mattis.
        """,
        title="GeoProb-Pipe".upper(),
        title_align="left",
        border_style="bright_blue",
        padding=(0, 2),
    ))

    start_pre_processing_questionnaire(ApplicationSettings())


if __name__ == "__main__":
    startup_geoprob_pipe()
