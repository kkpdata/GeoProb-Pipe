from __future__ import annotations
import matplotlib.pyplot as plt
from matplotlib.pyplot import Figure
import pandas as pd
from pandas import merge
import numpy as np
import os
from matplotlib.ticker import ScalarFormatter
from geoprob_pipe.misc.traject_normering import TrajectNormering
import plotly.graph_objects as go
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def background_graph(geoprob_pipe: GeoProbPipe, fig: go.Figure, df_for_graph: pd.DataFrame) -> go.Figure:
    # Categorie kleuren
    cg = geoprob_pipe.input_data.traject_normering.beta_categorie_grenzen
    colors = ["rgba(0,128,0,0.4)", "rgba(144,238,144,0.4)", 
            "rgba(255,255,0,0.4)", "rgba(255,165,0,0.4)", 
            "rgba(255,0,0,0.4)", "rgba(128,0,128,0.4)"]
    labels = ["β<sub>eis;sig;dsn / 30</sub>", "β<sub>eis;sig;dsn</sub>", "β<sub>eis;ond;dsn</sub>",
            "β<sub>eis;ond</sub>", "β<sub>eis;ond * 30</sub>", ""]
    
    if "M_value" in df_for_graph.columns:
        x_line = np.linspace(df_for_graph['M_value'].min()-10, df_for_graph['M_value'].max()+10)
    else:
        x_line = np.linspace(df_for_graph['M_van'].min()-10, df_for_graph['M_tot'].max()+10)

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
            x=x_line.max(),
            y=np.log10(cg[grens][0]),
            text=labels[i % len(labels)],
            showarrow=False,
            xanchor="left",
            yanchor="middle",
            font=dict(color="black", size=10),
            align="right"
        )
                
    return fig


def beta_scenarios_graph(geoprob_pipe: GeoProbPipe, export: bool = True) -> go.Figure:
    """ Grafiek van de betrouwbaarheidsindex per scenario over de gecombineerde uitvoer (uplift/heave/piping). Over
    de x-as uitgezet tegen de dijkpaal nummering. Op de achtergrond zijn de categoriegrenzen weergegeven. """
   
    # Collect data
    df_uittredepunten = geoprob_pipe.input_data.uittredepunten.df
    df_results_combined = geoprob_pipe.results.df_beta_scenarios
    df_for_graph = merge(
        left=df_results_combined[["uittredepunt_id", "beta"]],
        right=df_uittredepunten[["uittredepunt_id", "M_value"]],
        on="uittredepunt_id",
        how="left"
    )

    # Plot data
    fig = go.Figure()
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

    # Background
    fig = background_graph(geoprob_pipe, fig, df_for_graph)
    
    # Layout
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
        
    return fig


def beta_uittredepunten_graph(geoprob_pipe: GeoProbPipe, export: bool = True) -> go.Figure:
    """ Grafiek van de betrouwbaarheidsindex per uittredepunt over de gecombineerde uitvoer (uplift/heave/piping). Over
    de x-as uitgezet tegen de dijkpaal nummering. Op de achtergrond zijn de categoriegrenzen weergegeven. """


    # Collect data
    df_uittredepunten_m = geoprob_pipe.input_data.uittredepunten.df
    df_results_uittredepunten = geoprob_pipe.results.df_beta_uittredepunten
    df_for_graph = merge(
        left=df_results_uittredepunten[["uittredepunt_id", "beta"]],
        right=df_uittredepunten_m[["uittredepunt_id", "M_value"]],
        on="uittredepunt_id",
        how="left"
    )
    # Plot data
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=df_for_graph['M_value'],
            y=df_for_graph["beta"],
            mode='markers',
            marker=dict(symbol='circle', size=3, color='black'),
            name='Beta Uittredepunten',
            showlegend=True
        )
    )

    # Background
    fig = background_graph(geoprob_pipe, fig, df_for_graph)
    
    # Layout
    fig.update_layout(
            title=f"Betrouwbaarheidsindex STPH per uittredepunt",
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
        fig.write_html(os.path.join(export_dir, f"beta_uittredepunten.html"), include_plotlyjs='cdn')
        if geoprob_pipe.software_requirements.chrome_is_installed:
            fig.write_image(os.path.join(export_dir, f"beta_uittredepunten.png"), format="png")
        
    return fig


def beta_vakken_graph(geoprob_pipe: GeoProbPipe, export: bool = True) -> go.Figure:
    """ Grafiek van de betrouwbaarheidsindex per uittredepunt over de gecombineerde uitvoer (uplift/heave/piping). Over
    de x-as uitgezet tegen de dijkpaal nummering. Op de achtergrond zijn de categoriegrenzen weergegeven. """

    # Collect data
    df_vakken = geoprob_pipe.input_data.vakken.df
    df_results_vakken = geoprob_pipe.results.df_beta_vakken
    df_for_graph = merge(
        left=df_results_vakken[["vak_id", "beta"]],
        right=df_vakken[["vak_id", "M_van", "M_tot"]],
        on="vak_id",
        how="left"
    )
    
    # Plot data
    fig = go.Figure()
    for index, row in df_for_graph.iterrows():
        fig.add_shape(type="line", 
                      x0=row["M_van"], x1=row["M_tot"],
                      y0=row["beta"], y1=row["beta"],
                      line=dict(color="black", width=2.5))
        
        fig.add_vline(x=row["M_van"])
        fig.add_vline(x=row["M_tot"])
        
        fig.add_annotation(
            x=(row["M_van"] + row["M_tot"]) / 2, y=np.log10(row["beta"]),
            text=f"Vak: {int(row["vak_id"]) + 1}<br>β = {row["beta"].round(3)}",
            showarrow=False,
            xanchor="center",
            yanchor="top",
            font=dict(color="black"))
    
    # Background
    fig = background_graph(geoprob_pipe, fig, df_for_graph)
        
    # Layout
    fig.update_layout(
            title=f"Betrouwbaarheidsindex STPH per vak",
            xaxis=dict(title=f"Metrering",
                    type='linear',
                    range=[df_for_graph['M_van'].min()-10, df_for_graph['M_tot'].max()+10],
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
        fig.write_html(os.path.join(export_dir, f"beta_vakken.html"), include_plotlyjs='cdn')
        if geoprob_pipe.software_requirements.chrome_is_installed:
            fig.write_image(os.path.join(export_dir, f"beta_vakken.png"), format="png")
        
    return fig