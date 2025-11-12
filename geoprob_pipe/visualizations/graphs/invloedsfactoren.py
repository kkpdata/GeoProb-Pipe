from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import os
from pandas import DataFrame, merge
from geopandas import GeoDataFrame, read_file
from geoprob_pipe.globals import DISTINCTIVE_COLORS
from plotly.graph_objects import Figure, Bar
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def get_plot_order(geoprob_pipe: GeoProbPipe) -> DataFrame:

    # Define plot order
    df: DataFrame = geoprob_pipe.results.df_alphas_influence_factors_and_physical_values(filter_derived=True)
    df = df[["variable", "influence_factor"]]
    df = df.groupby(['variable']).mean()
    df = df.sort_values(by=["influence_factor"], ascending=False)
    df = df.reset_index(drop=False)
    df['plot_order'] = df.index

    # Add colors to plot order
    df_colors = DataFrame({"color": DISTINCTIVE_COLORS})
    df_colors['plot_order'] = df_colors.index
    df = merge(df, df_colors, how="left", on="plot_order")

    return df


def get_influence_factors_for_vak(
        geoprob_pipe: GeoProbPipe, df_invloedsfactoren: DataFrame, vak_id: int
) -> Optional[DataFrame]:
    """ Returns the influence factors for the worst result of a scenario within the vak. May be empty dataframe if
    vak has no results.

    In the past weigh it for the uittredepunt, or average is among all uittredepunten, as was done in the past. The
    choice was made to keep the actual resulting influence factors because they sum up to 100%. There is also no
    physical reason to average them, and the worst case scenario is normative for the final result anyway. """
    df_result = geoprob_pipe.results.df_beta_scenarios
    df_result = df_result[df_result["vak_id"] == vak_id]

    # Check if results for vak
    if df_result.__len__() == 0:
        return None

    df_result = df_result.sort_values(by=["beta"], ascending=True)
    worst_uittredepunt_id = df_result.iloc[0]['uittredepunt_id']
    worst_scenario_id = df_result.iloc[0]['ondergrondscenario_id']
    df = df_invloedsfactoren[
        (df_invloedsfactoren["uittredepunt_id"] == worst_uittredepunt_id) &
        (df_invloedsfactoren["ondergrondscenario_id"] == worst_scenario_id)
    ]
    return df.sort_values(by=["plot_order"])


def invloedsfactoren(geoprob_pipe: GeoProbPipe, export: bool = False) -> Figure:

    # Get data
    df_invloedsfactoren = geoprob_pipe.results.df_alphas_influence_factors_and_physical_values(filter_derived=True)

    # Add plot order
    df_plot_order = get_plot_order(geoprob_pipe=geoprob_pipe)
    df_invloedsfactoren = merge(
        df_invloedsfactoren, df_plot_order[["variable", "plot_order", "color"]], how="left", on="variable")

    # Plot data
    fig = Figure()
    # vakken = {row['vak_id']: row['vak_naam'] for index, row in geoprob_pipe.input_data.vakken.df.iterrows()}
    gdf_vakindeling: GeoDataFrame = read_file(
        geoprob_pipe.input_data.app_settings.geopackage_filepath, layer="vakindeling")
    vakken = {row['vak_id']: row["naam"] for index, row in gdf_vakindeling.iterrows()}
    picked_colors = {}
    added_to_legend = []
    for vak_id, vak_naam in vakken.items():

        # Get invloedsfactoren data
        df_factoren = get_influence_factors_for_vak(geoprob_pipe, df_invloedsfactoren, vak_id)

        # If not results/factors
        if df_factoren is None:
            color = f"rgb{DISTINCTIVE_COLORS[0]}"
            # Add dummy zero value to visualize no results in vak
            # noinspection PyTypeChecker
            fig.add_trace(Bar(
                x=[vak_naam],
                y=[0],
                name="dummy",
                marker_color=color,
                showlegend=False,
            ))
            continue

        # Plot data
        stochasten = df_factoren['variable'].unique().tolist()
        for stochast in stochasten:
            if stochast not in picked_colors.keys():
                color = f"rgb{DISTINCTIVE_COLORS[picked_colors.__len__()]}"
                picked_colors[stochast] = color
            else:
                color = picked_colors[stochast]
            show_legend = False
            if stochast not in added_to_legend:
                added_to_legend.append(stochast)
                show_legend = True
            fig.add_trace(Bar(
                x=[vak_naam],
                y=[df_factoren[df_factoren['variable'] == stochast].iloc[0]['influence_factor'] * 100],
                name=stochast,
                marker_color=color,
                showlegend=show_legend,
                legendgroup=stochast,
            ))

    # Layout styling
    fig.update_layout(
        barmode='stack',
        bargap=0,       # Geen ruimte tussen groepen
        bargroupgap=0,  # Geen ruimte tussen individuele bars binnen een groep
        title='Invloedsfactoren<br>'
              '<sup>Invloedsfactoren zijn van het worstcase ondergrondscenario en uittredepunt.</sup>',
        xaxis_title='Vak',
        yaxis=dict(
            # range=[0, 100],
            title="Percentage",
        ),  # Pas dit aan naar jouw gewenste bereik
    )

    # Export
    if export:
        export_dir = geoprob_pipe.visualizations.graphs.export_dir
        os.makedirs(export_dir, exist_ok=True)
        fig.write_html(os.path.join(export_dir, f"invloedsfactoren.html"), include_plotlyjs='cdn')
        if geoprob_pipe.software_requirements.chrome_is_installed:
            fig.write_image(os.path.join(export_dir, f"invloedsfactoren.png"), format="png")


    # for stochast in
    return fig
