import matplotlib.pyplot as plt
from datetime import datetime
import os
import plotly.graph_objects as go
from geoprob_pipe import GeoProbPipe
from pandas import merge, Series

project = GeoProbPipe(...)

# Determine lowest scoring result per vak
df = project.results.df_limit_states
df = df[df['model'] == "piping"]
df_uittredepunten = project.input_data.uittredepunten.df[["uittredepunt_id", "vak_id"]]
df = merge(df, df_uittredepunten, how="left", on="uittredepunt_id")
df = df[["uittredepunt_id", "beta", "vak_id"]]

# Collect data in usable table
df_limit_states = project.results.df_limit_states
df_alphas = df_limit_states[df_limit_states["model"] == "piping"][["uittredepunt_id", "alphas"]]
df_uittredepunten = project.input_data.uittredepunten.df[["uittredepunt_id", "vak_id"]]
df_vakken = project.input_data.vakken.df[["vak_id", "vak_naam"]]
df_merged = merge(df_alphas, df_uittredepunten, how="left", on="uittredepunt_id")
df_merged = merge(df_merged, df_vakken, how="left", on="vak_id")

# Create column per alpha
stochast_names = [
    'c_voorland', 'buitenwaterstand', 'polderpeil', 'mv_exit', 'L_but', 'L_intrede', 'modelfactor_p', 'd70', 'D_wvp',
    'kD_wvp', 'top_zand', 'gamma_water', 'g', 'v', 'theta', 'eta', 'd70_m', 'gamma_korrel', 'r_c_deklaag'
]
df_merged[stochast_names] = df_merged['alphas'].apply(Series)
df_merged = df_merged.drop(columns='alphas')

# Create column per invloedsfactor
df_invloedsfactoren = df_merged.copy(deep=True)
df_invloedsfactoren[stochast_names] = df_invloedsfactoren[stochast_names] ** 2
df_invloedsfactoren['sum'] = df_invloedsfactoren[stochast_names].sum(axis=1)

fig = go.Figure()
for stochast_name in stochast_names:
    fig.add_trace(go.Bar(
        x=df_invloedsfactoren['vak_naam'],
        y=df_invloedsfactoren[stochast_name],
    ))
fig.update_layout(barmode="stack")


AlphasPerVak = data.groupby(by=['VakID'], as_index=False, axis=0).agg({
    'Vaknaam' : 'first',
    'D.infl': 'mean',
    'd70.infl': 'mean',
    'd_deklaag.infl': 'mean',
    'ic.infl': 'mean',
     'k.infl': 'mean',
     'r.infl': 'mean',
     'WS.infl': 'mean',
     'mp.infl': 'mean',
     'mu.infl': 'mean',
     'y_satdek.infl': 'mean',
     'λ1.infl': 'mean'
})
AlphasPerVak[AlphasPerVak['VakID'] != '0'].style.background_gradient(cmap='RdYlGn_r',axis=None,subset=['D.infl','d70.infl','d_deklaag.infl', 'ic.infl','k.infl','WS.infl','r.infl','mp.infl','mu.infl','y_satdek.infl','λ1.infl'])

plt.figure(figsize=(20,10))
plt.bar(
    AlphasPerVak['Vaknaam'],
    AlphasPerVak['r.infl'],
    color='green',label='r')
plt.bar(
    AlphasPerVak['Vaknaam'],
    AlphasPerVak['λ1.infl'],
    bottom=AlphasPerVak['r.infl'],color='blue',label='λ1')
plt.bar(
    AlphasPerVak['Vaknaam'],
    AlphasPerVak['D.infl'],
    bottom=AlphasPerVak['r.infl']+AlphasPerVak['λ1.infl'],
    color='pink',label='D')
plt.bar(
    AlphasPerVak['Vaknaam'],
    AlphasPerVak['d_deklaag.infl'],
    bottom=AlphasPerVak['r.infl']+AlphasPerVak['λ1.infl']+AlphasPerVak['D.infl'],
    color='yellow',label='d')
plt.bar(
    AlphasPerVak['Vaknaam'],
    AlphasPerVak['ic.infl'],
    bottom=AlphasPerVak['r.infl']+AlphasPerVak['λ1.infl']+AlphasPerVak['D.infl']+AlphasPerVak['d_deklaag.infl'],
    color='brown',label='ic')
