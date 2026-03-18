from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Tuple
import os
from pandas import DataFrame, merge
from geopandas import GeoDataFrame, read_file
from plotly.graph_objects import Figure, Bar
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


DISTINCTIVE_COLORS = [
    '(60, 180, 75)', '(230, 25, 75)', '(255, 225, 25)', '(0, 130, 200)', '(245, 130, 48)', '(145, 30, 180)',
    '(70, 240, 240)', '(240, 50, 230)', '(210, 245, 60)', '(250, 190, 212)', '(0, 128, 128)',
    '(220, 190, 255)', '(170, 110, 40)', '(255, 250, 200)', '(128, 0, 0)', '(170, 255, 195)',
    '(128, 128, 0)', '(255, 215, 180)', '(128, 128, 128)', '(255, 255, 255)']


def get_plot_order(geoprob_pipe: GeoProbPipe) -> DataFrame:
    """ Assigns color codes (indices) and color rgb-values to each stochast such that they can be plotted with the
    same color and same order.

    :param geoprob_pipe:
    :return: DataFrame with columns 'variable', 'plot_order' and 'color'
    """

    # Define plot order
    df: DataFrame = geoprob_pipe.results.df_alphas_influence_factors_and_physical_values(filter_derived=True)
    df = df[["variable", "influence_factor"]]
    df = df.groupby(['variable']).mean()  # Influence factor average value define color order
    df = df.sort_values(by=["influence_factor"], ascending=False)
    df = df.reset_index(drop=False)
    df['plot_order'] = df.index  # Result is df with columns 'variable', 'influence_factor' (average), 'plot_order'

    # Add colors to plot order
    df_colors = DataFrame({"color": DISTINCTIVE_COLORS})  # Convert to dict to df for ease of use
    df_colors['plot_order'] = df_colors.index
    df = merge(df, df_colors, how="left", on="plot_order")

    return df


def _get_method_used(geoprob_pipe: GeoProbPipe, worst_uittredepunt_id: int, worst_scenario_id: str):
    df_scenario_final: DataFrame = geoprob_pipe.results.df_beta_scenarios_final
    df_scenario_final = df_scenario_final[
        (df_scenario_final["uittredepunt_id"] == worst_uittredepunt_id) &
        (df_scenario_final["ondergrondscenario_id"] == worst_scenario_id)
    ]
    assert df_scenario_final.__len__() == 1

    method_used_str: str = df_scenario_final['method_used'].iloc[0]
    method_used_nr = int(method_used_str[0])

    # If Combine Project or Reliability Project
    if method_used_nr == 1:
        return "CP"
    if method_used_nr == 2:
        return "RP"

    # Else look up which Limit State Triggered
    df_limit_states: DataFrame = geoprob_pipe.results.df_beta_limit_states
    df_limit_states = df_limit_states[
        (df_limit_states["uittredepunt_id"] == worst_uittredepunt_id) &
        (df_limit_states["ondergrondscenario_id"] == worst_scenario_id)
    ]
    assert df_limit_states.__len__() == 3
    df_limit_states = df_limit_states.sort_values(by=["beta"], ascending=False)
    limit_state_used = df_limit_states["limit_state"].iloc[0]
    possible_return_values = {"calc_Z_u": "Zu", "calc_Z_h": "Zh", "calc_Z_p": "Zp"}
    return possible_return_values[limit_state_used]


def get_influence_factors_for_vak(
        geoprob_pipe: GeoProbPipe, df_invloedsfactoren: DataFrame, vak_id: int
) -> Tuple[Optional[DataFrame], int, str, str]:
    """ Returns the influence factors for the worst result of a scenario within the vak. May be empty dataframe if
    vak has no results.

    In the past weigh it for the uittredepunt, or average is among all uittredepunten, as was done in the past. The
    choice was made to keep the actual resulting influence factors because they sum up to 100%. There is also no
    physical reason to average them, and the worst case scenario is normative for the final result anyway.

    :param geoprob_pipe:
    :param df_invloedsfactoren:
    :param vak_id:
    :return: Influence factors, worst case uittredepunt ID, worst case scenario label and method used.
    """
    """  """
    df_result = geoprob_pipe.results.df_beta_scenarios_final
    df_result = df_result[df_result["vak_id"] == vak_id]

    # Check if results for vak
    if df_result.__len__() == 0:
        return None, -1, "", ""

    df_result = df_result.sort_values(by=["beta"], ascending=True)
    worst_uittredepunt_id = df_result.iloc[0]['uittredepunt_id']
    worst_scenario_id = df_result.iloc[0]['ondergrondscenario_id']
    df = df_invloedsfactoren[
        (df_invloedsfactoren["uittredepunt_id"] == worst_uittredepunt_id) &
        (df_invloedsfactoren["ondergrondscenario_id"] == worst_scenario_id)]
    df = df.sort_values(by=["plot_order"])

    # Determine method used
    method_used = _get_method_used(
        geoprob_pipe=geoprob_pipe, worst_uittredepunt_id=worst_uittredepunt_id, worst_scenario_id=worst_scenario_id)
    mapper = {"Zp": "3: Max Limit States (calc_Z_p)", "Zu": "3: Max Limit States (calc_Z_u)",
              "Zh": "3: Max Limit States (calc_Z_h)", "CP": "1: Combine Project", "RP": "2: Reliability Project"}
    df = df[df["design_point"] == mapper[method_used]]

    return df, worst_uittredepunt_id, worst_scenario_id, method_used


