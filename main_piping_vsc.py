""" The below code displays an example of how GeoProb-Pipe is run. This example works inside the repository. Use the
Project-object directly outside the repository. """
import sys 
#add the "scr" directory to the system path
repo_root = r"C:\Github\Project_GeoProb_Pipe\GeoProb-Pipe"
sys.path.append(repo_root) 

from geoprob_pipe import GeoProbPipe
from geoprob_pipe.utils.loggers import initiate_app_logger
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
# project.visualizations.export_visualizations()

# TODO Nu Should Klein: Exporteer ook validation messages van project.
# TODO Nu Should Middel: Exporteer ook resultaten naar shape files.

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
from pandas import merge
from geoprob_pipe.misc.traject_normering import TrajectNormering
import plotly.graph_objects as go
# plt.ioff()
export = True  # Set to False to not export the graph
# Collect data
df_uittredepunten = project.input_data.uittredepunten.df
df_results_combined = project.results.df_beta_scenarios
df_for_graph = merge(
    left=df_results_combined[["uittredepunt_id", "beta"]],
    right=df_uittredepunten[["uittredepunt_id", "M_value"]],
    on="uittredepunt_id",
    how="left"
)
traject_normering = TrajectNormering()  # TODO: Gebruikt nu dummy data: traject Elden-Heteren
cg = traject_normering.beta_categorie_grenzen

# plotly plot
fig=go.Figure()
fig.add_trace(
    go.Scatter(
        x=df_for_graph['M_value'],
        y=df_for_graph["beta"],
        mode='markers',
        marker=dict(symbol='circle', size=3, color='black'),
        name='Beta Scenarios',
        showlegend=True
    )
)

fig.add_trace(go.Scatter(
    x=[0, 100000, 100000, 0],
    y=[cg["I"][0], cg["I"][0], cg["I"][1], cg["I"][1]],
    mode='lines',
    line=dict(color='black', width=1),
    fill='toself',
    fillcolor='rgba(0, 255, 0, 0.5)',
    name='I'
    ))
fig.add_trace(go.Scatter(
    x=[0, 100000, 100000, 0],
    y=[cg["II"][0], cg["II"][0], cg["II"][1], cg["II"][1]],
    mode='lines',
    line=dict(color='black', width=1),
    fill='toself',
    fillcolor='rgba(144, 238, 144, 0.5)',
    name='II'
))
fig.add_trace(go.Scatter(
    x=[0, 100000, 100000, 0],
    y=[cg["III"][0], cg["III"][0], cg["III"][1], cg["III"][1]],
    mode='lines',
    line=dict(color='black', width=1),
    fill='toself',
    fillcolor='rgba(255, 255, 0, 0.5)',
    name='III' 
))
fig.add_trace(go.Scatter(
    x=[0, 100000, 100000, 0],
    y=[cg["IV"][0], cg["IV"][0], cg["IV"][1], cg["IV"][1]],
    mode='lines',
    line=dict(color='black', width=1),
    fill='toself',
    fillcolor='rgba(255, 165, 0, 0.5)',
    name='IV'
))
fig.add_trace(go.Scatter(
    x=[0, 100000, 100000, 0],
    y=[cg["V"][0], cg["V"][0], cg["V"][1], cg["V"][1]],
    mode='lines',
    line=dict(color='black', width=1),
    fill='toself',
    fillcolor='rgba(255, 0, 0, 0.5)',
    name='V'
))
fig.add_trace(go.Scatter(
    x=[0, 100000, 100000, 0],
    y=[cg["VI"][0], cg["VI"][0], cg["VI"][1], cg["VI"][1]],
    mode='lines',
    line=dict(color='black', width=1),
    fill='toself',
    fillcolor='rgba(128, 0, 128, 0.5)',
    name='VI'
))


