from __future__ import annotations
from geoprob_pipe.utils.statistics import convert_failure_probability_to_beta
from pandas import DataFrame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe.results import Results
    from geoprob_pipe import GeoProbPipe


def collect_df_beta_per_limit_state(geoprob_pipe: GeoProbPipe) -> DataFrame:

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


def collect_df_beta_per_scenario(geoprob_pipe: GeoProbPipe) -> DataFrame:

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


def calculate_df_beta_per_uittredepunt(geoprob_pipe: GeoProbPipe, results: Results) -> DataFrame:

    # Sum
    df = results.df_beta_scenarios.assign(
        failure_probability=results.df_beta_scenarios.apply(
            lambda row: row['failure_probability'] *
                        row['ondergrondscenario'].variables.ondergrondscenario_kans[
                            "value"], axis=1)).groupby('uittredepunt_id', as_index=False)[
        'failure_probability'].sum()
    df["beta"] = df["failure_probability"].apply(lambda failure_prob: convert_failure_probability_to_beta(failure_prob))

    # Add vak id back to it
    df_uittredepunten = geoprob_pipe.input_data.uittredepunten.df
    df_uittredepunten = df_uittredepunten[["uittredepunt_id", "vak_id"]]
    df = df.merge(df_uittredepunten, left_on="uittredepunt_id", right_on="uittredepunt_id")

    return df[["uittredepunt_id", "vak_id", "beta", "failure_probability"]]


def construct_df_beta_per_vak(results: Results):
    df = results.df_beta_uittredepunten
    return df.loc[df.groupby('vak_id')['beta'].idxmin()]
