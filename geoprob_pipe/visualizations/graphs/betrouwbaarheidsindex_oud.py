from __future__ import annotations
import matplotlib.pyplot as plt
from matplotlib.pyplot import Figure
from pandas import merge
import os
from matplotlib.ticker import ScalarFormatter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def beta_scenarios_graph(geoprob_pipe: GeoProbPipe, export: bool = True) -> Figure:
    """ Grafiek van de betrouwbaarheidsindex per scenario over de gecombineerde uitvoer (uplift/heave/piping). Over
    de x-as uitgezet tegen de dijkpaal nummering. Op de achtergrond zijn de categoriegrenzen weergegeven. """

    # Collect data
    df_uittredepunten = geoprob_pipe.input_data.uittredepunten.df
    df_results_combined = geoprob_pipe.results.gdf_beta_scenarios
    df_for_graph = merge(
        left=df_results_combined[["uittredepunt_id", "beta"]],
        right=df_uittredepunten[["uittredepunt_id", "M_value"]],
        on="uittredepunt_id",
        how="left"
    )

    # Initial variables
    naam = 'Betrouwbaarheidsindex'
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.5))

    # Plot data
    ax.plot(df_for_graph['M_value'], df_for_graph["beta"], 'o',
            color='black', markersize=3, label='Betrouwbaarheidsindex')

    # Formatting
    ax.grid(linewidth=0.5, color='black', alpha=0.5, linestyle='-.')

    ax.set_xlabel('Dijkpaal', fontsize=20, labelpad=15)  # TODO: Nu nog measure
    ax.set_ylabel(f"{naam} [-]", fontsize=20, labelpad=15)
    ax.legend(fontsize=15, loc=0)
    ax.set_title('Betrouwbaarheidsindex STPH scenarioberekeningen', fontsize=20)
    ax.set_ylim(2, 20)
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=False))
    ax.ticklabel_format(style='plain', axis='y')
    ax.set_yticks([2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20])
    ax.set_xlim(df_for_graph['M_value'].min() - 10, df_for_graph['M_value'].max() + 10)
    # TODO Nu Must Klein: Pas dijkpaal codering op x-as toe. Heb op dit moment niet deze gekoppeld aan de measure.

    # Categorie kleuren
    cg = geoprob_pipe.input_data.traject_normering.beta_categorie_grenzen
    ax.fill_between(
        [0, 100000], [cg["I"][0], cg["I"][0]], [cg["I"][1], cg["I"][1]],
        color='green', alpha=0.5, label='I'
    )
    ax.fill_between(
        [0, 100000], [cg["II"][0], cg["II"][0]], [cg["II"][1], cg["II"][1]],
        color='lightgreen', alpha=0.5, label='II')
    ax.fill_between(
        [0, 100000], [cg["III"][0], cg["III"][0]], [cg["III"][1], cg["III"][1]],
        color='yellow', alpha=0.5, label='III')
    ax.fill_between(
        [0, 100000], [cg["IV"][0], cg["IV"][0]], [cg["IV"][1], cg["IV"][1]],
        color='orange', alpha=0.5, label='IV')
    ax.fill_between(
        [0, 100000], [cg["V"][0], cg["V"][0]], [cg["V"][1], cg["V"][1]],
        color='red', alpha=0.5, label='V')
    ax.fill_between(
        [0, 100000], [cg["VI"][0], cg["VI"][0]], [cg["VI"][1], cg["VI"][1]],
        color='purple', alpha=0.5, label='VI')
    # TODO Nu Must klein: Dit zijn niet de officiële categoriekleuren. Aanpassen.
    # TODO Nu Must klein: De fills lijken een kleine overlap te hebben waardoor het lijkt alsof er een border is.

    # Categorie grens lijnen
    ax.axhline(cg["I"][0], color='black', linewidth=1)
    ax.axhline(cg["II"][0], color='black', linewidth=1)
    ax.axhline(cg["III"][0], color='black', linewidth=1)
    ax.axhline(cg["IV"][0], color='black', linewidth=1)
    ax.axhline(cg["V"][0], color='black', linewidth=1)

    # Plot vakken
    for index, row in geoprob_pipe.input_data.vakken.df.iterrows():
        ax.axvline(x=row['M_van'], color='black', linewidth=1)
        m_center = row['M_van'] + (row['M_tot'] - row['M_van']) / 2
        ax.text(x=m_center, y=2.25, s=f"Vak {row['vak_id']}",
                fontsize=15, verticalalignment='center', horizontalalignment='center')

    # Plot normering
    m_max = df_for_graph['M_value'].max()
    m_diff = m_max - df_for_graph['M_value'].min()
    m_spacing = m_diff * 0.02
    ax.text(
        m_max + m_spacing, cg["I"][0], '$β_{eis;sig;dsn / 30}$',
        fontsize=15, verticalalignment='center', horizontalalignment='left')
    ax.text(
        m_max + m_spacing, cg["II"][0], '$β_{eis;sig;dsn}$',
        fontsize=15, verticalalignment='center', horizontalalignment='left')
    ax.text(
        m_max + m_spacing, cg["III"][0], '$β_{eis;ond;dsn}$',
        fontsize=15, verticalalignment='center', horizontalalignment='left')
    ax.text(
        m_max + m_spacing, cg["IV"][0], '$β_{eis;ond}$',
        fontsize=15, verticalalignment='center', horizontalalignment='left')
    ax.text(
        m_max + m_spacing, cg["V"][0], '$β_{eis;ond * 30}$',
        fontsize=15, verticalalignment='center', horizontalalignment='left')
    export_path = os.path.join(geoprob_pipe.visualizations.graphs.export_dir, f"beta_scenarios.png")

    if export:
        fig.savefig(export_path, dpi=300)

    return fig


