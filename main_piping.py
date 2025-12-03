""" The below code displays an example of how GeoProb-Pipe is run. This example works inside the repository. Use the
Project-object directly outside the repository. """
from repo_utils.utils import repository_root_path
from geoprob_pipe import GeoProbPipe
import os

# Import environment variables
repo_root = repository_root_path()
workspace_path = os.path.join(repo_root, "workspaces", "traject_224")

# Initiate GeoProb-Pipe project object
geoprob_pipe = GeoProbPipe(workspace_path)
geoprob_pipe.export_archive()
