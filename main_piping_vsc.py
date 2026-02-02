# %%
""" The below code displays an example of how GeoProb-Pipe is run.
This example works inside the repository. Use the project-object
directly outside the repository. """
from geoprob_pipe import GeoProbPipe
import os
from geoprob_pipe.questionnaire.cmd import ApplicationSettings

if __name__ == "__main__":
    app_settings = ApplicationSettings()
    filepath = r"tests\systeem_testen\224\Traject224_MORIA_WBN_prob.geoprob_pipe.gpkg"
    app_settings.workspace_dir = os.path.dirname(filepath)
    app_settings.geopackage_filename = os.path.basename(filepath)
    geoprob_pipe = GeoProbPipe(app_settings)
    geoprob_pipe.export_archive()