plt.bar(AlphasPerVak['Vaknaam'],AlphasPerVak['k.infl'],bottom=AlphasPerVak['r.infl']+AlphasPerVak['λ1.infl']+AlphasPerVak['D.infl']+AlphasPerVak['d_deklaag.infl']+AlphasPerVak['ic.infl'],color='orange',label='k')
plt.bar(AlphasPerVak['Vaknaam'],AlphasPerVak['WS.infl'],bottom=AlphasPerVak['r.infl']+AlphasPerVak['λ1.infl']+AlphasPerVak['D.infl']+AlphasPerVak['d_deklaag.infl']+AlphasPerVak['ic.infl']+AlphasPerVak['k.infl'],color='grey',label='WS')
plt.bar(AlphasPerVak['Vaknaam'],AlphasPerVak['mp.infl'],bottom=AlphasPerVak['r.infl']+AlphasPerVak['λ1.infl']+AlphasPerVak['D.infl']+AlphasPerVak['d_deklaag.infl']+AlphasPerVak['ic.infl']+AlphasPerVak['k.infl']+AlphasPerVak['WS.infl'],color='lightgreen',label='mp')
plt.bar(AlphasPerVak['Vaknaam'],AlphasPerVak['mu.infl'],bottom=AlphasPerVak['r.infl']+AlphasPerVak['λ1.infl']+AlphasPerVak['D.infl']+AlphasPerVak['d_deklaag.infl']+AlphasPerVak['ic.infl']+AlphasPerVak['k.infl']+AlphasPerVak['WS.infl']+AlphasPerVak['mp.infl'],color='gold',label='mu')
plt.bar(AlphasPerVak['Vaknaam'],AlphasPerVak['y_satdek.infl'],bottom=AlphasPerVak['r.infl']+AlphasPerVak['λ1.infl']+AlphasPerVak['D.infl']+AlphasPerVak['d_deklaag.infl']+AlphasPerVak['ic.infl']+AlphasPerVak['k.infl']+AlphasPerVak['WS.infl']+AlphasPerVak['mp.infl']+AlphasPerVak['mu.infl'],color='purple',label='y')
plt.bar(AlphasPerVak['Vaknaam'],AlphasPerVak['d70.infl'],bottom=AlphasPerVak['r.infl']+AlphasPerVak['λ1.infl']+AlphasPerVak['D.infl']+AlphasPerVak['d_deklaag.infl']+AlphasPerVak['ic.infl']+AlphasPerVak['k.infl']+AlphasPerVak['WS.infl']+AlphasPerVak['mp.infl']+AlphasPerVak['mu.infl']+AlphasPerVak['y_satdek.infl'],color='olive',label='d70')
plt.ylim(0,1)
plt.xticks(rotation=90)
plt.xlabel('Dijkvak', fontsize=18,labelpad=15)
plt.ylabel('Invloedsfactor', fontsize=18,labelpad=15)
plt.grid(which='both')
plt.legend(bbox_to_anchor=(1,1))
plt.xlim(-1,len(AlphasPerVak['Vaknaam']))

# Export figure
timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
export_dir = r"C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV2\exports"
os.makedirs(export_dir, exist_ok=True)
export_path = os.path.join(export_dir, f"{timestamp}_Invloed_per_vak.png")
plt.savefig(export_path, dpi=300)


##

my_dict = {
    'L_achterland': 0.0,
    'c_voorland': -0.029510212061422684,
    'c_achterland': -0.19476482077085178,
    'polderpeil': 0.0,
    'buitenwaterstand': -0.49648488303997307,
    'L_intrede': 0.0,
    'L_but': 0.0,
    'L_bit': 0.0,
    'mv_exit': 0.0,
    'top_zand': -0.07745224086978751,
    'kD_wvp': -0.24614591095363988,
    'modelfactor_u': 0.03345252679206898,
    'gamma_water': 0.0, 'gamma_sat_deklaag': 0.004458598920536149, 'D_wvp': -0.0015952965537779876,
    'modelfactor_h': 0.0009274972710317258, 'i_c_h': 0.022369580723921333, 'modelfactor_p': 0.314464822679038,
    'd70': 0.12270172228581716, 'g': 0.0, 'v': 0.0, 'theta': 0.0, 'eta': 0.0, 'd70_m': 0.0, 'gamma_korrel': 0.0,
    'r_c_deklaag': 0.0}

# my_dict = {'L_achterland': 0.0, 'c_voorland': 0.002967427954935977, 'c_achterland': -0.3882076609011184, 'polderpeil': 0.0, 'buitenwaterstand': -0.7607415330246432, 'L_intrede': 0.0, 'L_but': 0.0, 'L_bit': 0.0, 'mv_exit': 0.0, 'top_zand': 0.0, 'kD_wvp': -0.5197633239558418, 'modelfactor_u': 0.013641371669388247, 'gamma_water': 0.0, 'gamma_sat_deklaag': 0.014775871198764258, 'D_wvp': 0.0}


invloedsfactoren = []
for key, value in my_dict.items():
    invloedsfactoren.append(value * value)
print(sum(invloedsfactoren))

##