fig.update_layout(
    title=f"Betrouwbaarheidsindex STPH scenarioberekeningen",
    xaxis=dict(title=f"Metrering",
                type='linear',
                range=[df_for_graph['M_value'].min()-10, df_for_graph['M_value'].max()+10],
                showgrid=True,
                gridwidth=0.5,
                gridcolor="gray"
                ),
    yaxis=dict(title=f"Betrouwbaarheidsindex β [-]",
                type='linear',
                range=[2, 15],
                showgrid=True,
                gridwidth=0.5,
                gridcolor="gray",
                minor=dict(
                    showgrid=True,
                    dtick=1
                )
                )
)

# ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=False))
# ax.ticklabel_format(style='plain', axis='y')
# ax.set_yticks([2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20])
# ax.set_xlim(df_for_graph['M_value'].min()-10, df_for_graph['M_value'].max()+10)
# TODO Nu Must Klein: Pas dijkpaal codering op x-as toe. Heb op dit moment niet deze gekoppeld aan de measure.

# # Categorie kleuren
# cg = traject_normering.beta_categorie_grenzen
# ax.fill_between(
#     [0, 100000], [cg["I"][0], cg["I"][0]], [cg["I"][1], cg["I"][1]],
#     color='green', alpha=0.5, label='I'
# )
# ax.fill_between(
#     [0, 100000],[cg["II"][0], cg["II"][0]],[cg["II"][1], cg["II"][1]],
#     color='lightgreen', alpha=0.5, label='II')
# ax.fill_between(
#     [0, 100000],[cg["III"][0], cg["III"][0]],[cg["III"][1], cg["III"][1]],
#     color='yellow', alpha=0.5, label='III')
# ax.fill_between(
#     [0, 100000],[cg["IV"][0], cg["IV"][0]],[cg["IV"][1], cg["IV"][1]],
#     color='orange', alpha=0.5, label='IV')
# ax.fill_between(
#     [0, 100000],[cg["V"][0], cg["V"][0]],[cg["V"][1], cg["V"][1]],
#     color='red', alpha=0.5, label='V')
# ax.fill_between(
#     [0, 100000],[cg["VI"][0], cg["VI"][0]],[cg["VI"][1], cg["VI"][1]],
#     color='purple', alpha=0.5, label='VI')
# TODO Nu Must klein: Dit zijn niet de officiële categoriekleuren. Aanpassen.
# TODO Nu Must klein: De fills lijken een kleine overlap te hebben waardoor het lijkt alsof er een border is.

# Categorie grens lijnen
# ax.axhline(cg["I"][0], color='black', linewidth=1)
# ax.axhline(cg["II"][0], color='black', linewidth=1)
# ax.axhline(cg["III"][0], color='black', linewidth=1)
# ax.axhline(cg["IV"][0], color='black', linewidth=1)
# ax.axhline(cg["V"][0], color='black', linewidth=1)

# Plot normering
# m_max = df_for_graph['M_value'].max()
# m_diff = m_max - df_for_graph['M_value'].min()
# m_spacing = m_diff * 0.02
# ax.text(
#     m_max + m_spacing, cg["I"][0], '$β_{eis;sig;dsn / 30}$',
#     fontsize=15, verticalalignment='center', horizontalalignment='left')
# ax.text(
#     m_max + m_spacing, cg["II"][0], '$β_{eis;sig;dsn}$',
#     fontsize=15, verticalalignment='center', horizontalalignment='left')
# ax.text(
#     m_max + m_spacing, cg["III"][0], '$β_{eis;ond;dsn}$',
#     fontsize=15, verticalalignment='center', horizontalalignment='left')
# ax.text(
#     m_max + m_spacing, cg["IV"][0], '$β_{eis;ond}$',
#     fontsize=15, verticalalignment='center', horizontalalignment='left')
# ax.text(
#     m_max + m_spacing, cg["V"][0], '$β_{eis;ond * 30}$',
#     fontsize=15, verticalalignment='center', horizontalalignment='left')

if export:
    fig.write_image(os.path.join(project.visualizations.graphs.export_dir, f"beta_scenarios.png"), format="png")
    fig.write_html(os.path.join(project.visualizations.graphs.export_dir, f"beta_scenarios.html"))
# %%
