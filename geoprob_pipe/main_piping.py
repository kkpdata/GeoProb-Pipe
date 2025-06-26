""" The below code displays an example of how GeoProb-Pipe is run. This example works inside the repository. Use the
Project-object directly outside the repository. """


from geoprob_pipe import Project
from geoprob_pipe.helper_functions.utils import repository_root_path
from geoprob_pipe.utils.loggers import initiate_app_logger
from dotenv import load_dotenv
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)  # Preferably address FutureWarnings: part of pydra-core


# Import environment variables
repo_root = repository_root_path()
load_dotenv(os.path.join(repo_root, "geoprob_pipe.ini"))

# Initiate logger
initiate_app_logger(repo_root=repo_root)

# Initiate GeoProb-Pipe project object
project = Project(os.getenv("PATH_WORKSPACE"))
