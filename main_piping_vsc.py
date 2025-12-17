# %%
""" The below code displays an example of how GeoProb-Pipe is run. This example works inside the repository. Use the
Project-object directly outside the repository. """
from geoprob_pipe import GeoProbPipe
import os
from geoprob_pipe.questionnaire.cmd import ApplicationSettings

app_settings = ApplicationSettings()

filepath = r"C:\Users\vinji\Python\geoprob_pipe\Analyse_20-2\Analyse_20-2.geoprob_pipe.gpkg"
app_settings.workspace_dir = os.path.dirname(filepath)
app_settings.geopackage_filename = os.path.basename(filepath)

geoprob_pipe = GeoProbPipe(app_settings)
geoprob_pipe.export_archive()
