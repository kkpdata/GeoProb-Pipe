""" The below code displays an example of how GeoProb-Pipe is run. This example works inside the repository. Use the
Project-object directly outside the repository. """
import sys 
#add the "scr" directory to the system path
repo_root = r"C:\Users\vinji\Python\GEOprob-Pipe\GeoProb-Pipe"
sys.path.append(repo_root) 

from geoprob_pipe import GeoProbPipe
from dotenv import load_dotenv
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)  # Preferably address FutureWarnings: part of pydra-core

# Import environment variables
load_dotenv(os.path.join(repo_root, "geoprob_pipe.ini"))


# Initiate GeoProb-Pipe project object
if __name__ == "__main__":
    geoprob_pipe = GeoProbPipe(os.getenv("PATH_WORKSPACE"))
    geoprob_pipe.export_archive()
