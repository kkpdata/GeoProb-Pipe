from __future__ import annotations
import os
import matplotlib.pyplot as plt
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def hfreq_graphs(geoprob_pipe: GeoProbPipe, export: bool = True) -> List[plt.Figure]:
    """Grafiek van de overschrijdingsfrequentielijn van de waterstand per HydraNL uitvoerpunt"""
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
        plt.ioff()
        fig = plt.figure(figsize=(8, 5))
        fig.plot(levels, freq, marker='o', linestyle='-', color='blue',markersize=1)
        fig.xscale('linear')  # belasting vaak lineair
        fig.yscale('log')     # faalkans logaritmisch
        fig.xlabel("Waterstand (m+NAP)")
        fig.ylabel("Overschrijdingsfrequentie (log-schaal)")
        fig.title("HydraNL locatie: " + hydra_nl_name + "\nbehorend bij uittredepunten: " + ", ".join([str(u) for u in uittredepunten]))
        fig.grid(True, which="both", linestyle='--', linewidth=0.5)
        fig.tight_layout()
        figures.append(fig)

        # Export or not?
        export_path = os.path.join(export_dir, f"{hydra_nl_name}_hfreq.png")
        if export:
            plt.savefig(export_path)

    return figures
