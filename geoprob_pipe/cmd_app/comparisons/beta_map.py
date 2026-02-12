from __future__ import annotations
import os
import plotly.graph_objects as go
import geopandas as gpd
from shapely.geometry import LineString, MultiLineString, GeometryCollection
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.comparisons import ComparisonCollector


def _determine_zoom(gdf_latlon):
    min_lat = gdf_latlon.geometry.y.min()
    max_lat = gdf_latlon.geometry.y.max()
    min_lon = gdf_latlon.geometry.x.min()
    max_lon = gdf_latlon.geometry.x.max()

    def _calculate_zoom(lat_range_val, lon_range_val):
        max_range = max(lat_range_val, lon_range_val)
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
    zoom = _calculate_zoom(lat_range, lon_range)
    return zoom


def _add_line(comparison: ComparisonCollector, fig: go.Figure,
              layer: str, color: str):
    gdf_traject = gpd.read_file(comparison.geopackage_filepath_1,
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
            line=dict(color=color, width=1.5),
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


def map_delta_beta_comparison(comparison: ComparisonCollector,
                              export: bool = False) -> go.Figure:
    # load data from class
    gdf_result1 = (comparison.gdf1_uittredepunten[
        ["uittredepunt_id", "beta", "geometry"]
        ].rename(columns={"beta": "beta1"}))
    gdf_result2 = (comparison.gdf2_uittredepunten[
        ["uittredepunt_id", "beta"]].rename(columns={"beta": "beta2"}))
    gdf = gdf_result1.merge(gdf_result2, on="uittredepunt_id")
    gdf["beta_delta"] = gdf["beta2"] - gdf["beta1"]

    # Covert to crs for map.
    gdf_latlon = gdf.to_crs("EPSG:4326")

    fig = go.Figure()
    fig.add_trace(go.Scattermap(
        mode="markers",
        lat=gdf_latlon.geometry.y,
        lon=gdf_latlon.geometry.x,
        marker=dict(
            size=9,
            color="black"
            ),
        showlegend=False
        ))
    hoverdata = ["uittredepunt_id", "beta_delta", "beta1", "beta2"]
    fig.add_trace(go.Scattermap(
        mode="markers",
        lat=gdf_latlon.geometry.y,
        lon=gdf_latlon.geometry.x,
        marker=dict(
            size=8,
            color=gdf_latlon["beta_delta"],
            cmax=3,
            cmin=-3,
            colorscale="RdYlGn",
            colorbar=dict(title="Delta Beta")
        ),
        hoverinfo='text',
        text=gdf_latlon[hoverdata].apply(
            lambda row: '<br>'.join(
                [f"{col}: {round(row[col], 3)}" for col in hoverdata]
                ),
            axis=1),
        showlegend=False
        ))

    fig = _add_line(comparison, fig, "dijktraject", "black")
    fig = _add_line(comparison, fig, "intredelijn", "blue")
    fig = _add_line(comparison, fig, "binnenteenlijn", "red")
    fig = _add_line(comparison, fig, "buitenteenlijn", "red")

    zoom = _determine_zoom(gdf_latlon)
    fig.update_layout(
        map_style="open-street-map",
        # carto-positron, open-street-map, satellite-streets
        map_zoom=zoom,
        map_center=dict(
            lat=gdf_latlon.geometry.y.mean(),
            lon=gdf_latlon.geometry.x.mean()
        ),
        dragmode="zoom",
        title=f"Delta beta van uittredepunten tussen<br>" +
              f"<sup>Beta1: {comparison.name_1} en Beta2: {comparison.name_2}</sup>",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1))

    if export:
        os.makedirs(comparison.export_dir, exist_ok=True)
        fig.write_html(os.path.join(
            comparison.export_dir, "delta_beta_map.html"
            ), include_plotlyjs='cdn', include_mathjax='cdn')
        # fig.write_image(os.path.join(
        #     comparison.export_dir, "delta_beta_map.png"
        #     ), format="png", scale=5,  width=1400)

    return fig


def map_ratio_beta_comparison(comparison: ComparisonCollector,
                              export: bool = False) -> go.Figure:
    # load data from class
    gdf_result1 = (comparison.gdf1_uittredepunten[
        ["uittredepunt_id", "beta", "geometry"]
        ].rename(columns={"beta": "beta1"}))
    gdf_result2 = (comparison.gdf2_uittredepunten[
        ["uittredepunt_id", "beta"]].rename(columns={"beta": "beta2"}))
    gdf = gdf_result1.merge(gdf_result2, on="uittredepunt_id")

    gdf["beta_ratio"] = round((gdf["beta1"] / gdf["beta2"]) * 100, 2)

    # Covert to crs for map.
    gdf_latlon = gdf.to_crs("EPSG:4326")

    fig = go.Figure()
    fig.add_trace(go.Scattermap(
        mode="markers",
        lat=gdf_latlon.geometry.y,
        lon=gdf_latlon.geometry.x,
        marker=dict(
            size=9,
            color="black"
            ),
        showlegend=False
        ))
    hoverdata = ["uittredepunt_id", "beta_ratio", "beta1", "beta2"]
    fig.add_trace(go.Scattermap(
        mode="markers",
        lat=gdf_latlon.geometry.y,
        lon=gdf_latlon.geometry.x,
        marker=dict(
            size=8,
            color=gdf_latlon["beta_ratio"],
            cmax=200,
            cmin=0,
            colorscale="RdYlGn",
            colorbar=dict(title="Beta Ratio - Beta1/Beta2 [%]"),
        ),
        hoverinfo='text',
        text=gdf_latlon[hoverdata].apply(
            lambda row: '<br>'.join(
                [f"{col}: {round(row[col], 3)}" for col in hoverdata]
                ),
            axis=1),
        showlegend=False
        ))

    fig = _add_line(comparison, fig, "dijktraject", "black")
    fig = _add_line(comparison, fig, "intredelijn", "blue")
    fig = _add_line(comparison, fig, "binnenteenlijn", "red")
    fig = _add_line(comparison, fig, "buitenteenlijn", "red")

    zoom = _determine_zoom(gdf_latlon)
    fig.update_layout(
        map_style="open-street-map",
        # carto-positron, open-street-map, satellite-streets
        map_zoom=zoom,
        map_center=dict(
            lat=gdf_latlon.geometry.y.mean(),
            lon=gdf_latlon.geometry.x.mean()
        ),
        dragmode="zoom",
        title=f"Beta ratio van uittredepunten tussen<br>" +
              f"<sup>Beta1: {comparison.name_1} en Beta2: {comparison.name_2}</sup>",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
            )
        )
    if export:
        os.makedirs(comparison.export_dir, exist_ok=True)
        fig.write_html(os.path.join(
            comparison.export_dir, "ratio_beta_map.html"
            ), include_plotlyjs='cdn', include_mathjax='cdn')
        # fig.write_image(os.path.join(
        #     comparison.export_dir, "ratio_beta_map.png"
        #     ), format="png", scale=5,  width=1400)

    return fig
