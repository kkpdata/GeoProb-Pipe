from __future__ import annotations
from typing import TYPE_CHECKING
import plotly.graph_objects as go
import os
import geopandas as gpd
from shapely.geometry import LineString, MultiLineString, GeometryCollection

if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def _add_line(geoprobpipe: GeoProbPipe, fig: go.Figure,
              layer: str, color: str):
    """
Helperfunctie om de lijen uit de geopackage te vinden en
toe tevoegen aan de map. Layer is de naam van de laag in de
geopackage waar de lijn is opgeslagen. Color is de kleur van deze
lijn in de map.
    """
    gdf_traject = gpd.read_file(
        geoprobpipe.input_data.app_settings.geopackage_filepath,
        layer=layer)
    gdf_traject = gdf_traject.to_crs("EPSG:4326")

    def plot_linestring(ls):
        xs, ys = ls.xy
        xs = list(xs)
        ys = list(ys)
        fig.add_trace(go.Scattermap(
            lon=xs,
            lat=ys,
            mode="lines",
            line=dict(color=color, width=1),
            hoverinfo="none",
            name=layer
        ))

    for geom in gdf_traject.geometry:
        if isinstance(geom, LineString):
            plot_linestring(geom)

        elif isinstance(geom, MultiLineString):
            for line in geom.geoms:
                plot_linestring(line)

        elif isinstance(geom, GeometryCollection):
            for g in geom.geoms:
                if isinstance(g, LineString):
                    plot_linestring(g)
                elif isinstance(g, MultiLineString):
                    for line in g.geoms:
                        plot_linestring(line)

        else:
            print("Skipping unsupported geometry:", geom.geom_type)

    return fig


class BetaMap:

    def __init__(self, geoprob_pipe: GeoProbPipe, export: bool = False):

        self.geoprob_pipe = geoprob_pipe

        # Logic
        self._import_results()
        self._setup_gdf()
        self._determine_zoom()
        self._create_figure()
        self._add_lines()
        self._optionally_export()

    def _import_results(self):
        # results import
        self.inp_point = self.geoprob_pipe.input_data.uittredepunten.gdf
        self.res_sc = self.geoprob_pipe.results.df_beta_scenarios

        # Setup of beta category limits
        self.cg = (self.geoprob_pipe.input_data.traject_normering
                   .riskeer_categorie_grenzen)
        self.colors = ["rgb(30,141,41)", "rgb(146,206,90)",
                       "rgb(198,226,176)", "rgb(255,255,0)",
                       "rgb(254,165,3)", "rgb(255,0,0)",
                       "rgb(177,33,38)"]
        self.labels = ["+III", "+II", "+I", "0", "-I", "-II", "-III"]

        self.len_cg = self.cg[self.labels[0]][1] - self.cg[self.labels[6]][0]

        self.color1 = ((self.cg[self.labels[0]][1]
                        - self.cg[self.labels[6]][0]) / self.len_cg)
        self.color2 = ((self.cg[self.labels[1]][1]
                        - self.cg[self.labels[6]][0]) / self.len_cg)
        self.color3 = ((self.cg[self.labels[2]][1]
                        - self.cg[self.labels[6]][0]) / self.len_cg)
        self.color4 = ((self.cg[self.labels[3]][1]
                        - self.cg[self.labels[6]][0]) / self.len_cg)
        self.color5 = ((self.cg[self.labels[4]][1]
                        - self.cg[self.labels[6]][0]) / self.len_cg)
        self.color6 = ((self.cg[self.labels[5]][1]
                        - self.cg[self.labels[6]][0]) / self.len_cg)
        self.color7 = ((self.cg[self.labels[6]][1]
                        - self.cg[self.labels[6]][0]) / self.len_cg)
        self.color8 = ((self.cg[self.labels[6]][0]
                        - self.cg[self.labels[6]][0]) / self.len_cg)

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
                    (self.color8, self.colors[6]),
                    (self.color7, self.colors[6]),
                    (self.color7, self.colors[5]),
                    (self.color6, self.colors[5]),
                    (self.color6, self.colors[4]),
                    (self.color5, self.colors[4]),
                    (self.color5, self.colors[3]),
                    (self.color4, self.colors[3]),
                    (self.color4, self.colors[2]),
                    (self.color3, self.colors[2]),
                    (self.color3, self.colors[1]),
                    (self.color2, self.colors[1]),
                    (self.color2, self.colors[0]),
                    (self.color1, self.colors[0])
                ],
                cmin=self.cg[self.labels[6]][0],
                cmax=self.cg[self.labels[0]][1],
                colorbar=dict(
                    title="Bèta, WBI cat.",
                    tickvals=[
                        self.cg[self.labels[6]][0],
                        self.cg[self.labels[6]][1],
                        self.cg[self.labels[5]][1],
                        self.cg[self.labels[4]][1],
                        self.cg[self.labels[3]][1],
                        self.cg[self.labels[2]][1],
                        self.cg[self.labels[1]][1],
                        self.cg[self.labels[0]][1]
                    ],
                    ticktext=[f"{v:.2f}" for v in [
                        self.cg[self.labels[6]][0],
                        self.cg[self.labels[6]][1],
                        self.cg[self.labels[5]][1],
                        self.cg[self.labels[4]][1],
                        self.cg[self.labels[3]][1],
                        self.cg[self.labels[2]][1],
                        self.cg[self.labels[1]][1],
                        self.cg[self.labels[0]][1]]],
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
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
            ),
            dragmode='zoom',
            title='Faalkansberekening STPH'
        )

    def _add_lines(self):
        self.fig = _add_line(self.geoprob_pipe, self.fig,
                             "dijktraject", "black")
        self.fig = _add_line(self.geoprob_pipe, self.fig,
                             "intredelijn", "blue")
        self.fig = _add_line(self.geoprob_pipe, self.fig,
                             "binnenteenlijn", "purple")
        self.fig = _add_line(self.geoprob_pipe, self.fig,
                             "buitenteenlijn", "red")

    def _optionally_export(self):
        path = self.geoprob_pipe.visualizations.maps.export_dir
        self.fig.write_html(os.path.join(path, 'Faalkansberekening STPH.html'),
                            include_plotlyjs='cdn')
        self.fig.write_image(os.path.join(path, 'Faalkansberekening STPH.png'),
                             format='png')
