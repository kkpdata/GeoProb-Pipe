from __future__ import annotations
from geoprob_pipe.utils.statistics import convert_failure_probability_to_beta
import pandas as pd
import numpy as np
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from geoprob_pipe.results import Results
    from geoprob_pipe import GeoProbPipe
    from geoprob_pipe.calculations.systems.base_objects.system_calculation import \
        SystemCalculation
    from probabilistic_library import DesignPoint
    from geoprob_pipe.calculations.systems.build_and_run import CalcResult


def collect_df_beta_limit_state(calculation: SystemCalculation) -> pd.DataFrame:

    def create_row(dp: DesignPoint, model_name):
        return {
            "uittredepunt_id": calculation.metadata["uittredepunt_id"],
            "ondergrondscenario_id": calculation.metadata["ondergrondscenario_naam"],  # TODO: id naar naam veranderen?
            "vak_id": calculation.metadata["vak_id"],
            "limit_state": model_name,
            "converged": dp.is_converged,
            "beta": round(dp.reliability_index, 2),
            "failure_probability": dp.probability_failure,
            "convergence": dp.convergence,
            "total_iterations": dp.total_iterations,
            "total_model_runs": dp.total_model_runs,
        }

    rows = []
    for design_point, model in zip(calculation.results.dps_limit_states, calculation.setup.system_limit_states):
        rows.append(create_row(dp=design_point, model_name=model.__name__))
    df = pd.DataFrame(rows).sort_values(by=["uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(drop=True)
    return df


def combine_df_beta_per_limit_state(calc_results: List[CalcResult]) -> pd.DataFrame:
    df = pd.concat((result.df_limit_state for result in calc_results), ignore_index=True)
    return df


def collect_df_beta_scenario_rp(calc: SystemCalculation) -> pd.DataFrame:
    return pd.DataFrame([{
        "uittredepunt_id": calc.metadata["uittredepunt_id"],
        "ondergrondscenario_id": calc.metadata["ondergrondscenario_naam"],  # TODO: id naar naam veranderen?
        "vak_id": calc.metadata["vak_id"],
        "system_calculation": calc,
        "converged": calc.results.dp_reliability.is_converged,
        "beta": round(calc.results.dp_reliability.reliability_index, 2),
        "failure_probability": calc.results.dp_reliability.probability_failure,
        "convergence": calc.results.dp_reliability.convergence,
        "total_model_runs": calc.results.dp_reliability.total_model_runs,
        "total_iterations": calc.results.dp_reliability.total_iterations,
    }])


def collect_df_beta_scenario_cp(calc: SystemCalculation) -> pd.DataFrame:
    return pd.DataFrame([{
        "uittredepunt_id": calc.metadata["uittredepunt_id"],
        "ondergrondscenario_id": calc.metadata["ondergrondscenario_naam"],  # TODO: id naar naam veranderen?
        "vak_id": calc.metadata["vak_id"],
        "system_calculation": calc,
        "converged": calc.results.dp_combine.is_converged,
        "beta": round(calc.results.dp_combine.reliability_index, 2),
        "failure_probability": calc.results.dp_combine.probability_failure,
        "convergence": calc.results.dp_combine.convergence,
        "total_model_runs": calc.results.dp_combine.total_model_runs,
    }])


def collect_df_beta_scenario_final(calc: SystemCalculation) -> pd.DataFrame:

    converged_pofs = []
    all_pofs = []
    converged_methods = []
    all_methods = []

    beta1: float = max([dp.reliability_index for dp in calc.results.dps_limit_states])
    converged1: bool = all([dp.is_converged for dp in calc.results.dps_limit_states])
    pof1: float = min([dp.probability_failure for dp in calc.results.dps_limit_states])
    all_methods.append("1: Max Limit States")
    all_pofs.append(pof1)
    if converged1:
        converged_methods.append("1: Max Limit States")
        converged_pofs.append(pof1)

    beta2: float = calc.results.dp_reliability.reliability_index
    converged2: bool = calc.results.dp_reliability.is_converged
    pof2: float = calc.results.dp_reliability.probability_failure
    all_methods.append("2: Reliability Project")
    all_pofs.append(pof2)
    if converged2:
        converged_methods.append("2: Reliability Project")
        converged_pofs.append(pof2)

    beta3: float = calc.results.dp_combine.reliability_index
    converged3: bool = calc.results.dp_combine.is_converged
    pof3: float = calc.results.dp_combine.probability_failure
    all_methods.append("3: Combined Project")
    all_pofs.append(pof3)
    if converged3:
        converged_methods.append("3: Combined Project")
        converged_pofs.append(pof2)

    method_used = all_methods[np.argmax(all_pofs)]
    method_pof = max(all_pofs)
    if converged_pofs.__len__() > 0:
        method_used = converged_methods[np.argmax(converged_pofs)]
        method_pof = max(converged_pofs)

    return pd.DataFrame([{
        "uittredepunt_id": calc.metadata["uittredepunt_id"],
        "ondergrondscenario_id": calc.metadata["ondergrondscenario_naam"],  # TODO: id naar naam veranderen?
        "vak_id": calc.metadata["vak_id"],
        "system_calculation": calc,
        "beta1": max([dp.reliability_index for dp in calc.results.dps_limit_states]),
        "converged1": all([dp.is_converged for dp in calc.results.dps_limit_states]),
        "beta2": calc.results.dp_reliability.reliability_index,
        "converged2": calc.results.dp_reliability.is_converged,
        "beta3": calc.results.dp_combine.reliability_index,
        "converged3": calc.results.dp_combine.is_converged,
        "method_used": method_used,
        "failure_probability": method_pof,
    }])


def combine_df_beta_per_scenario_rp(calc_results: List[CalcResult]) -> pd.DataFrame:
    df = pd.concat((result.df_scenario for result in calc_results), ignore_index=True)
    df = df.sort_values(["uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(drop=True)
    return df


def combine_df_beta_per_scenario_cp(calc_results: List[CalcResult]) -> pd.DataFrame:
    df = pd.concat((result.df_scenario for result in calc_results), ignore_index=True)
    df = df.sort_values(["uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(drop=True)
    return df


def combine_df_beta_per_scenario_final(calc_results: List[CalcResult]) -> pd.DataFrame:
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
