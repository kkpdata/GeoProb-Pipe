import matplotlib.pyplot as plt
import os
from pandas import read_excel, merge
from datetime import datetime
from matplotlib.ticker import ScalarFormatter
from geoprob_pipe.misc.traject_normering import TrajectNormering


# Collect data
df_uittredepunten = read_excel(r"C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV2\GeoProb-Pipe\workspaces\example_new_calculations\input\input.xlsx", sheet_name="Uittredepunten")
df_results_combined = read_excel(r"C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV2\GeoProb-Pipe\workspaces\example_new_calculations\output\2025-06-30_1714\df_combined.xlsx")
df_for_graph = merge(
    left=df_results_combined[["uittredepunt_id", "beta"]],
    right=df_uittredepunten[["uittredepunt_id", "M_value"]],
    on="uittredepunt_id",
    how="left"
)
traject_normering = TrajectNormering()  # TODO: Gebruikt nu dummy data: traject Elden-Heteren

# Initial variables
naam = 'Betrouwbaarheidsindex'
inp_semi = 'Beta_semi_prob'
inp = 'DesignPoint.Beta[x]'
fig = plt.figure(figsize=(20,10))
ax = plt.axes()
ax.yaxis.set_major_locator(plt.MultipleLocator(0.5))

# Plot data
plt.plot(df_for_graph['M_value'], df_for_graph["beta"],'o', color='black', markersize=3, label='Prob. ontwerpp.')

# Formatting
plt.grid(linewidth=0.5,color='black',alpha=0.5,linestyle='-.')
plt.xlabel('Dijkpaal', fontsize=20, labelpad=15)  # TODO: Nu nog measure
plt.ylabel(f"{naam} [-]", fontsize=20, labelpad=15)
plt.legend(fontsize=15, loc=0)
plt.title('Betrouwbaarheidsindex STPH scenarioberekeningen', fontsize=20)
plt.ylim(2, 20)
ax.set_yscale("log")
ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=False))
ax.ticklabel_format(style='plain', axis='y')
ax.set_yticks([2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20])
plt.xlim(df_for_graph['M_value'].min()-10, df_for_graph['M_value'].max()+10)
# TODO Nu Must Klein: Pas dijkpaal codering op x-as toe. Heb op dit moment niet deze gekoppeld aan de measure.

# Categorie kleuren
cg = traject_normering.beta_categorie_grenzen
plt.fill_between(
    [0, 100000],[cg["I"][0], cg["I"][0]],[cg["I"][1], cg["I"][1]],
    color='green', alpha=0.5, label='I')
plt.fill_between(
    [0, 100000],[cg["II"][0], cg["II"][0]],[cg["II"][1], cg["II"][1]],
    color='lightgreen', alpha=0.5, label='II')
plt.fill_between(
    [0, 100000],[cg["III"][0], cg["III"][0]],[cg["III"][1], cg["III"][1]],
    color='yellow', alpha=0.5, label='III')
plt.fill_between(
    [0, 100000],[cg["IV"][0], cg["IV"][0]],[cg["IV"][1], cg["IV"][1]],
    color='orange', alpha=0.5, label='IV')
plt.fill_between(
    [0, 100000],[cg["V"][0], cg["V"][0]],[cg["V"][1], cg["V"][1]],
    color='red', alpha=0.5, label='V')
plt.fill_between(
    [0, 100000],[cg["VI"][0], cg["VI"][0]],[cg["VI"][1], cg["VI"][1]],
    color='purple', alpha=0.5, label='VI')
# TODO Nu Must klein: Dit zijn niet de officiële categoriekleuren. Aanpassen.
# TODO Nu Must klein: De fills lijken een kleine overlap te hebben waardoor het lijkt alsof er een border is.

# Categorie grens lijnen
plt.axhline(cg["I"][0], color='black', linewidth=1)
plt.axhline(cg["II"][0], color='black', linewidth=1)
plt.axhline(cg["III"][0], color='black', linewidth=1)
plt.axhline(cg["IV"][0], color='black', linewidth=1)
plt.axhline(cg["V"][0], color='black', linewidth=1)

# Plot normering
m_max = df_for_graph['M_value'].max()
m_diff = m_max - df_for_graph['M_value'].min()
m_spacing = m_diff * 0.02
plt.text(
    m_max + m_spacing, cg["I"][0], '$β_{eis;sig;dsn / 30}$',
    fontsize=15, verticalalignment='center', horizontalalignment='left')
plt.text(
    m_max + m_spacing, cg["II"][0], '$β_{eis;sig;dsn}$',
    fontsize=15, verticalalignment='center', horizontalalignment='left')
plt.text(
    m_max + m_spacing, cg["III"][0], '$β_{eis;ond;dsn}$',
    fontsize=15, verticalalignment='center', horizontalalignment='left')
plt.text(
    m_max + m_spacing, cg["IV"][0], '$β_{eis;ond}$',
    fontsize=15, verticalalignment='center', horizontalalignment='left')
plt.text(
    m_max + m_spacing, cg["V"][0], '$β_{eis;ond * 30}$',
    fontsize=15, verticalalignment='center', horizontalalignment='left')

# Export figure
timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
export_dir = r"C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV2\exports"
os.makedirs(export_dir, exist_ok=True)
export_path = os.path.join(export_dir, f"{timestamp}_B_STPH_sc.png")
plt.savefig(export_path, dpi=300)
