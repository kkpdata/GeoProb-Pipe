from __future__ import annotations
from pandas import DataFrame
from typing import TYPE_CHECKING, Optional
from geoprob_pipe.results.construct_dataframes import (
    combine_df_beta_per_limit_state, collect_df_beta_scenario_rp, collect_df_beta_scenario_cp,
    collect_df_beta_scenario_final, calculate_df_beta_per_uittredepunt, construct_df_beta_per_vak)
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
        self.df_beta_scenarios_cp = combine_df_beta_per_scenario_cp(geoprob_pipe.calc_results)
        self.df_beta_scenarios_final = combine_df_beta_per_scenario_final(geoprob_pipe.calc_results)
        self._df_alphas_influence_factors_and_physical_values: Optional[DataFrame] = None
        self.df_beta_uittredepunten = calculate_df_beta_per_uittredepunt(geoprob_pipe=geoprob_pipe, results=self)
        self.df_beta_vakken = construct_df_beta_per_vak(self)

    def df_alphas_influence_factors_and_physical_values(
            self,
            system_only: bool = True,
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
        if system_only:
            df = df[df['design_point'] == "system"]
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
