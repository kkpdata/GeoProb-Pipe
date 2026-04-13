from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List, Tuple
import plotly.graph_objects as go
import os
import geopandas as gpd
from shapely.geometry import LineString, MultiLineString, GeometryCollection

if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def _add_line(geoprob_pipe: GeoProbPipe, fig: go.Figure,
              layer: str, color: str):
    """ Helperfunctie om de lijnen uit de geopackage te vinden en toe te voegen aan de map. Layer is de naam van de
    laag in de geopackage waar de lijn is opgeslagen. Color is de kleur van deze lijn in de map. """

    gdf_traject = gpd.read_file(
        geoprob_pipe.input_data.app_settings.geopackage_filepath,
        layer=layer)
    gdf_traject = gdf_traject.to_crs("EPSG:4326")

    def plot_linestring(ls, display):
        xs, ys = ls.xy
        xs = list(xs)
        ys = list(ys)
        fig.add_trace(go.Scattermap(
            lon=xs,
            lat=ys,
            mode="lines",
            line=dict(color=color, width=1),
            hoverinfo="none",
            name=layer,
            legendgroup=layer,
            showlegend=display
        ))

    show = True
    for geom in gdf_traject.geometry:
        if isinstance(geom, LineString):
            plot_linestring(geom, show)
            show = False

        elif isinstance(geom, MultiLineString):
            for line in geom.geoms:
                plot_linestring(line, show)
                show = False

        elif isinstance(geom, GeometryCollection):
            for g in geom.geoms:
                if isinstance(g, LineString):
                    plot_linestring(g, show)
                    show = False
                elif isinstance(g, MultiLineString):
                    for line in g.geoms:
                        plot_linestring(line, show)
                        show = False

        else:
            print("Skipping unsupported geometry:", geom.geom_type)

    return fig

def _generate_colorscale(cg: Dict[str, List], labels: List[str]) -> List[Tuple[float, str]]:
    # cg > category label > [van beta, tot beta]
    upper_boundary_beta_graph = cg[labels[0]][1]
    lower_boundary_beta_graph = cg[labels[-1]][0]
    beta_range_graph = upper_boundary_beta_graph - lower_boundary_beta_graph

    # Calculate intervals (starts with boundary value 1.0, and then decreases)
    colorscale_intervals: Dict = {}
    for index, label in enumerate(labels):
        cg_beta_bovengrens = cg[label][1]
        colorscale_intervals[index] = (cg_beta_bovengrens - lower_boundary_beta_graph) / beta_range_graph

    # Other end boundary value: 0.0
    colorscale_intervals[labels.__len__()] = 0.0

    # Color scale
    colors = ["rgb(30,141,41)", "rgb(146,206,90)", "rgb(198,226,176)", "rgb(255,255,0)", "rgb(254,165,3)",
              "rgb(255,0,0)", "rgb(177,33,38)"]
    colorscale = [
        (colorscale_intervals[7], colors[6]),
        (colorscale_intervals[6], colors[6]),
        (colorscale_intervals[6], colors[5]),
        (colorscale_intervals[5], colors[5]),
        (colorscale_intervals[5], colors[4]),
        (colorscale_intervals[4], colors[4]),
        (colorscale_intervals[4], colors[3]),
        (colorscale_intervals[3], colors[3]),
        (colorscale_intervals[3], colors[2]),
        (colorscale_intervals[2], colors[2]),
        (colorscale_intervals[2], colors[1]),
        (colorscale_intervals[1], colors[1]),
        (colorscale_intervals[1], colors[0]),
        (colorscale_intervals[0], colors[0]),
    ]

    return colorscale


