from repo_utils.utils import repository_root_path
from geoprob_pipe import GeoProbPipe
import os

repo_root = repository_root_path()
workspace_path = os.path.join(repo_root, "workspaces", "traject_224")
geoprob_pipe = GeoProbPipe(workspace_path)
geoprob_pipe.export_archive()

##

import scipy.stats as sct
import geopandas as gpd
from plotly.offline import plot
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

inputp = geoprob_pipe.input_data.uittredepunten.df
inpsc = geoprob_pipe.input_data.ondergrondscenarios.df
inphfreq = geoprob_pipe.input_data.overschrijdingsfrequentielijnen
inppar = geoprob_pipe.input_data.df_overview_parameters
resutp = geoprob_pipe.results.df_beta_uittredepunten
ressc = geoprob_pipe.results.df_beta_scenarios
reslim = geoprob_pipe.results.df_beta_limit_states

##





een = 10
twee = -1*sct.norm.ppf(geoprob_pipe.input_data.traject_normering.faalkanseis_sign_dsn/30.0)
drie = -1*sct.norm.ppf(geoprob_pipe.input_data.traject_normering.faalkanseis_sign_dsn)
vier  = -1*sct.norm.ppf(geoprob_pipe.input_data.traject_normering.faalkanseis_ond_dsn)
vijf = -1*sct.norm.ppf(geoprob_pipe.input_data.traject_normering.faalkanseis_ondergrens)
zes = -1*sct.norm.ppf(geoprob_pipe.input_data.traject_normering.faalkanseis_ondergrens*30)
zeven = -1

zesp = (zes-zeven)/(een-zeven)
vijfp = (vijf-zeven)/(een-zeven)
vierp = (vier-zeven)/(een-zeven)
driep = (drie-zeven)/(een-zeven)
tweep = (twee-zeven)/(een-zeven)




hoverdata = [
'uittredepunt_id',
'beta']

df = ressc.merge(inputp, on='uittredepunt_id', how='left')

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.uittredepunt_x_coord, df.uittredepunt_y_coord), crs="EPSG:28992")
print(gdf.columns)
# 2️⃣ Transformeer naar WGS84 (latitude / longitude)
gdf_latlon = gdf.to_crs("EPSG:4326")


center_lat=gdf_latlon.geometry.y.mean(),
center_lon=gdf_latlon.geometry.x.mean()
min_lat = gdf_latlon.geometry.y.min()
max_lat = gdf_latlon.geometry.y.max()
min_lon = gdf_latlon.geometry.x.min()
max_lon = gdf_latlon.geometry.x.max()

def bereken_zoom(lat_range, lon_range):
    max_range = max(lat_range, lon_range)
    if max_range < 0.01:
        return 15
    elif max_range < 0.05:
        return 13
    elif max_range < 0.1:
        return 12
    elif max_range < 0.5:
        return 10
    elif max_range < 1.0:
        return 9
    else:
        return 8

lat_range = max_lat - min_lat
lon_range = max_lon - min_lon
zoom = bereken_zoom(lat_range, lon_range)

fig = go.Figure()

fig.add_trace(go.Scattermap(
    mode='markers',
    lat=gdf_latlon.geometry.y,   # direct uit geometrie
    lon=gdf_latlon.geometry.x,   # direct uit geometrie
    marker=dict(
        size=8,
        color=gdf_latlon['beta'],
        colorscale=[
            (0.00, "purple"),  (zesp, "purple"),
            (zesp, "red"), (vijfp, "red"),
            (vijfp, "orange"), (vierp, "orange"),
            (vierp, "yellow"), (driep, "yellow"),
            (driep, "lightgreen"), (tweep, "lightgreen"),
            (tweep, "green"), (1.0, "green")
        ],
        cmin=-1,
        cmax=10,
        colorbar=dict(
            title="Bèta, WBI cat.",
            tickvals=[np.round(zeven, 2), np.round(zes, 2), np.round(vijf, 2),
                      np.round(vier, 2), np.round(drie, 2), np.round(twee, 2), 10]
        )
    ),
    hoverinfo='text',
    text=gdf_latlon[hoverdata].apply(
        lambda row: '<br>'.join([f"{col}: {row[col]}" for col in hoverdata]), axis=1),
    showlegend=False
))

# Layout
fig.update_layout(
    map_style="open-street-map", #carto-positron, open-street-map, satellite-streets
    map_zoom=zoom,
    map_center=dict(
        lat=gdf_latlon.geometry.y.mean(),
        lon=gdf_latlon.geometry.x.mean()
    ),
    dragmode='zoom',
    title='Faalkansberekening STPH'
)
path = geoprob_pipe.results.export_dir
plot(fig, filename=path + "/" + 'Faalkansberekening STPH.html',
     config={'scrollZoom': True})
#plt.close('all')









##