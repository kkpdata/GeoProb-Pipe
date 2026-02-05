from __future__ import annotations
from geoprob_pipe.utils.statistics import convert_failure_probability_to_beta
import pandas as pd
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from geoprob_pipe.results import Results
    from geoprob_pipe import GeoProbPipe
    from geoprob_pipe.calculations.systems.base_objects.system_calculation import \
        SystemCalculation
    from probabilistic_library import DesignPoint
    from geoprob_pipe.calculations.systems.build_and_run import CalcResult


def collect_df_beta_per_limit_state(calculation: SystemCalculation) -> pd.DataFrame:

    def create_row(calc, dp: DesignPoint, model_name):
        return {
            "uittredepunt_id": calc.metadata["uittredepunt_id"],
            "ondergrondscenario_id": calc.metadata["ondergrondscenario_naam"],  # TODO: id naar naam veranderen?
            "vak_id": calc.metadata["vak_id"],
            "limit_state": model_name,
            "converged": dp.is_converged,
            "beta": round(dp.reliability_index, 2),
            "failure_probability": dp.probability_failure,
            "convergence": dp.convergence,
            "total_iterations": dp.total_iterations,
            "total_model_runs": dp.total_model_runs,
        }

    rows = []
    for design_point, model in zip(calculation.model_design_points, calculation.given_limit_states):
        rows.append(create_row(calc=calculation, dp=design_point, model_name=model.__name__))
    df = pd.DataFrame(rows).sort_values(by=["uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(drop=True)
    return df


def combine_df_beta_per_limit_state(calc_results: List[CalcResult]) -> pd.DataFrame:
    df = pd.concat((result.df_limit_state for result in calc_results), ignore_index=True)
    return df


def collect_df_beta_per_scenario(calc: SystemCalculation) -> pd.DataFrame:

    def create_row(calculation):
        return {
            "uittredepunt_id": calculation.metadata["uittredepunt_id"],
            "ondergrondscenario_id": calculation.metadata["ondergrondscenario_naam"],  # TODO: id naar naam veranderen?
            "vak_id": calculation.metadata["vak_id"],
            "system_calculation": calculation,
            "converged": calculation.system_design_point.is_converged,
            "beta": round(calculation.system_design_point.reliability_index, 2),
            "failure_probability": calculation.system_design_point.probability_failure,
            "convergence": calculation.system_design_point.convergence,
            "total_model_runs": calculation.system_design_point.total_model_runs,
            "total_iterations": calculation.system_design_point.total_iterations,
            "model_betas": ", ".join([
                str(round(dp.reliability_index, 2)) for dp in calculation.model_design_points
            ])
        }
    row = create_row(calc)

    return pd.DataFrame([row])


def combine_df_beta_per_scenario(calc_results: List[CalcResult]) -> pd.DataFrame:
    df = pd.concat((result.df_scenario for result in calc_results), ignore_index=True)
    df = df.sort_values(["uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(drop=True)
    return df


def calculate_df_beta_per_uittredepunt(geoprob_pipe: GeoProbPipe, results: Results) -> pd.DataFrame:

    # Sum
    df = results.df_beta_scenarios.assign(
        failure_probability=results.df_beta_scenarios.apply(
            lambda row: row['failure_probability'] * geoprob_pipe.input_data.scenarios.scenario_kans(
                vak_id=row['vak_id'], scenario_naam=row['ondergrondscenario_id']
            ), axis=1)).groupby('uittredepunt_id', as_index=False)[
        'failure_probability'].sum()
    df["beta"] = df["failure_probability"].apply(lambda failure_prob: convert_failure_probability_to_beta(failure_prob))

    # Determine when uittredepunt is converged (when all scenarios are converged)
    conv = results.df_beta_scenarios.groupby(
        'uittredepunt_id', as_index=False)["converged"].all()
    df = df.merge(conv, on="uittredepunt_id", how="left")

    # Add vak id back to it
    gdf_uittredepunten = geoprob_pipe.input_data.uittredepunten.gdf
    df_uittredepunten = gdf_uittredepunten[["uittredepunt_id", "vak_id"]]
    df = df.merge(df_uittredepunten, left_on="uittredepunt_id", right_on="uittredepunt_id")

    return df[["uittredepunt_id", "vak_id", "converged", "beta", "failure_probability"]]


def construct_df_beta_per_vak(results: Results):

    # TODO: Check if all calculations on scenario level are converged?
    conv = results.df_beta_scenarios.groupby('vak_id', as_index=False)["converged"].all()

    # TODO: Wat doet dit stukje code?
    df = results.df_beta_uittredepunten
    df = df.drop(columns=["converged"])  # TODO: Waarom drop converged?
    df = df.loc[df.groupby('vak_id')['beta'].idxmin()]  # Minimale beta van beta uittredepunten per vak

    # TODO: Waarom de merge?
    df = df.merge(conv, on="vak_id", how="left")
    return df[["uittredepunt_id", "vak_id", "converged", "beta", "failure_probability"]]
