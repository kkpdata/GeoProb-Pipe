#%%
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
geoprob_pipe = GeoProbPipe(os.getenv("PATH_WORKSPACE"))
geoprob_pipe.export_archive()


#%% beta_scenario_graph

export=True

from pandas import merge
import plotly.graph_objects as go
import numpy as np

# Collect data
df_uittredepunten = geoprob_pipe.input_data.uittredepunten.df
df_results_combined = geoprob_pipe.results.df_beta_scenarios
df_for_graph = merge(
    left=df_results_combined[["uittredepunt_id", "beta"]],
    right=df_uittredepunten[["uittredepunt_id", "M_value"]],
    on="uittredepunt_id",
    how="left"
)

# Initial variables
naam = 'Betrouwbaarheidsindex'
fig = go.Figure()


# Plot data
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

# Catogorie kleuren
cg = geoprob_pipe.input_data.traject_normering.beta_categorie_grenzen
colors = ["rgba(0,128,0,0.4)", "rgba(144,238,144,0.4)", 
          "rgba(255,255,0,0.4)", "rgba(255,165,0,0.4)", 
          "rgba(255,0,0,0.4)", "rgba(128,0,128,0.4)"]
labels = ["β<sub>eis;sig;dsn / 30</sub>", "β<sub>eis;sig;dsn</sub>", "β<sub>eis;ond;dsn</sub>",
          "β<sub>eis;ond</sub>", "β<sub>eis;ond * 30</sub>", ""]

x_line = np.linspace(df_for_graph['M_value'].min()-10, df_for_graph['M_value'].max()+10)

for i, grens in enumerate(cg):

    if cg[grens][0] <=0:
        cg[grens][0] = np.log10(2)
        
    # Onderste lijn (zichtbaar)
    fig.add_trace(go.Scatter(
        x=x_line,
        y=[cg[grens][0]] * len(x_line),
        name=grens,
        mode="lines",
        line=dict(color="black", width=1.5),
        hoverinfo="skip",
        showlegend=False,
    ))
        
    # Bovenste lijn (onzichtbaar, zorgt voor fill)
    fig.add_trace(go.Scatter(
        x=x_line,
        y=[cg[grens][1]] * len(x_line),
        name=grens,
        mode="lines",
        line=dict(width=0),        # geen bovenrand zichtbaar
        fill="tonexty",
        fillcolor=colors[i % len(colors)],  # kleur uit lijst
        hoverinfo="skip",
        showlegend=False, 
    ))
    
    # Labels bij de ondergrens
    fig.add_annotation(
        x=df_for_graph['M_value'].max()+10,
        y=np.log10(cg[grens][0]),
        text=labels[i % len(labels)],
        showarrow=False,
        xanchor="left",
        yanchor="middle",
        font=dict(color="black", size=10),
        align="right"
    )
              

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
                   type='log',
                   range=[np.log10(2), np.log10(20)],
                   showgrid=True,
                   gridwidth=0.5,
                   gridcolor="gray",
                   minor=dict(
                       showgrid=True,
                       dtick=1
                   )
                   )
    )

# Export
if export:
    export_dir = geoprob_pipe.visualizations.graphs.export_dir
    os.makedirs(export_dir, exist_ok=True)
    fig.write_html(os.path.join(export_dir, f"beta_scenarios.html"), include_plotlyjs='cdn')
    if geoprob_pipe.software_requirements.chrome_is_installed:
        fig.write_image(os.path.join(export_dir, f"beta_scenarios.png"), format="png")
fig.show()
# %%