class BetaMap:

    def __init__(self, geoprob_pipe: GeoProbPipe, export: bool = False):

        self.geoprob_pipe = geoprob_pipe
        self.export = export

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
        self.res_sc = self.geoprob_pipe.results.df_beta_scenarios_final
        mask = self.inp_point["uittredepunt_id"].isin(self.res_sc["uittredepunt_id"])
        self.inp_point = self.inp_point[mask]

        # Setup of beta category limits
        self.cg: Dict[str, List] = self.geoprob_pipe.input_data.traject_normering.riskeer_categorie_grenzen
        print(f"{self.cg=}")
        self.labels: List[str] = list(self.cg.keys())
        # self.labels: List[str] = ["+III", "+II", "+I", "0", "-I", "-II", "-III"]

        # print(f"{self.len_cg=}")

        # self.marker_colors: Dict = ...

        # self.color1 = (self.cg[self.labels[0]][1] - self.cg[self.labels[6]][0]) / self.len_cg
        # self.color2 = (self.cg[self.labels[1]][1] - self.cg[self.labels[6]][0]) / self.len_cg
        # self.color3 = (self.cg[self.labels[2]][1] - self.cg[self.labels[6]][0]) / self.len_cg
        # self.color4 = (self.cg[self.labels[3]][1] - self.cg[self.labels[6]][0]) / self.len_cg
        # self.color5 = (self.cg[self.labels[4]][1] - self.cg[self.labels[6]][0]) / self.len_cg
        # self.color6 = (self.cg[self.labels[5]][1] - self.cg[self.labels[6]][0]) / self.len_cg
        # self.color7 = (self.cg[self.labels[6]][1] - self.cg[self.labels[6]][0]) / self.len_cg
        # self.color8 = (self.cg[self.labels[6]][0] - self.cg[self.labels[6]][0]) / self.len_cg

    def _setup_gdf(self):
        self.hoverdata = ["uittredepunt_id", "converged", "beta"]

        self.df = self.res_sc.merge(self.inp_point, on="uittredepunt_id", how="inner")
        idx = self.df.groupby(["uittredepunt_id"])["beta"].idxmin()
        self.df = self.df.loc[idx]

        self.gdf = gpd.GeoDataFrame(
            self.df,
            geometry=gpd.points_from_xy(self.inp_point.geometry.x, self.inp_point.geometry.y),
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
            mode="markers",
            lat=self.gdf_latlon.geometry.y,
            lon=self.gdf_latlon.geometry.x,
            marker=dict(size=9, color="black"),
            showlegend=False))
        print(f"{_generate_colorscale(cg=self.cg, labels=self.labels)=}")
        self.fig.add_trace(go.Scattermap(
            mode='markers',
            lat=self.gdf_latlon.geometry.y,   # direct uit geometrie
            lon=self.gdf_latlon.geometry.x,   # direct uit geometrie
            marker=dict(
                size=8,
                color=self.gdf_latlon['beta'],
                colorscale=_generate_colorscale(cg=self.cg, labels=self.labels),
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
        if self.export:
            path = self.geoprob_pipe.visualizations.maps.export_dir
            self.fig.write_html(os.path.join(
                path, 'Faalkansberekening STPH.html'), include_plotlyjs='cdn')
            # self.fig.write_image(os.path.join(
            #     path, 'Faalkansberekening STPH.png'), format='png')


# import numpy as np
#
# input_value = [
#     (0.0, 'rgb(177,33,38)'),
#     (np.float64(0.07794071307696135), 'rgb(177,33,38)'),
#     (np.float64(0.07794071307696135), 'rgb(255,0,0)'),
#     (np.float64(0.11043771870038431), 'rgb(255,0,0)'),
#     (np.float64(0.11043771870038431), 'rgb(254,165,3)'),
#     (np.float64(0.1258272663290458), 'rgb(254,165,3)'),
#     (np.float64(0.1258272663290458), 'rgb(255,255,0)'),
#     (np.float64(0.1529680171568277), 'rgb(255,255,0)'),
#     (np.float64(0.1529680171568277), 'rgb(198,226,176)'),
#     (np.float64(0.1777409767884898), 'rgb(198,226,176)'),
#     (np.float64(0.1777409767884898), 'rgb(146,206,90)'),
#     (np.float64(0.20066673578748828), 'rgb(146,206,90)'),
#     (np.float64(0.20066673578748828), 'rgb(30,141,41)'),
#     (1.0, 'rgb(30,141,41)'),
# ]
#



# cg = {
#     '+III': [np.float64(5.612001244174789), 20],
#     '+II': [np.float64(5.1993375821928165), np.float64(5.612001244174789)],
#     '+I': [np.float64(4.753424308822899), np.float64(5.1993375821928165)],
#     '0': [np.float64(4.264890793922825), np.float64(4.753424308822899)],
#     '-I': [np.float64(3.9878789366069176), np.float64(4.264890793922825)],
#     '-II': [np.float64(3.4029328353853043), np.float64(3.9878789366069176)],
#     '-III': [2, np.float64(3.4029328353853043)]
# }
#


# cg= {
#     '+III': [np.float64(4.264890793922825), 20.0],
#     '+II': [np.float64(3.7190164854556804), np.float64(4.264890793922825)],
#     '+I': [np.float64(3.090232306167813), np.float64(3.7190164854556804)],
#     '0': [np.float64(2.3263478740408408), np.float64(3.090232306167813)],
#     '-I': [np.float64(2.3263478740408408), np.float64(2.3263478740408408)],
#     '-II': [np.float64(1.2815515655446004), np.float64(2.3263478740408408)],
#     '-III': [2.0, np.float64(1.2815515655446004)],
# }
