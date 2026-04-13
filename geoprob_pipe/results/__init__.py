from __future__ import annotations
from pandas import DataFrame
from typing import TYPE_CHECKING, Optional
from geoprob_pipe.results.construct_dataframes import (
    combine_df_beta_per_limit_state, combine_df_beta_per_scenario_rp, combine_df_beta_per_scenario_cp,
    combine_df_beta_per_scenario_final, calculate_df_beta_per_uittredepunt, construct_df_beta_per_vak)
from geoprob_pipe.results.alphas_and_physical_values import construct_df
import os
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


class Results:
    """ Subclass to intuitively group the results. """

    def __init__(self, geoprob_pipe: GeoProbPipe):
        self.geoprob_pipe = geoprob_pipe
        self.df_beta_limit_states = combine_df_beta_per_limit_state(geoprob_pipe.calc_results)
        self.df_beta_scenarios_rp = combine_df_beta_per_scenario_rp(geoprob_pipe.calc_results)
        # Scenario calculations as a single Reliability Project.
        self.df_beta_scenarios_cp = combine_df_beta_per_scenario_cp(geoprob_pipe.calc_results)
        # Scenario calculations as a single Combine Project.
        self.df_beta_scenarios_final = combine_df_beta_per_scenario_final(geoprob_pipe.calc_results)
        # Worst result from scenario calculations, either combine project, reliability project or max of limit states.
        self._df_alphas_influence_factors_and_physical_values: Optional[DataFrame] = None
        self.df_beta_uittredepunten = calculate_df_beta_per_uittredepunt(geoprob_pipe=geoprob_pipe, results=self)
        self.df_beta_vakken = construct_df_beta_per_vak(self)

    def df_alphas_influence_factors_and_physical_values(
            self,
            filter_deterministic: bool = True,
            filter_derived: bool = False,
    ) -> DataFrame:

        # Generate if not generated yet
        if self._df_alphas_influence_factors_and_physical_values is None:
            self._df_alphas_influence_factors_and_physical_values = (
                construct_df(self.geoprob_pipe))

        # Filters
        df = self._df_alphas_influence_factors_and_physical_values
        if filter_deterministic:
            df = df[df['distribution_type'] != "deterministic"]
        if filter_derived:
            df = df[df['distribution_type'] != "derived"]

        return df

    @property
    def export_dir(self) -> str:
        path: str = os.path.join(
            self.geoprob_pipe.input_data.app_settings.workspace_dir,
            "exports",
            str(self.geoprob_pipe.input_data.app_settings.datetime_stamp),
            "results")
        os.makedirs(path, exist_ok=True)
        return path

    def export_results(
            self,
            bool_beta_limit_states: bool = True,
            bool_beta_scenarios_rp: bool = True,
            bool_beta_scenarios_cp: bool = True,
            bool_beta_scenarios_final: bool = True,
            bool_alphas_influence_factors_and_physical_values: bool = True,
            bool_beta_uittredepunten: bool = True,
            bool_beta_vakken: bool = True):

        # Results of limit state calculations
        if bool_beta_limit_states:
            df = self.df_beta_limit_states
            # TODO Nu Must Klein: Voor export df_beta_limit_states, kolommen filteren?
            df.to_excel(excel_writer=os.path.join(self.export_dir, "df_beta_limit_states.xlsx"))
            # TODO Nu Should Klein: Sommige resultaten zijn niet converged. Wat doen we daarmee?
            #  Op dit moment worden ze gewoon gebruikt om de scenario-faalkans te berekenen.

        if bool_beta_scenarios_rp:
            df = self.df_beta_scenarios_rp
            df.to_excel(excel_writer=os.path.join(self.export_dir, "df_beta_scenarios_rp.xlsx"))

        if bool_beta_scenarios_cp:
            df = self.df_beta_scenarios_cp
            df.to_excel(excel_writer=os.path.join(self.export_dir, "df_beta_scenarios_cp.xlsx"))

        if bool_beta_scenarios_final:
            df = self.df_beta_scenarios_final
            df.to_excel(excel_writer=os.path.join(self.export_dir, "df_beta_scenarios_final.xlsx"))

        if bool_alphas_influence_factors_and_physical_values:
            df = self.df_alphas_influence_factors_and_physical_values()
            df.to_excel(
                excel_writer=os.path.join(self.export_dir, "df_alphas_influence_factors_and_physical_values.xlsx"))

        if bool_beta_uittredepunten:
            self.df_beta_uittredepunten.to_excel(
                excel_writer=os.path.join(self.export_dir, "df_beta_uittredepunten.xlsx"))

        if bool_beta_vakken:
            self.df_beta_vakken.to_excel(excel_writer=os.path.join(self.export_dir, "df_beta_vakken.xlsx"))


# Traceback (most recent call last):
#   File "C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV4\GeoProb-Pipe\geoprob_pipe\calculations\systems\build_and_run.py", line 93, in _worker
#     calc = _BUILDER.build_instance(row_unique=row_unique)
#            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV4\GeoProb-Pipe\geoprob_pipe\calculations\systems\base_objects\base_system_build.py", line 104, in build_instance
#     calc = _generate_single_calculation(
#            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV4\GeoProb-Pipe\geoprob_pipe\calculations\systems\base_objects\base_system_build.py", line 62, in _generate_single_calculation
#     calculation_input = _gather_calculation_input(
#                         ^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV4\GeoProb-Pipe\geoprob_pipe\calculations\systems\base_objects\base_system_build.py", line 47, in _gather_calculation_input
#     df['parameter_input'] = df.apply(
#                             ^^^^^^^^^
#   File "C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV4\.venv\Lib\site-packages\pandas\core\frame.py", line 10401, in apply
#     return op.apply().__finalize__(self, method="apply")
#            ^^^^^^^^^^
#   File "C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV4\.venv\Lib\site-packages\pandas\core\apply.py", line 916, in apply
#     return self.apply_standard()
#            ^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV4\.venv\Lib\site-packages\pandas\core\apply.py", line 1063, in apply_standard
#     results, res_index = self.apply_series_generator()
#                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV4\.venv\Lib\site-packages\pandas\core\apply.py", line 1081, in apply_series_generator
#     results[i] = self.func(v, *self.args, **self.kwargs)
#                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV4\GeoProb-Pipe\geoprob_pipe\calculations\systems\base_objects\base_system_build.py", line 48, in <lambda>
#     lambda row2: {**row2['parameter_input'], 'name': row2['parameter_name']}, axis=1)
#                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# TypeError: 'float' object is not a mapping