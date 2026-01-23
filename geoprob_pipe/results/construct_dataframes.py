from __future__ import annotations
from geoprob_pipe.utils.statistics import convert_failure_probability_to_beta
import pandas as pd
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from geoprob_pipe.results import Results
    from geoprob_pipe import GeoProbPipe
    from geoprob_pipe.calculations.system_calculations.system_base_objects.parallel_system_reliability_calculation import \
        ParallelSystemReliabilityCalculation
    from probabilistic_library import DesignPoint
    from geoprob_pipe.calculations.system_calculations.build_and_run import CalcResult


def collect_df_beta_per_limit_state(calculation: ParallelSystemReliabilityCalculation) -> pd.DataFrame:

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
    for design_point, model in zip(calculation.model_design_points, calculation.given_system_models):
        rows.append(create_row(calc=calculation, dp=design_point, model_name=model.__name__))
    df = pd.DataFrame(rows).sort_values(by=["uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(drop=True)
    return df


def combine_df_beta_per_limit_state(calc_results: List[CalcResult]) -> pd.DataFrame:
    df = pd.concat((result.df_limit_state for result in calc_results), ignore_index=True)
    return df


def collect_df_beta_per_scenario(calc: ParallelSystemReliabilityCalculation
                                 ) -> pd.DataFrame:

    def create_row(calculation):
        return {
            "uittredepunt_id": calculation.metadata["uittredepunt_id"],
            "ondergrondscenario_id": calculation.metadata["ondergrondscenario_naam"],  # TODO: id naar naam veranderen?
            # "ondergrondscenario": calculation.metadata["ondergrondscenario"],
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
    df = df.sort_values(
        ["uittredepunt_id", "ondergrondscenario_id", "vak_id"]
        ).reset_index(drop=True)
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
    df = results.df_beta_uittredepunten
    return df.loc[df.groupby('vak_id')['beta'].idxmin()]


# def collect_df_alphas_influence_factors_and_physical_values(geoprob_pipe: GeoProbPipe) -> DataFrame:
#     """ Collects all Alphas, Influence factors and Physical values of the stochast input parameters. """
#
#     # Create
#     def create_df_rows_for_design_point(
#             dp: DesignPoint, calc: ParallelSystemReliabilityCalculation
#     ) -> List[Dict[str, Union[str, float]]]:
#         rows_from_dp = []
#         for alpha in dp.alphas:
#             alpha: Alpha
#             rows_from_dp.append({
#                 "uittredepunt_id": calc.metadata['uittredepunt_id'],
#                 "ondergrondscenario_id": calc.metadata['ondergrondscenario_id'],
#                 "vak_id": calc.metadata['vak_id'],
#                 "design_point": dp.identifier,
#                 "variable": alpha.identifier,
#                 "distribution_type": alpha.variable.distribution.value,
#                 "alpha": alpha.alpha,
#                 "influence_factor": alpha.alpha * alpha.alpha,
#                 "physical_value": alpha.x
#             })
#         return rows_from_dp
#
#     # Gather data
#     rows = []
#     for calculation in geoprob_pipe.calculations:
#         for design_point in calculation.model_design_points:
#             rows.extend(create_df_rows_for_design_point(dp=design_point, calc=calculation))
#         rows.extend(create_df_rows_for_design_point(dp=calculation.system_design_point, calc=calculation))
#
#     # Generate df from rows
#     df = DataFrame(rows)
#
#     return df
