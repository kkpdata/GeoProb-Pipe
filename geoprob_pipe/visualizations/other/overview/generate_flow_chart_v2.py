from __future__ import annotations
import os
from typing import Union, Literal
from pandas import DataFrame, Series
from copy import deepcopy
from geoprob_pipe.utils.other import repository_root_path
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe



class VisualizeInfo:

    def __init__(self, main_tag: str, beta: Union[float, int, str] = "n.b.", visible: bool = False):
        self.main_tag: str = main_tag
        self.beta: Union[float, int, str] = beta
        self.visible: bool = visible

    @property
    def svg_color(self) -> str:
        """ Color value formatted for the SVG-file. """
        if self.beta > 5.00:
            return "rgb(154,205,50)"  # Green
        return "rgb(206,32,41)"  # Red

    @property
    def svg_beta(self) -> str:
        """ Beta value formatted for the SVG-file. """
        if isinstance(self.beta, float) or isinstance(self.beta, int):
            if self.beta >= 10.0:
                return f"{round(self.beta, 1):.1f}"
            return f"{round(self.beta, 2):.2f}"
        return str(self.beta)

    @property
    def svg_visibility(self):
        """ Visibility value formatted for the SVG-file. """
        if self.visible:
            return "visible"
        return "hidden"

    def svg_tag(self, option: Literal["beta", "color", "visibility"]) -> str:
        return f"{self.main_tag}.{option}"

    def svg_tag_incl_brackets(self, option: Literal["beta", "color", "visibility"]) -> str:
        return f"{{{{ {self.svg_tag(option=option)} }}}}"