def beta_uittredepunten_graph(geoprob_pipe: GeoProbPipe, export: bool = True) -> Figure:
    """ Grafiek van de betrouwbaarheidsindex per uittredepunt over de gecombineerde uitvoer (uplift/heave/piping). Over
    de x-as uitgezet tegen de dijkpaal nummering. Op de achtergrond zijn de categoriegrenzen weergegeven. """

    # Collect data
    df_uittredepunten_m = geoprob_pipe.input_data.uittredepunten.df
    gdf_results_uittredepunten = geoprob_pipe.results.gdf_beta_uittredepunten
    df_for_graph = merge(
        left=gdf_results_uittredepunten[["uittredepunt_id", "beta"]],
        right=df_uittredepunten_m[["uittredepunt_id", "M_value"]],
        on="uittredepunt_id",
        how="left"
    )

    # Initial variables
    naam = 'Betrouwbaarheidsindex'
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.5))

    # Plot data
    ax.plot(df_for_graph['M_value'], df_for_graph["beta"], 'o',
            color='black', markersize=3, label='Betrouwbaarheidsindex')

    # Formatting
    ax.grid(linewidth=0.5, color='black', alpha=0.5, linestyle='-.')

    ax.set_xlabel('Dijkpaal', fontsize=20, labelpad=15)  # TODO: Nu nog measure
    ax.set_ylabel(f"{naam} [-]", fontsize=20, labelpad=15)
    ax.legend(fontsize=15, loc=0)
    ax.set_title('Betrouwbaarheidsindex STPH per uittredepunt', fontsize=20)
    ax.set_ylim(2, 20)
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=False))
    ax.ticklabel_format(style='plain', axis='y')
    ax.set_yticks([2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20])
    ax.set_xlim(df_for_graph['M_value'].min() - 10, df_for_graph['M_value'].max() + 10)
    # TODO Nu Must Klein: Pas dijkpaal codering op x-as toe. Heb op dit moment niet deze gekoppeld aan de measure.

    # Categorie kleuren
    cg = geoprob_pipe.input_data.traject_normering.beta_categorie_grenzen
    ax.fill_between(
        [0, 100000], [cg["I"][0], cg["I"][0]], [cg["I"][1], cg["I"][1]],
        color='green', alpha=0.5, label='I'
    )
    ax.fill_between(
        [0, 100000], [cg["II"][0], cg["II"][0]], [cg["II"][1], cg["II"][1]],
        color='lightgreen', alpha=0.5, label='II')
    ax.fill_between(
        [0, 100000], [cg["III"][0], cg["III"][0]], [cg["III"][1], cg["III"][1]],
        color='yellow', alpha=0.5, label='III')
    ax.fill_between(
        [0, 100000], [cg["IV"][0], cg["IV"][0]], [cg["IV"][1], cg["IV"][1]],
        color='orange', alpha=0.5, label='IV')
    ax.fill_between(
        [0, 100000], [cg["V"][0], cg["V"][0]], [cg["V"][1], cg["V"][1]],
        color='red', alpha=0.5, label='V')
    ax.fill_between(
        [0, 100000], [cg["VI"][0], cg["VI"][0]], [cg["VI"][1], cg["VI"][1]],
        color='purple', alpha=0.5, label='VI')
    # TODO Nu Must klein: Dit zijn niet de officiële categoriekleuren. Aanpassen.
    # TODO Nu Must klein: De fills lijken een kleine overlap te hebben waardoor het lijkt alsof er een border is.

    # Categorie grens lijnen
    ax.axhline(cg["I"][0], color='black', linewidth=1)
    ax.axhline(cg["II"][0], color='black', linewidth=1)
    ax.axhline(cg["III"][0], color='black', linewidth=1)
    ax.axhline(cg["IV"][0], color='black', linewidth=1)
    ax.axhline(cg["V"][0], color='black', linewidth=1)

    # Plot vakken
    for index, row in geoprob_pipe.input_data.vakken.df.iterrows():
        ax.axvline(x=row['M_van'], color='black', linewidth=1)
        m_center = row['M_van'] + (row['M_tot'] - row['M_van']) / 2
        ax.text(x=m_center, y=2.25, s=f"Vak {row['vak_id']}",
                fontsize=15, verticalalignment='center', horizontalalignment='center')

    # Plot normering
    m_max = df_for_graph['M_value'].max()
    m_diff = m_max - df_for_graph['M_value'].min()
    m_spacing = m_diff * 0.02
    ax.text(
        m_max + m_spacing, cg["I"][0], '$β_{eis;sig;dsn / 30}$',
        fontsize=15, verticalalignment='center', horizontalalignment='left')
    ax.text(
        m_max + m_spacing, cg["II"][0], '$β_{eis;sig;dsn}$',
        fontsize=15, verticalalignment='center', horizontalalignment='left')
    ax.text(
        m_max + m_spacing, cg["III"][0], '$β_{eis;ond;dsn}$',
        fontsize=15, verticalalignment='center', horizontalalignment='left')
    ax.text(
        m_max + m_spacing, cg["IV"][0], '$β_{eis;ond}$',
        fontsize=15, verticalalignment='center', horizontalalignment='left')
    ax.text(
        m_max + m_spacing, cg["V"][0], '$β_{eis;ond * 30}$',
        fontsize=15, verticalalignment='center', horizontalalignment='left')
    export_path = os.path.join(geoprob_pipe.visualizations.graphs.export_dir, f"beta_uittredepunten.png")

    if export:
        fig.savefig(export_path, dpi=300)

    return fig


