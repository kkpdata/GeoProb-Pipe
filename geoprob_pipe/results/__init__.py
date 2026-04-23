from __future__ import annotations
from pandas import DataFrame
from typing import TYPE_CHECKING, Optional
from geoprob_pipe.results.construct_dataframes import (
    combine_df_beta_per_limit_state,
    combine_df_beta_per_scenario_cp,
    combine_df_beta_per_scenario_rp,
    combine_df_beta_per_scenario_final,
    calculate_df_beta_per_uittredepunt,
    construct_df_beta_wbi_vak,
    construct_df_beta_window_vak,
    construct_df_beta_scaled_vak,
    construct_df_beta_per_traject,
    construct_df_beta_window_traject,
    construct_df_beta_scaled_traject)
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
        self.df_beta_uittredepunten = calculate_df_beta_per_uittredepunt(
            geoprob_pipe=geoprob_pipe, results=self
            )
        self.df_beta_WBI_vakken = construct_df_beta_wbi_vak(
            geoprob_pipe=geoprob_pipe, results=self
            )
        self.df_beta_window50m_vakken = construct_df_beta_window_vak(
            geoprob_pipe=geoprob_pipe, results=self, window_size=50.0)
        self.df_beta_window100m_vakken = construct_df_beta_window_vak(
            geoprob_pipe=geoprob_pipe, results=self, window_size=100.0)
        self.df_beta_window200m_vakken = construct_df_beta_window_vak(
            geoprob_pipe=geoprob_pipe, results=self, window_size=200.0)
        self.df_beta_window300m_vakken = construct_df_beta_window_vak(
            geoprob_pipe=geoprob_pipe, results=self, window_size=300.0)
        self.df_beta_scaled_vakken = construct_df_beta_scaled_vak(
            geoprob_pipe=geoprob_pipe, results=self
        )
        self.df_beta_traject = construct_df_beta_per_traject(
            geoprob_pipe=geoprob_pipe, results=self
            )
        self.df_beta_window50m_traject = construct_df_beta_window_traject(
            geoprob_pipe=geoprob_pipe, results=self, window_size=50.0)
        self.df_beta_window100m_traject = construct_df_beta_window_traject(
            geoprob_pipe=geoprob_pipe, results=self, window_size=100.0)
        self.df_beta_window200m_traject = construct_df_beta_window_traject(
            geoprob_pipe=geoprob_pipe, results=self, window_size=200.0)
        self.df_beta_window300m_traject = construct_df_beta_window_traject(
            geoprob_pipe=geoprob_pipe, results=self, window_size=300.0)
        self.df_beta_scaled_traject = construct_df_beta_scaled_traject(
            geoprob_pipe=geoprob_pipe, results=self
            )

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
            str(self.geoprob_pipe.input_data.app_settings.workspace_dir),
            "exports",
            str(self.geoprob_pipe.input_data.app_settings.datetime_stamp),
            "results")
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def export_dir_vakken(self) -> str:
        path: str = os.path.join(
            str(self.geoprob_pipe.input_data.app_settings.workspace_dir),
            "exports",
            str(self.geoprob_pipe.input_data.app_settings.datetime_stamp),
            "results/vakken")
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def export_dir_traject(self) -> str:
        path: str = os.path.join(
            str(self.geoprob_pipe.input_data.app_settings.workspace_dir),
            "exports",
            str(self.geoprob_pipe.input_data.app_settings.datetime_stamp),
            "results/alternatieve methoden")
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
            bool_beta_vakken: bool = True,
            bool_beta_alternative_vakken: bool = False,
            bool_beta_traject: bool = True):

        # Results of limit state calculations
        if bool_beta_limit_states:
            df = self.df_beta_limit_states
            df.to_excel(excel_writer=os.path.join(self.export_dir, "df_beta_limit_states.xlsx"), index=False)

        if bool_beta_scenarios_rp:
            df = self.df_beta_scenarios_rp
            df.to_excel(excel_writer=os.path.join(self.export_dir, "df_beta_scenarios_rp.xlsx"), index=False)

        if bool_beta_scenarios_cp:
            df = self.df_beta_scenarios_cp
            df.to_excel(excel_writer=os.path.join(self.export_dir, "df_beta_scenarios_cp.xlsx"), index=False)

        if bool_beta_scenarios_final:
            df = self.df_beta_scenarios_final
            df.to_excel(excel_writer=os.path.join(self.export_dir, "df_beta_scenarios_final.xlsx"), index=False)

        if bool_alphas_influence_factors_and_physical_values:
            df = self.df_alphas_influence_factors_and_physical_values()
            df.to_excel(
                excel_writer=os.path.join(self.export_dir, "df_alphas_influence_factors_and_physical_values.xlsx"),
                index=False)

        if bool_beta_uittredepunten:
            self.df_beta_uittredepunten.to_excel(
                excel_writer=os.path.join(self.export_dir, "df_beta_uittredepunten.xlsx"), index=False)

        if bool_beta_vakken:
            self.df_beta_WBI_vakken.to_excel(
                excel_writer=os.path.join(
                    self.export_dir, "df_beta_vakken.xlsx"))
            if bool_beta_alternative_vakken:
                self.df_beta_window50m_vakken.to_excel(
                    excel_writer=os.path.join(
                        self.export_dir_vakken, "df_beta_window50m_vakken.xlsx"))
                self.df_beta_window100m_vakken.to_excel(
                    excel_writer=os.path.join(
                        self.export_dir_vakken, "df_beta_window100m_vakken.xlsx"))
                self.df_beta_window200m_vakken.to_excel(
                    excel_writer=os.path.join(
                        self.export_dir_vakken, "df_beta_window200m_vakken.xlsx"))
                self.df_beta_window300m_vakken.to_excel(
                    excel_writer=os.path.join(
                        self.export_dir_vakken, "df_beta_window300m_vakken.xlsx"))
                self.df_beta_scaled_vakken.to_excel(
                    excel_writer=os.path.join(
                        self.export_dir_vakken, "df_beta_scaled_vakken.xlsx"))

        if bool_beta_traject:
            self.df_beta_traject.to_excel(
                excel_writer=os.path.join(self.export_dir,
                                          "df_beta_traject.xlsx"))
            self.df_beta_window50m_traject.to_excel(
                excel_writer=os.path.join(self.export_dir_traject,
                                          "df_beta_window50m_traject.xlsx"))
            self.df_beta_window100m_traject.to_excel(
                excel_writer=os.path.join(self.export_dir_traject,
                                          "df_beta_window100m_traject.xlsx"))
            self.df_beta_window200m_traject.to_excel(
                excel_writer=os.path.join(self.export_dir_traject,
                                          "df_beta_window200m_traject.xlsx"))
            self.df_beta_window300m_traject.to_excel(
                excel_writer=os.path.join(self.export_dir_traject,
                                          "df_beta_window300m_traject.xlsx"))
            self.df_beta_scaled_traject.to_excel(
                excel_writer=os.path.join(self.export_dir_traject,
                                          "df_beta_scaled_traject.xlsx"))
