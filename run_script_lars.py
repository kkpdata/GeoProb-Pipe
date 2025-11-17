# Stap 1

# Stap 1 is het bij elkaar verzamelen van de invoer met het onderstaande commando.
# python -m geoprob_pipe.pre_processing.cmd startup_geoprob_pipe


# Stap 2
# Stap 2 is het uitvoeren van de berekeningen met het bestand wat uit stap 1 volgt.
# Voer dit bestand
#  - conda omgeving te activeren
#  - cd naar de juiste map
#  - het commando: python run_script_lars.py


from geoprob_pipe import GeoProbPipe
import os
from geoprob_pipe.pre_processing.cmd import ApplicationSettings

app_settings = ApplicationSettings()

filepath = r"AANPASSEN\NAAR\JOU\PAD\Deest_BovenLeeuwen_Test.geoprob_pipe.gpkg"
app_settings.workspace_dir = os.path.dirname(filepath)
app_settings.geopackage_filename = os.path.basename(filepath)

geoprob_pipe = GeoProbPipe(app_settings)
geoprob_pipe.export_archive()