def beta_vakken_graph(geoprob_pipe: GeoProbPipe, export: bool = True) -> Figure:
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

    # Initial variables
    naam = 'Betrouwbaarheidsindex'
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.5))

    # Plot data
    plot_legend = True
    for index, row in df_for_graph.iterrows():
        label = None
        if plot_legend:
            label = "Betrouwbaarheidsindex"
            plot_legend = False
        ax.plot([row['M_van'], row['M_tot']], [row['beta'], row['beta']], linestyle='-',
                color='black', linewidth = '4', label=label)

    # Formatting
    ax.grid(linewidth=0.5, color='black', alpha=0.5, linestyle='-.')

    ax.set_xlabel('Dijkpaal', fontsize=20, labelpad=15)  # TODO: Nu nog measure
    ax.set_ylabel(f"{naam} [-]", fontsize=20, labelpad=15)
    ax.legend(fontsize=15, loc=0)
    ax.set_title('Betrouwbaarheidsindex STPH per uittredepunt', fontsize=20)
    ax.set_ylim(2, 20)
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=False))
    ax.ticklabel_format(style='plain', axis='y')
    ax.set_yticks([2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20])
    ax.set_xlim(df_for_graph['M_van'].min() - 10, df_for_graph['M_tot'].max() + 10)
    # TODO Nu Must Klein: Pas dijkpaal codering op x-as toe. Heb op dit moment niet deze gekoppeld aan de measure.

    # Categorie kleuren
    cg = geoprob_pipe.input_data.traject_normering.beta_categorie_grenzen
    ax.fill_between(
        [0, 100000], [cg["I"][0], cg["I"][0]], [cg["I"][1], cg["I"][1]],
        color='green', alpha=0.5, label='I')
    ax.fill_between(
        [0, 100000], [cg["II"][0], cg["II"][0]], [cg["II"][1], cg["II"][1]],
        color='lightgreen', alpha=0.5, label='II')
    ax.fill_between(
        [0, 100000], [cg["III"][0], cg["III"][0]], [cg["III"][1], cg["III"][1]],
        color='yellow', alpha=0.5, label='III')
    ax.fill_between(
        [0, 100000], [cg["IV"][0], cg["IV"][0]], [cg["IV"][1], cg["IV"][1]],
        color='orange', alpha=0.5, label='IV')
    ax.fill_between(
        [0, 100000], [cg["V"][0], cg["V"][0]], [cg["V"][1], cg["V"][1]],
        color='red', alpha=0.5, label='V')
    ax.fill_between(
        [0, 100000], [cg["VI"][0], cg["VI"][0]], [cg["VI"][1], cg["VI"][1]],
        color='purple', alpha=0.5, label='VI')
    # TODO Nu Must klein: Dit zijn niet de officiële categoriekleuren. Aanpassen.
    # TODO Nu Must klein: De fills lijken een kleine overlap te hebben waardoor het lijkt alsof er een border is.

    # Categorie grens lijnen
    ax.axhline(cg["I"][0], color='black', linewidth=1)
    ax.axhline(cg["II"][0], color='black', linewidth=1)
    ax.axhline(cg["III"][0], color='black', linewidth=1)
    ax.axhline(cg["IV"][0], color='black', linewidth=1)
    ax.axhline(cg["V"][0], color='black', linewidth=1)

    # Plot vakken
    for index, row in geoprob_pipe.input_data.vakken.df.iterrows():
        ax.axvline(x=row['M_van'], color='black', linewidth=1)
        m_center = row['M_van'] + (row['M_tot'] - row['M_van']) / 2
        ax.text(x=m_center, y=2.25, s=f"Vak {row['vak_id']}",
                fontsize=15, verticalalignment='center', horizontalalignment='center')

    # Plot normering
    m_max = df_for_graph['M_tot'].max()
    m_diff = m_max - df_for_graph['M_van'].min()
    m_spacing = m_diff * 0.02
    ax.text(
        m_max + m_spacing, cg["I"][0], '$β_{eis;sig;dsn / 30}$',
        fontsize=15, verticalalignment='center', horizontalalignment='left')
    ax.text(
        m_max + m_spacing, cg["II"][0], '$β_{eis;sig;dsn}$',
        fontsize=15, verticalalignment='center', horizontalalignment='left')
    ax.text(
        m_max + m_spacing, cg["III"][0], '$β_{eis;ond;dsn}$',
        fontsize=15, verticalalignment='center', horizontalalignment='left')
    ax.text(
        m_max + m_spacing, cg["IV"][0], '$β_{eis;ond}$',
        fontsize=15, verticalalignment='center', horizontalalignment='left')
    ax.text(
        m_max + m_spacing, cg["V"][0], '$β_{eis;ond * 30}$',
        fontsize=15, verticalalignment='center', horizontalalignment='left')

    if export:
        export_path = os.path.join(geoprob_pipe.visualizations.graphs.export_dir, f"beta_vakken.png")
        fig.savefig(export_path, dpi=300)

    return fig
