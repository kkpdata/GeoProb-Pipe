from __future__ import annotations
from geoprob_pipe.utils.statistics import convert_failure_probability_to_beta
import pandas as pd
import numpy as np
from typing import TYPE_CHECKING, List
# from geoprob_pipe.utils.loggers import TmpAppConsoleHandler as logger
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

    converged_pofs: List[float] = []
    converged_methods: List[str] = []
    converged_betas: List[float] = []
    all_pofs: List[float] = []
    all_methods: List[str] = []
    all_betas: List[float] = []
    all_converged: List[bool] = []

    beta1: float = max([dp.reliability_index for dp in calc.results.dps_limit_states])
    converged1: bool = all([dp.is_converged for dp in calc.results.dps_limit_states])
    pof1: float = min([dp.probability_failure for dp in calc.results.dps_limit_states])
    all_converged.append(converged1)
    all_methods.append("1: Max Limit States")
    all_pofs.append(pof1)
    all_betas.append(beta1)
    if converged1:
        converged_methods.append("1: Max Limit States")
        converged_pofs.append(pof1)
        converged_betas.append(beta1)

    beta2: float = calc.results.dp_reliability.reliability_index
    converged2: bool = calc.results.dp_reliability.is_converged
    pof2: float = calc.results.dp_reliability.probability_failure
    all_converged.append(converged2)
    all_methods.append("2: Reliability Project")
    all_pofs.append(pof2)
    all_betas.append(beta2)
    if converged2:
        converged_methods.append("2: Reliability Project")
        converged_pofs.append(pof2)
        converged_betas.append(beta2)

    beta3: float = calc.results.dp_combine.reliability_index
    converged3: bool = calc.results.dp_combine.is_converged
    pof3: float = calc.results.dp_combine.probability_failure
    all_converged.append(converged3)
    all_methods.append("3: Combined Project")
    all_pofs.append(pof3)
    all_betas.append(beta3)
    if converged3:
        converged_methods.append("3: Combined Project")
        converged_pofs.append(pof3)
        converged_betas.append(beta3)

    # Determine final result
    if converged_pofs.__len__() > 0:
        converged: bool = True
        index_max_pof = np.argmax(converged_pofs)
        method_used = converged_methods[index_max_pof]
        method_pof = converged_pofs[index_max_pof]
        method_beta = converged_betas[index_max_pof]
        final_reason = "Converged"
    else:
        converged: bool = False
        index_max_pof = np.argmax(all_pofs)
        method_used = all_methods[index_max_pof]
        method_pof = all_pofs[index_max_pof]
        method_beta = all_betas[index_max_pof]
        final_reason = ""  # No reason, because unconverged can be considered not final.

    # Alternative final reasons
    if final_reason == "" and converged_pofs.__len__() == 0 and method_beta >= 8.0:
        final_reason = "Beta >= 8.0"
    if converged and method_used == "1: Max Limit States":
        final_reason = "Approximation (converged)"

    return_df = pd.DataFrame([{
        "uittredepunt_id": calc.metadata["uittredepunt_id"],
        "ondergrondscenario_id": calc.metadata["ondergrondscenario_naam"],  # TODO: id naar naam veranderen?
        "vak_id": calc.metadata["vak_id"],
        "system_calculation": calc,
        "beta1": beta1, "converged1": converged1,
        "beta2": beta2, "converged2": converged2,
        "beta3": beta3, "converged3": converged3,
        "method_used": method_used, "failure_probability": method_pof, "beta": method_beta, "converged": converged,
        "final": final_reason,
    }])

    return return_df


def combine_df_beta_per_scenario_rp(calc_results: List[CalcResult]) -> pd.DataFrame:
    df = pd.concat((result.df_scenario_rp for result in calc_results), ignore_index=True)
    df = df.sort_values(["uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(drop=True)
    return df


def combine_df_beta_per_scenario_cp(calc_results: List[CalcResult]) -> pd.DataFrame:
    df = pd.concat((result.df_scenario_cp for result in calc_results), ignore_index=True)
    df = df.sort_values(["uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(drop=True)
    return df


def combine_df_beta_per_scenario_final(calc_results: List[CalcResult]) -> pd.DataFrame:
    df = pd.concat((result.df_scenario_final for result in calc_results), ignore_index=True)
    df = df.sort_values(["uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(drop=True)
    return df


def calculate_df_beta_per_uittredepunt(geoprob_pipe: GeoProbPipe, results: Results) -> pd.DataFrame:

    df_beta_scenarios_final = results.df_beta_scenarios_final.copy(deep=True)
    df_beta_scenarios_final['final_number'] = df_beta_scenarios_final['final'].map({
        'Beta >= 8.0': 4,
        'Converged': 3,
        'Approximation (converged)': 2,
    }).fillna(1)

    # Sum
    df = df_beta_scenarios_final.assign(
        failure_probability=df_beta_scenarios_final.apply(
            lambda row: row['failure_probability'] * geoprob_pipe.input_data.scenarios.scenario_kans(
                vak_id=row['vak_id'], scenario_naam=row['ondergrondscenario_id']
            ), axis=1)).groupby('uittredepunt_id', as_index=False)[
        'failure_probability'].sum()
    df["beta"] = df["failure_probability"].apply(lambda failure_prob: convert_failure_probability_to_beta(failure_prob))

    # Determine when uittredepunt is converged (when all scenarios are converged)
    conv = df_beta_scenarios_final.groupby('uittredepunt_id', as_index=False)["converged"].all()
    df = df.merge(conv, on="uittredepunt_id", how="left")

    # Determine uittredepunt final reason
    final_nr = df_beta_scenarios_final.groupby('uittredepunt_id', as_index=False)["final_number"].min()
    df = df.merge(final_nr, on="uittredepunt_id", how="left")
    df['final'] = df['final_number'].map({
        4: "Beta >= 8.0",
        3: "Converged",
        2: "Approximation (converged)",
    }).fillna("")

    # Add vak id back to it
    gdf_uittredepunten = geoprob_pipe.input_data.uittredepunten.gdf
    df_uittredepunten = gdf_uittredepunten[["uittredepunt_id", "vak_id"]]
    df = df.merge(df_uittredepunten, left_on="uittredepunt_id", right_on="uittredepunt_id")

    return df[["uittredepunt_id", "vak_id", "converged", "beta", "failure_probability", "final"]]


def construct_df_beta_per_vak(results: Results):

    # Gather data
    df_beta_scenarios_final = results.df_beta_uittredepunten.copy(deep=True)
    df_beta_scenarios_final = df_beta_scenarios_final.drop(columns=["converged"])  # B > 8 can have no convergence, but is considered final. Therefore, drop col
    df_beta_scenarios_final['final_number'] = df_beta_scenarios_final['final'].map({
        'Beta >= 8.0': 4,
        'Converged': 3,
        'Approximation (converged)': 2,
    }).fillna(1)

    # Minimale beta van beta uittredepunten per vak
    df = df_beta_scenarios_final.loc[df_beta_scenarios_final.groupby('vak_id')['beta'].idxmin()]

    # Add advise to further calculate where necessary
    final_number = df_beta_scenarios_final.groupby('vak_id', as_index=False)["final_number"].min()
    df = df.merge(final_number, on="vak_id", how="left")
    df['advies_verder_rekenen'] = df['final_number'].map({1: "Ja"}).fillna("")

    return df[["uittredepunt_id", "vak_id", "beta", "failure_probability", "advies_verder_rekenen"]]
