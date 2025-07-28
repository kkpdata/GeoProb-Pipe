# import os
# import random
# from typing import Union, Literal
# import sys
#
# # rgb(153,204,0)
#
#
# # class Tags:
# #
# #     def __init__(self, main_tag: str):
# #         self.main_tag: str = main_tag
# #
# #     @property
# #     def beta(self):
# #         return
# #
#
#
#
#
# class VisualizeInfo:
#
#     def __init__(self, main_tag: str, beta: Union[float, int, str] = "n.b.", visible: bool = False):
#         self.main_tag: str = main_tag
#         self.beta: Union[float, int, str] = beta
#         self.visible: bool = visible
#
#     @property
#     def svg_color(self) -> str:
#         """ Color value formatted for the SVG-file. """
#         if self.beta > 5.00:
#             return "rgb(154,205,50)"  # Green
#         return "rgb(206,32,41)"  # Red
#
#     @property
#     def svg_beta(self) -> str:
#         """ Beta value formatted for the SVG-file. """
#         if isinstance(self.beta, float) or isinstance(self.beta, int):
#             return f"{round(self.beta, 2):.2f}"
#         return str(self.beta)
#
#     @property
#     def svg_visibility(self):
#         """ Visibility value formatted for the SVG-file. """
#         if self.visible:
#             return "visible"
#         return "hidden"
#
#     def svg_tag(self, option: Literal["beta", "color", "visibility"]) -> str:
#         return f"{self.main_tag}.{option}"
#
#     def svg_tag_incl_brackets(self, option: Literal["beta", "color", "visibility"]) -> str:
#         return f"{{{{ {self.svg_tag(option=option)} }}}}"
#
#
# list_visualize_info = [
#     VisualizeInfo(main_tag=, beta=random.random() * 7 + 2, visible=True),
# ]
#
# dict_visualize_info = {
#     "uplift": VisualizeInfo(main_tag="uplift", beta=random.random() * 7 + 2, visible=True),
#     "heave": VisualizeInfo(main_tag="heave", beta=random.random() * 7 + 2, visible=True),
#     "piping": VisualizeInfo(main_tag="piping", beta=random.random() * 7 + 2, visible=True),
#     "scenarios.1": VisualizeInfo(main_tag="scenarios.1", beta=random.random() * 7 + 2, visible=True),
#     "scenarios.2": VisualizeInfo(main_tag="scenarios.2", beta=random.random() * 7 + 2),
# }
#
#
#
#
#
# def generate_overview_flow_chart_with_betas(scenario, uittredepunt):
#     """ Generates a flow chart that provides an overview what the beta values are per step in the calculation process.
#     It displays it from the given scenario and uittredepunt, until vak- and traject-level. """
#
#
#     tags = {
#         "uplift": VisualInfo(random.random() * 7 + 2, True),
#         "heave": VisualInfo(random.random() * 7 + 2, True),
#         "piping": VisualInfo(random.random() * 7 + 2, True),
#         "scenarios": {
#             1: VisualInfo(random.random() * 7 + 2),
#             2: VisualInfo(random.random() * 7 + 2),
#             3: VisualInfo(random.random() * 7 + 2),
#             4: VisualInfo(random.random() * 7 + 2),
#             5: VisualInfo(random.random() * 7 + 2),
#             6: VisualInfo(random.random() * 7 + 2),
#             7: VisualInfo(random.random() * 7 + 2),
#         },
#         "uittredepunten": {
#             1: VisualInfo(random.random() * 7 + 2),
#             2: VisualInfo(random.random() * 7 + 2),
#             3: VisualInfo(random.random() * 7 + 2),
#             4: VisualInfo(random.random() * 7 + 2),
#             5: VisualInfo(random.random() * 7 + 2),
#             6: VisualInfo(random.random() * 7 + 2),
#             7: VisualInfo(random.random() * 7 + 2),
#         },
#         "vakken": {
#             1: VisualInfo(random.random() * 7 + 2),
#             2: VisualInfo(random.random() * 7 + 2),
#             3: VisualInfo(random.random() * 7 + 2),
#             4: VisualInfo(random.random() * 7 + 2),
#             5: VisualInfo(random.random() * 7 + 2),
#             6: VisualInfo(random.random() * 7 + 2),
#             7: VisualInfo(random.random() * 7 + 2),
#         },
#         "traject": VisualInfo(random.random() * 7 + 2),
#
#     }
#
#     # Apply visual and value to each circle
#     concatenated_tags = []
#     values_to_concatenated_tags = []
#     visibility_to_concatenated_tags = []
#     for key, value in tags.items():
#
#         print(f"{key=}, {value=}")
#
#
#         # Determine tag .-string
#         if isinstance(value, VisualInfo):
#             tag_beta = f"{key}.beta"
#             value_beta = value.beta
#             tag_color = f"{key}.color"
#             value_color = value.color
#
#             concatenated_tags.append(tag_beta)
#             values_to_concatenated_tags.append(value_beta)
#             concatenated_tags.append(tag_color)
#             values_to_concatenated_tags.append(value_color)
#
#         elif isinstance(value, dict):
#             # print(f"{concatenated_tags=}")
#             # print(f"{values_to_concatenated_tags=}")
#             # sys.exit()
#             for key2, value2 in value.items():
#                 # print(f"{key2=}, {value2=}")
#                 value2: VisualInfo
#                 tag_beta = f"{key}.{key2}.beta"
#                 # print(f"{value2=}")
#                 value_beta = value2.beta
#                 tag_color = f"{key}.{key2}.color"
#                 value_color = value2.color
#
#                 concatenated_tags.append(tag_beta)
#                 values_to_concatenated_tags.append(value_beta)
#                 concatenated_tags.append(tag_color)
#                 values_to_concatenated_tags.append(value_color)
#
#         else:
#             raise ValueError
#
#     # Read template
#     svg_text = None
#     with open(r"C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV2\GeoProb-Pipe\geoprob_pipe\graphs\overview\Hierarchie_berekeningen_incl_result_tags.svg",
#               "r", encoding="utf-8") as f:
#         svg_text = f.read()
#     if svg_text is None:
#         raise ValueError
#
#     # Replace tags
#     for tag, value in zip(concatenated_tags, values_to_concatenated_tags):
#
#         # Prepare tag to search
#         tag_with_brackets = f"{{{{ {tag} }}}}"
#         print(f"{tag_with_brackets=}", tag_with_brackets in svg_text)
#
#         # Prepare value to add
#         if isinstance(value, float) or isinstance(value, int):
#             value_prepped = f"{round(value, 2):.2f}"
#         else:
#             value_prepped = str(value)
#
#         # Add value and color
#         svg_text = svg_text.replace(tag_with_brackets, value_prepped)
#
#     # Save new svg
#     print(f"{svg_text=}")
#     export_dir = r"C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV2\exports"
#     with open(os.path.join(export_dir, "updated5.svg"), "w", encoding="utf-8") as f:
#         f.write(svg_text)
#
#     return concatenated_tags, values_to_concatenated_tags
#
#
# generate_overview_flow_chart_with_betas(1, 2)
