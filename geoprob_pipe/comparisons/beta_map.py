import plotly.graph_objects as go
from geoprob_pipe.comparisons.comparison_collector import ComparisonCollecter


def _determine_zoom(gdf_latlon):
        center_lat = gdf_latlon.geometry.y.mean()
        center_lon = gdf_latlon.geometry.x.mean()
        min_lat = gdf_latlon.geometry.y.min()
        max_lat = gdf_latlon.geometry.y.max()
        min_lon = gdf_latlon.geometry.x.min()
        max_lon = gdf_latlon.geometry.x.max()

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

        lat_range = max_lat - min_lat
        lon_range = max_lon - min_lon
        zoom = _calculate_zoom(lat_range, lon_range)
        return zoom


def map_beta_comparison(comparison: ComparisonCollecter):
    # load data from class
    gdf_result1 = (comparison.gdf1_uittredepunten[
        ["uittredepunt_id", "beta", "geometry"]]
                   .rename(columns={"beta": "beta1"}))
    gdf_result2 = (comparison.gdf2_uittredepunten[
        ["uittredepunt_id", "beta"]].rename(columns={"beta": "beta2"}))
    gdf = gdf_result1.merge(gdf_result2, on="uittredepunt_id")
    gdf["beta_delta"] = gdf["beta1"] - gdf["beta2"]
    # gdf["beta_ratio"] = (gdf["beta1"] - gdf["beta2"]) / gdf["beta1"]

    # Covert to crs for map.
    gdf_latlon = gdf.to_crs("EPSG:4326")

    fig = go.Figure()
    hoverdata = ["uittredepunt_id", "beta_delta"]
    fig.add_trace(go.Scattermap(
        mode="markers",
        lat=gdf_latlon.geometry.y,
        lon=gdf_latlon.geometry.x,
        marker=dict(
            size=8,
            color=gdf_latlon["beta_delta"],
            cmax=20,
            cmin=-20,
            colorscale="Turbo_r",
            colorbar=dict(
                title="Delta Beta"
            )
        ),
        hoverinfo='text',
        text=gdf_latlon[hoverdata].apply(
            lambda row: '<br>'.join(
                [f"{col}: {row[col]}" for col in hoverdata]
                ),
            axis=1),
        showlegend=False
        ))

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
        title="Delta beta uittredepunt tussen<br>" +
        f"{comparison.name_1} en {comparison.name_2}"
        )
    fig.show()
    return
