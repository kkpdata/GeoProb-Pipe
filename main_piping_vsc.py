# %%
""" The below code displays an example of how GeoProb-Pipe is run.
This example works inside the repository. Use the project-object
directly outside the repository. """
from geoprob_pipe import GeoProbPipe
import os
import time
from geoprob_pipe.questionnaire.cmd import ApplicationSettings

app_settings = ApplicationSettings()
app_settings.to_run = "vakken:12,13,14"

filepath = r"C:\Users\vinji\Python\GEOprob-Pipe\Bestandenuitwisseling\Analyse16-1_V5.geoprob_pipe\Analyse16-1_V5.geoprob_pipe.gpkg"
# filepath = r"C:\Users\vinji\Python\GEOprob-Pipe\Bestandenuitwisseling\Analyse16-1_V5.geoprob_pipe\Analyse16-1_V5alt.geoprob_pipe.gpkg"
app_settings.workspace_dir = os.path.dirname(filepath)
app_settings.workspace_dir = os.path.dirname(filepath)
app_settings.geopackage_filename = os.path.basename(filepath)

geoprob_pipe = GeoProbPipe(app_settings)
geoprob_pipe.export_archive()