DICT_VISUALIZE_INFO = {
    "uplift": VisualizeInfo(main_tag="uplift", beta=-1, visible=True),
    "heave": VisualizeInfo(main_tag="heave", beta=-1, visible=True),
    "piping": VisualizeInfo(main_tag="piping", beta=-1, visible=True),
    "scenario.1": VisualizeInfo(main_tag="scenario.1", beta=-1),
    "scenario.2": VisualizeInfo(main_tag="scenario.2", beta=-1),
    "scenario.3": VisualizeInfo(main_tag="scenario.3", beta=-1),
    "scenario.4": VisualizeInfo(main_tag="scenario.4", beta=-1),
    "scenario.5": VisualizeInfo(main_tag="scenario.5", beta=-1),
    "scenario.6": VisualizeInfo(main_tag="scenario.6", beta=-1),
    "scenario.7": VisualizeInfo(main_tag="scenario.7", beta=-1),
    "scenario.8": VisualizeInfo(main_tag="scenario.8", beta=-1),
    "scenario.9": VisualizeInfo(main_tag="scenario.9", beta=-1),
    "scenario.10": VisualizeInfo(main_tag="scenario.10", beta=-1),
    "scenario.11": VisualizeInfo(main_tag="scenario.11", beta=-1),
    "scenario.12": VisualizeInfo(main_tag="scenario.12", beta=-1),
    "scenario.13": VisualizeInfo(main_tag="scenario.13", beta=-1),
    "scenario.14": VisualizeInfo(main_tag="scenario.14", beta=-1),
    "scenario.15": VisualizeInfo(main_tag="scenario.15", beta=-1),
    "scenario.16": VisualizeInfo(main_tag="scenario.16", beta=-1),
    "scenario.17": VisualizeInfo(main_tag="scenario.17", beta=-1),
    "scenario.18": VisualizeInfo(main_tag="scenario.18", beta=-1),
    "scenario.19": VisualizeInfo(main_tag="scenario.19", beta=-1),
    "scenario.20": VisualizeInfo(main_tag="scenario.20", beta=-1),
    "scenario.99": VisualizeInfo(main_tag="scenario.99", beta=-1),
    "uittredepunt.1": VisualizeInfo(main_tag="uittredepunt.1", beta=-1),
    "uittredepunt.2": VisualizeInfo(main_tag="uittredepunt.2", beta=-1),
    "uittredepunt.3": VisualizeInfo(main_tag="uittredepunt.3", beta=-1),
    "uittredepunt.4": VisualizeInfo(main_tag="uittredepunt.4", beta=-1),
    "uittredepunt.5": VisualizeInfo(main_tag="uittredepunt.5", beta=-1),
    "uittredepunt.6": VisualizeInfo(main_tag="uittredepunt.6", beta=-1),
    "uittredepunt.7": VisualizeInfo(main_tag="uittredepunt.7", beta=-1),
    "uittredepunt.8": VisualizeInfo(main_tag="uittredepunt.8", beta=-1),
    "uittredepunt.9": VisualizeInfo(main_tag="uittredepunt.9", beta=-1),
    "uittredepunt.10": VisualizeInfo(main_tag="uittredepunt.10", beta=-1),
    "uittredepunt.11": VisualizeInfo(main_tag="uittredepunt.11", beta=-1),
    "uittredepunt.12": VisualizeInfo(main_tag="uittredepunt.12", beta=-1),
    "uittredepunt.13": VisualizeInfo(main_tag="uittredepunt.13", beta=-1),
    "uittredepunt.14": VisualizeInfo(main_tag="uittredepunt.14", beta=-1),
    "uittredepunt.15": VisualizeInfo(main_tag="uittredepunt.15", beta=-1),
    "uittredepunt.16": VisualizeInfo(main_tag="uittredepunt.16", beta=-1),
    "uittredepunt.17": VisualizeInfo(main_tag="uittredepunt.17", beta=-1),
    "uittredepunt.18": VisualizeInfo(main_tag="uittredepunt.18", beta=-1),
    "uittredepunt.19": VisualizeInfo(main_tag="uittredepunt.19", beta=-1),
    "uittredepunt.20": VisualizeInfo(main_tag="uittredepunt.20", beta=-1),
    "uittredepunt.21": VisualizeInfo(main_tag="uittredepunt.21", beta=-1),
    "uittredepunt.99": VisualizeInfo(main_tag="uittredepunt.99", beta=-1),
    "vak.1": VisualizeInfo(main_tag="vak.1", beta=-1),
    "vak.2": VisualizeInfo(main_tag="vak.2", beta=-1),
    "vak.3": VisualizeInfo(main_tag="vak.3", beta=-1),
    "vak.4": VisualizeInfo(main_tag="vak.4", beta=-1),
    "vak.5": VisualizeInfo(main_tag="vak.5", beta=-1),
    "vak.6": VisualizeInfo(main_tag="vak.6", beta=-1),
    "vak.7": VisualizeInfo(main_tag="vak.7", beta=-1),
    "vak.8": VisualizeInfo(main_tag="vak.8", beta=-1),
    "vak.9": VisualizeInfo(main_tag="vak.9", beta=-1),
    "vak.10": VisualizeInfo(main_tag="vak.10", beta=-1),
    "vak.11": VisualizeInfo(main_tag="vak.11", beta=-1),
    "vak.12": VisualizeInfo(main_tag="vak.12", beta=-1),
    "vak.13": VisualizeInfo(main_tag="vak.13", beta=-1),
    "vak.14": VisualizeInfo(main_tag="vak.14", beta=-1),
    "vak.15": VisualizeInfo(main_tag="vak.15", beta=-1),
    "vak.16": VisualizeInfo(main_tag="vak.16", beta=-1),
    "vak.17": VisualizeInfo(main_tag="vak.17", beta=-1),
    "vak.18": VisualizeInfo(main_tag="vak.18", beta=-1),
    "vak.19": VisualizeInfo(main_tag="vak.19", beta=-1),
    "vak.20": VisualizeInfo(main_tag="vak.20", beta=-1),
    "vak.21": VisualizeInfo(main_tag="vak.21", beta=-1),
    "vak.99": VisualizeInfo(main_tag="vak.99", beta=-1),
    "traject": VisualizeInfo(main_tag="traject", beta=-1),
}


