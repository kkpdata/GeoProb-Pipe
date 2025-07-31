from __future__ import annotations
import matplotlib.pyplot as plt
from matplotlib.pyplot import Figure
from pandas import merge
from matplotlib.ticker import ScalarFormatter
from geoprob_pipe.misc.traject_normering import TrajectNormering
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe

def overschreidingsfrequentielijn(geoprob_pipe: GeoProbPipe) -> Figure:
    """Grafiek van de overschrijdingsfrequentielijn van de waterstand per HydraNL uitvoerpunt"""
    gevonden_locaties = []
    df_uitredepunten = geoprob_pipe.input_data.uittredepunten.df
    for hydra_nl_name in geoprob_pipe.input_data.overschrijdingsfrequentielijnen.keys():
        hfreq = geoprob_pipe.input_data.overschrijdingsfrequentielijnen[hydra_nl_name]
        uittredepunten = list(df_uitredepunten[df_uitredepunten['hydra_locatie_id'] == 'MA_1_41-4_dk_00004']['uittredepunt_id'])
    geoprob_pipe.input_data.uittredepunten.keys()



##% Oude code Ard-Jan
print("\nFragility Curve (CDF):")
    print(f"{'x':>20} {'P(failure)':>25}")
    print("-" * 50)
    for fc in sorted(project.variables["WS"].fragility_values, key=lambda f: f.x):
        print(f"{fc.x:20} {fc.probability_of_failure:25}")

    fragility_vals = sorted(project.variables["WS"].fragility_values, key=lambda f: f.x)
    x_vals = [fc.x for fc in fragility_vals]
    p_vals = [max(fc.probability_of_failure, 1e-10) for fc in fragility_vals]  # voorkom log(0)

    plt.figure(figsize=(8, 5))
    plt.plot(x_vals, p_vals, marker='o', linestyle='-', color='blue',markersize=1)
    plt.xscale('linear')  # belasting vaak lineair
    plt.yscale('log')     # faalkans logaritmisch
    plt.xlabel("Belasting (x)")
    plt.ylabel("Kans op falen (log-schaal)")
    plt.title("Fragility Curve (CDF)")
    plt.grid(True, which="both", linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()