def _get_data(geoprob_pipe: GeoProbPipe) -> DataFrame:
    # Get data
    df_invloedsfactoren = geoprob_pipe.results.df_alphas_influence_factors_and_physical_values(filter_derived=True)

    # Add plot order
    df_plot_order = get_plot_order(geoprob_pipe=geoprob_pipe)
    df_invloedsfactoren = merge(
        df_invloedsfactoren, df_plot_order[["variable", "plot_order", "color"]], how="left", on="variable")

    return df_invloedsfactoren


def _plot_data(geoprob_pipe: GeoProbPipe, df_invloedsfactoren: DataFrame) -> Figure:
    fig = Figure()
    gdf_vakindeling: GeoDataFrame = read_file(
        geoprob_pipe.input_data.app_settings.geopackage_filepath, layer="vakindeling")
    vakken = {row['id']: row["naam"] for index, row in gdf_vakindeling.iterrows()}
    picked_colors = {}
    added_to_legend = []
    for vak_id, vak_naam in vakken.items():

        # Get invloedsfactoren data
        df_factoren, worst_uittredepunt_id, worst_scenario_id, method_used = get_influence_factors_for_vak(
            geoprob_pipe=geoprob_pipe, df_invloedsfactoren=df_invloedsfactoren, vak_id=vak_id)
        vak_has_results = worst_uittredepunt_id != -1
        x_axis_label = f"{vak_id}"
        if vak_has_results:
            x_axis_label = f"{vak_id} ({worst_uittredepunt_id}, {worst_scenario_id})"

        # If not results/factors
        if df_factoren is None:
            color = f"rgb{DISTINCTIVE_COLORS[0]}"
            # Add dummy zero value to visualize no results in vak
            # noinspection PyTypeChecker
            fig.add_trace(Bar(x=[x_axis_label], y=[0], name="dummy", marker_color=color, showlegend=False))
            continue

        # Plot data
        stochasten = df_factoren['variable'].unique().tolist()
        for index, stochast in enumerate(stochasten):
            if stochast not in picked_colors.keys():
                color = f"rgb{DISTINCTIVE_COLORS[picked_colors.__len__()]}"
                picked_colors[stochast] = color
            else:
                color = picked_colors[stochast]
            show_legend = False
            if stochast not in added_to_legend:
                added_to_legend.append(stochast)
                show_legend = True

            # Plot, including label?
            if index + 1 == stochasten.__len__():
                fig.add_trace(Bar(
                    x=[x_axis_label],
                    y=[df_factoren[df_factoren['variable'] == stochast].iloc[0]['influence_factor'] * 100],
                    text=method_used, textposition='outside',
                    name=stochast, marker_color=color, showlegend=show_legend, legendgroup=stochast))
            else:
                fig.add_trace(Bar(
                    x=[x_axis_label],
                    y=[df_factoren[df_factoren['variable'] == stochast].iloc[0]['influence_factor'] * 100],
                    name=stochast, marker_color=color, showlegend=show_legend, legendgroup=stochast))

    return fig


def _update_layout(fig: Figure) -> Figure:
    fig.update_layout(
        barmode='stack',
        bargap=0,       # Geen ruimte tussen groepen
        bargroupgap=0,  # Geen ruimte tussen individuele bars binnen een groep
        title='Invloedsfactoren<br>'
              '<sup>Invloedsfactoren zijn van de worstcase Beta (combinatie uittredepunt en ondergrondscenario, '
              'zie x-axis label). De labels boven de barchart (CP, RP, Zu, Zh of Zp) zijn een verwijzing naar de '
              'gebruikte design points.</sup>',
        xaxis_title='Vak ID',
        yaxis=dict(title="Percentage", ticksuffix="%"))
    return fig


def invloedsfactoren(geoprob_pipe: GeoProbPipe, export: bool = False) -> Figure:

    # Logic
    df_invloedsfactoren = _get_data(geoprob_pipe=geoprob_pipe)
    fig = _plot_data(geoprob_pipe=geoprob_pipe, df_invloedsfactoren=df_invloedsfactoren)
    fig = _update_layout(fig=fig)

    # Export
    if export:
        export_dir = geoprob_pipe.visualizations.graphs.export_dir
        os.makedirs(export_dir, exist_ok=True)
        fig.write_html(os.path.join(export_dir, f"invloedsfactoren.html"), include_plotlyjs='cdn')

    # for stochast in
    return fig
