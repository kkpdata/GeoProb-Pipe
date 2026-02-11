from __future__ import annotations
import pandas as pd
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from geoprob_pipe.calculations.systems.base_objects.system_calculation import \
        SystemCalculation
    from geoprob_pipe.calculations.systems.build_and_run import CalcResult


def _create_row(calculation):
    return {
        "uittredepunt_id": calculation.metadata["uittredepunt_id"],
        "ondergrondscenario_id":
            calculation.metadata["ondergrondscenario_naam"],
        "vak_id": calculation.metadata["vak_id"],
        "system_calculation": calculation,
        "converged": calculation.single_design_point.is_converged,
        "beta": round(calculation.single_design_point.reliability_index, 2),
        "failure_probability":
            calculation.single_design_point.probability_failure,
        "convergence": calculation.single_design_point.convergence,
        "total_model_runs": calculation.single_design_point.total_model_runs,
        "total_iterations": calculation.single_design_point.total_iterations,
        "model_betas": ", ".join([
            str(round(dp.reliability_index, 2))
            for dp in calculation.model_design_points
        ])
    }
    # TODO: ondergrondscenario_id naar ondergrondscenario_naam veranderen?


def collect_df_beta_scenario_v2(calc: SystemCalculation) -> pd.DataFrame:
    row = _create_row(calc)
    return pd.DataFrame([row])


def combine_df_beta_per_scenario_v2(
        calc_results: List[CalcResult]) -> pd.DataFrame:
    df = pd.concat((
        result.df_scenario_v2 for result in calc_results), ignore_index=True)
    df = df.sort_values([
        "uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(
        drop=True)
    return df
