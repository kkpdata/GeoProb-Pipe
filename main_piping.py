""" The below code displays an example of how GeoProb-Pipe is run. This example works inside the repository. Use the
Project-object directly outside the repository. """
from repo_utils.utils import repository_root_path
from geoprob_pipe import GeoProbPipe
from dotenv import load_dotenv
import os


# Import environment variables
repo_root = repository_root_path()
load_dotenv(os.path.join(repo_root, "geoprob_pipe.ini"))


# Initiate GeoProb-Pipe project object
geoprob_pipe = GeoProbPipe(os.getenv("PATH_WORKSPACE"))
geoprob_pipe.export_archive()

