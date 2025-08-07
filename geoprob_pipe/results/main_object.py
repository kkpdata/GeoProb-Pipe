from __future__ import annotations
from pandas import DataFrame
from geoprob_pipe.utils.statistics import convert_failure_probability_to_beta
from typing import TYPE_CHECKING
import os
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


class Results:
    """ Subclass to intuitively group the results. """

    def __init__(self, geoprob_pipe: GeoProbPipe):
        self.geoprob_pipe = geoprob_pipe
        self.df_beta_limit_states = _collect_df_beta_per_limit_state(geoprob_pipe)
        self.df_beta_scenarios = _collect_df_beta_per_scenario(geoprob_pipe)
        self.df_beta_uittredepunten = _calculate_df_beta_per_uittredepunt(self)
        # self.df_beta_vakken = self._calculated_df_beta_per_limit_state(geoprob_pipe)

    @property
    def export_dir(self) -> str:
        # TODO Later Could Klein: Elk sub-object heeft een export_dir-method. Kan dit handiger?
        path = os.path.join(self.geoprob_pipe.workspace.path_output_folder.folderpath, "results")
        os.makedirs(path, exist_ok=True)
        return path

    def export_results(
            self, bool_beta_limit_states: bool = True, bool_beta_scenarios: bool = True,
            bool_beta_uittredepunten: bool = True):

        # Results of limit state calculations
        if bool_beta_limit_states:
            df = self.df_beta_limit_states
            # df = df[["uittredepunt_id", "ondergrondscenario_id", "model", "converged", "beta", "failure_probability"]]
            # TODO Nu Must Klein: Voor export df_beta_limit_states, kolommen filteren?
            df.to_excel(
                excel_writer=os.path.join(self.export_dir, "df_beta_limit_states.xlsx"))
            # TODO Nu Should Klein: Sommige resultaten zijn niet converged. Wat doen we daarmee?
            #  Op dit moment worden ze gewoon gebruikt om de scenario-faalkans te berekenen.

        if bool_beta_scenarios:
            df = self.df_beta_scenarios.drop(columns=['ondergrondscenario', 'system_calculation'])
            df.to_excel(
                excel_writer=os.path.join(self.export_dir, "df_beta_scenarios.xlsx"))

        if bool_beta_uittredepunten:
            df = self.df_beta_uittredepunten
            # df = df[["uittredepunt_id", "ondergrondscenario_id", "model", "converged", "beta", "failure_probability"]]
            # TODO Nu Must Klein: Voor export df_beta_uittredepunten, kolommen filteren?
            df.to_excel(
                excel_writer=os.path.join(self.export_dir, "df_beta_uittredepunten.xlsx"))


def _collect_df_beta_per_limit_state(geoprob_pipe: GeoProbPipe):

    def create_row(calc, dp, model_name):
        return {
            "uittredepunt_id": calc.metadata["uittredepunt_id"],
            "ondergrondscenario_id": calc.metadata["ondergrondscenario_id"],
            "vak_id": calc.metadata["vak_id"],
            "limit_state": model_name,
            "converged": dp.is_converged,
            "beta": round(dp.reliability_index, 2),
            "failure_probability": dp.probability_failure,
        }

    rows = []
    for calculation in geoprob_pipe.calculations:
        for design_point, model in zip(calculation.model_design_points, calculation.given_system_models):
            rows.append(create_row(calc=calculation, dp=design_point, model_name=model.__name__))
    df = DataFrame(rows).sort_values(by=["uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(drop=True)
    return df


def _collect_df_beta_per_scenario(geoprob_pipe: GeoProbPipe):

    def create_row(calc):
        return {
            "uittredepunt_id": calc.metadata["uittredepunt_id"],
            "ondergrondscenario_id": calc.metadata["ondergrondscenario_id"],
            "ondergrondscenario": calc.metadata["ondergrondscenario"],
            "vak_id": calc.metadata["vak_id"],
            "system_calculation": calc,
            "converged": calc.system_design_point.is_converged,
            "beta": round(calc.system_design_point.reliability_index, 2),
            "failure_probability": calc.system_design_point.probability_failure,
            "model_betas": ", ".join([
                str(round(dp.reliability_index, 2)) for dp in calc.model_design_points
            ])
        }

    df = DataFrame([
        create_row(calc)
        for calc in geoprob_pipe.calculations]
    ).sort_values(
        by=["uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(drop=True)
    return df


def _calculate_df_beta_per_uittredepunt(self: Results) -> DataFrame:

    df = self.df_beta_scenarios.assign(
        failure_probability=self.df_beta_scenarios.apply(
            lambda row: row['failure_probability'] *
                        row['ondergrondscenario'].variables.ondergrondscenario_kans[
                            "value"], axis=1)).groupby('uittredepunt_id', as_index=False)[
        'failure_probability'].sum()
    df["beta"] = df["failure_probability"].apply(lambda failure_prob: convert_failure_probability_to_beta(failure_prob))
    return df
