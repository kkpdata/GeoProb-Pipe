from __future__ import annotations
import os
import matplotlib.pyplot as plt
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def export_hfreq_graphs(geoprob_pipe: GeoProbPipe):
    """Grafiek van de overschrijdingsfrequentielijn van de waterstand per HydraNL uitvoerpunt"""

    export_dir = os.path.join(geoprob_pipe.visualizations.graphs.export_dir, "grafiek_hfreq")
    os.makedirs(export_dir, exist_ok=True)

    df_uittredepunten = geoprob_pipe.input_data.uittredepunten.df
    for hydra_nl_name in geoprob_pipe.input_data.overschrijdingsfrequentielijnen.keys():
        hfreq = geoprob_pipe.input_data.overschrijdingsfrequentielijnen[hydra_nl_name]
        levels = hfreq.overschrijdingsfrequentielijn.level
        freq =  hfreq.overschrijdingsfrequentielijn.exceedance_frequency
        uittredepunten = list(df_uittredepunten[df_uittredepunten['hydra_locatie_id'] == hydra_nl_name]['uittredepunt_id'])
        plt.ioff()
        plt.figure(figsize=(8, 5))
        plt.plot(levels, freq, marker='o', linestyle='-', color='blue',markersize=1)
        plt.xscale('linear')  # belasting vaak lineair
        plt.yscale('log')     # faalkans logaritmisch
        plt.xlabel("Waterstand (m+NAP)")
        plt.ylabel("Overschrijdingsfrequentie (log-schaal)")
        plt.title("HydraNL locatie: " + hydra_nl_name + "\nbehorend bij uittredepunten: " + ", ".join([str(u) for u in uittredepunten]))
        plt.grid(True, which="both", linestyle='--', linewidth=0.5)
        plt.tight_layout()
        export_path = os.path.join(export_dir, f"{hydra_nl_name}_hfreq.png")
        plt.savefig(export_path)