def populate_visualize_dict(uittredepunt_id: int, ondergrondscenario_id: int, app_obj: GeoProbPipe):

    visualize_dict = deepcopy(DICT_VISUALIZE_INFO)

    # Populate uplift, heave and piping for focus scenario
    df_filter_limit_states = app_obj.results.df_limit_states.copy(deep=True)
    df_filter_limit_states: DataFrame = df_filter_limit_states[
        (df_filter_limit_states["uittredepunt_id"] == uittredepunt_id) &
        (df_filter_limit_states["ondergrondscenario_id"] == ondergrondscenario_id)
    ]
    assert df_filter_limit_states.__len__() == 3
    for row in df_filter_limit_states.itertuples(index=False):
        row: Series
        visualize_dict[row.model].beta = row.beta

    # Populate scenarios results: other scenarios
    df_filter_combined = app_obj.results.df_combined.copy(deep=True)
    df_filter_combined: DataFrame = df_filter_combined[
        (df_filter_combined["uittredepunt_id"] == uittredepunt_id) &
        (df_filter_combined["ondergrondscenario_id"] != ondergrondscenario_id)
    ]
    for index, row in enumerate(df_filter_combined.itertuples(index=False)):
        row: Series
        visualize_dict[f"scenario.{index+2}"].beta = row.beta
        visualize_dict[f"scenario.{index+2}"].visible = True

    # Populate scenarios results: focus scenarios
    df_filter_combined = app_obj.results.df_combined.copy(deep=True)
    df_filter_combined: DataFrame = df_filter_combined[
        (df_filter_combined["uittredepunt_id"] == uittredepunt_id) &
        (df_filter_combined["ondergrondscenario_id"] == ondergrondscenario_id)
    ]
    assert df_filter_combined.__len__() == 1
    for row in df_filter_combined.itertuples(index=False):
        row: Series
        visualize_dict["scenario.1"].beta = row.beta
        visualize_dict["scenario.1"].visible = True

    # Populate vak

    return visualize_dict


def export_flowchart_overview_beta_results(
        geoprob_pipe: GeoProbPipe,
        export: bool = True
):
    """ Generates a flow chart that provides an overview what the beta values are per step in the calculation process.
    It displays it from the given scenario and uittredepunt, until vak- and traject-level. """

    # df = self.geoprob_pipe.results.df_beta_scenarios
    # lowest_beta_row: DataFrame = df.loc[df['beta'].idxmin()]
    # ondergrondscenario_id = lowest_beta_row['ondergrondscenario_id'],
    # uittredepunt_id = lowest_beta_row['uittredepunt_id'],

    dict_to_use = populate_visualize_dict(
        uittredepunt_id=uittredepunt_id, ondergrondscenario_id=ondergrondscenario_id, app_obj=app_obj)

    # Read template
    svg_text = None
    repo_root = repository_root_path()
    path_to_svg = os.path.join(
        repo_root, "geoprob_pipe", "graphs", "overview", "Hierarchie_berekeningen_incl_result_tags_v2.svg")
    with open(path_to_svg, "r", encoding="utf-8") as f:
        svg_text = f.read()
    if svg_text is None:
        raise ValueError

    # Replace tags
    for main_tag, info in dict_to_use.items():
        svg_text = svg_text.replace(info.svg_tag_incl_brackets(option="beta"), info.svg_beta)
        svg_text = svg_text.replace(info.svg_tag_incl_brackets(option="color"), info.svg_color)
        svg_text = svg_text.replace(info.svg_tag_incl_brackets(option="visibility"), info.svg_visibility)

    # Save new svg
    if export:
        export_dir = geoprob_pipe.visualizations.other.export_dir
        with open(os.path.join(export_dir, "results_overview_flow_chart.svg"), "w", encoding="utf-8") as f:
            f.write(svg_text)

    return
