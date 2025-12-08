from __future__ import annotations
from typing import TYPE_CHECKING
import plotly.graph_objects as go
import os
import scipy.stats as sct
import geopandas as gpd
import numpy as np

if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


class BetaMap:

    def __init__(self, geoprob_pipe: GeoProbPipe, export: bool = False):

        self.geoprob_pipe = geoprob_pipe
        # Logic
        self._import_results()
        self._setup_gdf()
        self._determine_zoom()
        self._create_figure()
        self._optionally_export()

    def _import_results(self):
        # results import
        self.inp_point = self.geoprob_pipe.input_data.uittredepunten.gdf
        self.res_sc = self.geoprob_pipe.results.df_beta_scenarios

        # Setup of beta category limits
        # TODO Later Should Middel: Omzetten naar riskeer kleuren
        self.een = 10
        self.twee = -1*sct.norm.ppf(
            self.geoprob_pipe.input_data.traject_normering
            .faalkanseis_sign_dsn/30.0
            )
        self.drie = -1*sct.norm.ppf(
            self.geoprob_pipe.input_data.traject_normering
            .faalkanseis_sign_dsn
            )
        self.vier = -1*sct.norm.ppf(
            self.geoprob_pipe.input_data.traject_normering
            .faalkanseis_ond_dsn
            )
        self.vijf = -1*sct.norm.ppf(
            self.geoprob_pipe.input_data.traject_normering
            .faalkanseis_ondergrens
            )
        self.zes = -1*sct.norm.ppf(
            self.geoprob_pipe.input_data.traject_normering
            .faalkanseis_ondergrens*30
            )
        self.zeven = -1

        self.zesp = (self.zes-self.zeven)/(self.een-self.zeven)
        self.vijfp = (self.vijf-self.zeven)/(self.een-self.zeven)
        self.vierp = (self.vier-self.zeven)/(self.een-self.zeven)
        self.driep = (self.drie-self.zeven)/(self.een-self.zeven)
        self.tweep = (self.twee-self.zeven)/(self.een-self.zeven)

    def _setup_gdf(self):
        self.hoverdata = ["uittredepunt_id", "converged", "beta", "model_betas"]

        self.df = self.res_sc.merge(self.inp_point, on="uittredepunt_id",
                                    how="left")

        self.gdf = gpd.GeoDataFrame(
            self.df, geometry=gpd.points_from_xy(
                self.inp_point.geometry.x, self.inp_point.geometry.y
                ),
            crs="EPSG:28992")
        # Transformeer naar WGS84 (latitude / longitude)
        self.gdf_latlon = self.gdf.to_crs("EPSG:4326")

    def _determine_zoom(self):
        self.center_lat = self.gdf_latlon.geometry.y.mean()
        self.center_lon = self.gdf_latlon.geometry.x.mean()
        self.min_lat = self.gdf_latlon.geometry.y.min()
        self.max_lat = self.gdf_latlon.geometry.y.max()
        self.min_lon = self.gdf_latlon.geometry.x.min()
        self.max_lon = self.gdf_latlon.geometry.x.max()

        def _calculate_zoom(lat_range, lon_range):
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

        self.lat_range = self.max_lat - self.min_lat
        self.lon_range = self.max_lon - self.min_lon
        self.zoom = _calculate_zoom(self.lat_range, self.lon_range)

    def _create_figure(self):
        self.fig = go.Figure()

        self.fig.add_trace(go.Scattermap(
            mode='markers',
            lat=self.gdf_latlon.geometry.y,   # direct uit geometrie
            lon=self.gdf_latlon.geometry.x,   # direct uit geometrie
            marker=dict(
                size=8,
                color=self.gdf_latlon['beta'],
                colorscale=[
                    (0.00, "purple"),  (self.zesp, "purple"),
                    (self.zesp, "red"), (self.vijfp, "red"),
                    (self.vijfp, "orange"), (self.vierp, "orange"),
                    (self.vierp, "yellow"), (self.driep, "yellow"),
                    (self.driep, "lightgreen"), (self.tweep, "lightgreen"),
                    (self.tweep, "green"), (1.0, "green")
                ],
                cmin=-1,
                cmax=10,
                colorbar=dict(
                    title="Bèta, WBI cat.",
                    tickvals=[np.round(self.zeven, 2), np.round(self.zes, 2),
                              np.round(self.vijf, 2), np.round(self.vier, 2),
                              np.round(self.drie, 2), np.round(self.twee, 2),
                              10]
                )
            ),
            hoverinfo='text',
            text=self.gdf_latlon[self.hoverdata].apply(
                lambda row: '<br>'.join(
                    [f"{col}: {row[col]}" for col in self.hoverdata]
                    ),
                axis=1),
            showlegend=False
        ))

        # Layout
        self.fig.update_layout(
            map_style="open-street-map",
            # carto-positron, open-street-map, satellite-streets
            map_zoom=self.zoom,
            map_center=dict(
                lat=self.gdf_latlon.geometry.y.mean(),
                lon=self.gdf_latlon.geometry.x.mean()
            ),
            dragmode='zoom',
            title='Faalkansberekening STPH'
        )

    def _optionally_export(self):
        path = self.geoprob_pipe.visualizations.maps.export_dir
        self.fig.write_html(os.path.join(path, 'Faalkansberekening STPH.html'),
                            include_plotlyjs='cdn')
        self.fig.write_image(os.path.join(path, 'Faalkansberekening STPH.png'),
                             format='png')
