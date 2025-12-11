# %%
""" The below code displays an example of how GeoProb-Pipe is run.
This example works inside the repository. Use the project-object
directly outside the repository. """
from geoprob_pipe import GeoProbPipe
import os
import time
from geoprob_pipe.questionnaire.cmd import ApplicationSettings

app_settings = ApplicationSettings()

filepath = r"tests\systeem_testen\224\Traject224_MORIA_WBN_det_corr.geoprob_pipe.gpkg"
app_settings.workspace_dir = os.path.dirname(filepath)
app_settings.geopackage_filename = os.path.basename(filepath)

geoprob_pipe = GeoProbPipe(app_settings)
geoprob_pipe.visualizations.graphs.beta_scenarios().show()
# start_time = time.time()
# geoprob_pipe.export_archive()
# end_time = time.time()

# print(f"Time passed for export: {end_time - start_time:.2f} sec")
