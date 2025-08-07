from __future__ import annotations
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def hfreq_graphs_per_location(geoprob_pipe: GeoProbPipe, export: bool = True) -> List[plt.Figure]:
    """ Grafiek van de overschrijdingsfrequentielijn van de waterstand per HydraNL uitvoerpunt. """

    # TODO Later Should Middel: Visualiseer WBN waterstand in hfreq-plot ter bewustzijn. 
    # TODO Later Nice Middel: Visualiseer physical design point value in hfreq-plot ter bewustzijn.

    export_dir = os.path.join(geoprob_pipe.visualizations.graphs.export_dir, "grafiek_hfreq")
    os.makedirs(export_dir, exist_ok=True)
    figures = []
    df_uittredepunten = geoprob_pipe.input_data.uittredepunten.df
    for hydra_nl_name in geoprob_pipe.input_data.overschrijdingsfrequentielijnen.keys():
        
        # Collect data for the graph
        hfreq = geoprob_pipe.input_data.overschrijdingsfrequentielijnen[hydra_nl_name]
        levels = hfreq.overschrijdingsfrequentielijn.level
        freq =  hfreq.overschrijdingsfrequentielijn.exceedance_frequency
        uittredepunten = list(df_uittredepunten[df_uittredepunten['hydra_locatie_id'] == hydra_nl_name]['uittredepunt_id'])

        # Create the graph
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=levels,
            y=freq,
            mode='lines+markers',
            name='Overschrijdingsfrequentie',
            line= dict(dash='dash', color='blue', width=1),
            marker=dict(symbol='circle', size=1, color='blue')
        ))
        fig.update_layout(
            title=f"HydraNL locatie: {hydra_nl_name}<br>behorend bij uittredepunten: {', '.join([str(u) for u in uittredepunten])}",
            xaxis=dict(title=f"Waterstand (m+NAP)", 
            type='linear',
            showgrid=True, 
            gridwidth=0.5, 
            gridcolor="gray"
            ),
            yaxis=dict(title=f"Overschrijdingsfrequentie (log-schaal)", 
            type='log', 
            showgrid=True, 
            gridwidth=0.5, 
            gridcolor="gray",
            minor=dict(showgrid=True)
            )
            )
        figures.append(fig)

        # Export or not?
        if export:
            fig.write_html(os.path.join(export_dir, f"{hydra_nl_name}_hfreq.html"))
            fig.write_image(os.path.join(export_dir, f"{hydra_nl_name}_hfreq.png"), format="png")

    return figures


def hfreq_graph_in_single_interactive(geoprob_pipe: GeoProbPipe, export: bool = True):

    export_dir = os.path.join(geoprob_pipe.visualizations.graphs.export_dir, "grafiek_hfreq")
    os.makedirs(export_dir, exist_ok=True)
    df_uittredepunten = geoprob_pipe.input_data.uittredepunten.df
    fig = go.Figure()
    for index, hydra_nl_name in enumerate(geoprob_pipe.input_data.overschrijdingsfrequentielijnen.keys()):
        # Collect data for the graph
        hfreq = geoprob_pipe.input_data.overschrijdingsfrequentielijnen[hydra_nl_name]
        levels = hfreq.overschrijdingsfrequentielijn.level
        freq = hfreq.overschrijdingsfrequentielijn.exceedance_frequency
        uittredepunten = list(
            df_uittredepunten[df_uittredepunten['hydra_locatie_id'] == hydra_nl_name]['uittredepunt_id'])

        visible = 'legendonly'
        if index == 0:
            visible = True

        # Create the graph
        fig.add_trace(go.Scatter(
            x=levels,
            y=freq,
            mode='lines+markers',
            name=f"{hydra_nl_name}<br>"
                 f"uittredepunten: {', '.join([str(u) for u in uittredepunten])}",
            visible=visible,
            line=dict(dash='dash', color='blue', width=1),
            marker=dict(symbol='circle', size=1, color='blue'),
            showlegend=True,
        ))

    fig.update_layout(
        title=f"Overschrijdingsfrequentielijnen voor alle HydraNL locaties in dit traject",
        xaxis=dict(title=f"Waterstand (m+NAP)",
                   type='linear',
                   showgrid=True,
                   gridwidth=0.5,
                   gridcolor="gray"
                   ),
        yaxis=dict(title=f"Overschrijdingsfrequentie (log-schaal)",
                   type='log',
                   showgrid=True,
                   tickformat=".0e",  # TODO: Not satisfied about gridlines and ticks
                   gridwidth=0.5,
                   gridcolor="gray",
                   minor=dict(
                       showgrid=True,
                       dtick=1
                   )
                   )
    )

    # Export or not?
    if export:
        fig.write_html(os.path.join(export_dir, f"hfreq.html"))
        fig.write_image(os.path.join(export_dir, f"hfreq.png"), format="png")
