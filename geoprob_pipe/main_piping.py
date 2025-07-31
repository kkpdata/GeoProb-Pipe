""" The below code displays an example of how GeoProb-Pipe is run. This example works inside the repository. Use the
Project-object directly outside the repository. """
import sys 
import os 
#add the "scr" directory to the system path 
repo_root = r"C:\Github\Project_GeoProb_Pipe\GeoProb-Pipe"
sys.path.append(repo_root) 

from geoprob_pipe import GeoProbPipe
from geoprob_pipe.utils.other import repository_root_path
from geoprob_pipe.utils.loggers import initiate_app_logger
# from geoprob_pipe.classes.reliability_calculation import CombinedReliabilityCalculation
from dotenv import load_dotenv
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)  # Preferably address FutureWarnings: part of pydra-core
# Import environment variables
# repo_root = repository_root_path()
# print(repo_root)
load_dotenv(os.path.join(repo_root, "geoprob_pipe.ini"))

# Initiate logger
initiate_app_logger(repo_root=repo_root)

# Initiate GeoProb-Pipe project object
project = GeoProbPipe(os.getenv("PATH_WORKSPACE"))
project.results.export_results()
project.visualizations.export_visualizations()


#%%

# import os
# import matplotlib.pyplot as plt
# from matplotlib.pyplot import Figure
# from pandas import merge
# from matplotlib.ticker import ScalarFormatter
# from geoprob_pipe.misc.traject_normering import TrajectNormering


# geoprob_pipe = project

# gevonden_locaties = []

# export_dir = os.path.join(geoprob_pipe.visualizations.graphs.export_dir, "grafiek_hfreq")
# os.makedirs(export_dir, exist_ok=True)

# df_uitredepunten = geoprob_pipe.input_data.uittredepunten.df
# for hydra_nl_name in geoprob_pipe.input_data.overschrijdingsfrequentielijnen.keys():
#     hfreq = geoprob_pipe.input_data.overschrijdingsfrequentielijnen[hydra_nl_name]
#     levels = hfreq.overschrijdingsfrequentielijn.level
#     freq =  hfreq.overschrijdingsfrequentielijn.exceedance_frequency
#     uittredepunten = list(df_uitredepunten[df_uitredepunten['hydra_locatie_id'] == hydra_nl_name]['uittredepunt_id'])
#     plt.figure(figsize=(8, 5))
#     plt.plot(levels, freq, marker='o', linestyle='-', color='blue',markersize=1)
#     plt.xscale('linear')  # belasting vaak lineair
#     plt.yscale('log')     # faalkans logaritmisch
#     plt.xlabel("Waterstand (m+NAP)")
#     plt.ylabel("Overschrijdingsfrequentie (log-schaal)")
#     plt.title("HydraNL locatie: " + hydra_nl_name + "\nbehorend bij uittredepunten: " + ", ".join([str(u) for u in uittredepunten]))
#     plt.grid(True, which="both", linestyle='--', linewidth=0.5)
#     plt.tight_layout()
#     export_path = os.path.join(export_dir, f"{hydra_nl_name}_hfreq.png")
#     plt.savefig(export_path)


# TODO Nu Should Klein: Exporteer ook validation messages van project.
# TODO Nu Should Middel: Exporteer ook resultaten naar shape files.


##
#
# import threading
# import time
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from uuid import uuid4
#
#
# class Calculation:
#
#     def __init__(self, sect, pnt):
#         self.id = uuid4().__str__()
#         self.section = sect
#         self.point = pnt
#         self.result: int = 0
#
#     def run(self):
#         self.result += 1
#
#
# def start_calculations(list_of_calculations: list[Calculation]):
#     total = len(list_of_calculations)
#     completed = 0
#     lock = threading.Lock()
#
#     def run_calculation(calculation: Calculation):
#         nonlocal completed
#         try:
#             calculation.run()
#         except Exception as e:
#             print(f"ERROR: Could not run calculation {calculation.id}: {e}")
#         finally:
#             with lock:
#                 completed += 1
#
#     def progress_reporter():
#         while True:
#             with lock:
#                 print(f" -> {completed}/{total} of calculations completed.")
#                 if completed >= total:
#                     break
#             time.sleep(15)
#
#     # Start the progress reporter in a background thread
#     reporter_thread = threading.Thread(target=progress_reporter)
#     reporter_thread.start()
#
#     # Run calculations in parallel
#     with ThreadPoolExecutor() as executor:
#         futures = [executor.submit(run_calculation, calc) for calc in list_of_calculations]
#         for _ in as_completed(futures):
#             pass  # Just to ensure all tasks complete
#
#     reporter_thread.join()

# %%
