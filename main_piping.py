""" The below code displays an example of how GeoProb-Pipe is run. This example works inside the repository. Use the
Project-object directly outside the repository. """
from repo_utils.utils import repository_root_path
from geoprob_pipe import GeoProbPipe
from dotenv import load_dotenv
import os
from probabilistic_library import Alpha

# Import environment variables
repo_root = repository_root_path()
load_dotenv(os.path.join(repo_root, "geoprob_pipe.ini"))

# Initiate GeoProb-Pipe project object
project = GeoProbPipe(os.getenv("PATH_WORKSPACE"))
project.export_archive()

##


# TODO Nu Should Klein: Exporteer ook validation messages van project.
# TODO Nu Should Middel: Exporteer ook resultaten naar shape files.
##

from geopandas import GeoDataFrame, points_from_xy

df_uittredepunten = project.input_data.uittredepunten.df
df_coords = df_uittredepunten[["uittredepunt_id", "uittredepunt_x_coord", "uittredepunt_y_coord"]]

df_beta_limit_states = project.results.df_beta_limit_states
df = df_beta_limit_states.merge(df_coords, left_on="uittredepunt_id", right_on="uittredepunt_id")

gdf = GeoDataFrame(
    df,
    geometry=points_from_xy(df['uittredepunt_x_coord'], df['uittredepunt_y_coord']),
    crs='EPSG:28992'
)
gdf = gdf.drop(columns=['uittredepunt_x_coord', 'uittredepunt_y_coord'])

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
