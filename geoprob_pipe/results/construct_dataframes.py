from __future__ import annotations
from geoprob_pipe.utils.statistics import convert_failure_probability_to_beta
import pandas as pd
from geoprob_pipe.results.assemblage.objects import UittredepuntElement, VakElement, TrajectElement
from typing import TYPE_CHECKING, cast, List
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


def collect_df_beta_per_scenario(calc: ParallelSystemReliabilityCalculation) -> pd.DataFrame:

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
    df_scen = cast(pd.DataFrame, results.df_beta_scenarios.assign(
        failure_probability=results.df_beta_scenarios.apply(
            lambda row: row['failure_probability'] * geoprob_pipe.input_data.scenarios.scenario_kans(
                vak_id=row['vak_id'], scenario_naam=row['ondergrondscenario_id']
            ), axis=1)).groupby('uittredepunt_id', as_index=False)[
        'failure_probability'].sum())
    df_scen["beta"] = df_scen["failure_probability"].apply(lambda failure_prob: convert_failure_probability_to_beta(failure_prob))

    # Determine when uittredepunt is converged (when all scenarios are converged)
    conv = results.df_beta_scenarios.groupby(
        'uittredepunt_id', as_index=False)["converged"].all()
    df_scen = df_scen.merge(conv, on="uittredepunt_id", how="left")

    # Add vak id back to it
    gdf_uittredepunten = geoprob_pipe.input_data.uittredepunten.gdf
    df_uittredepunten = gdf_uittredepunten[["uittredepunt_id", "vak_id"]]
    df_scen = df_scen.merge(df_uittredepunten, left_on="uittredepunt_id",
                            right_on="uittredepunt_id")

    return df_scen[["uittredepunt_id", "vak_id", "converged",
                    "beta", "failure_probability"]]


def _generate_dsn_list(geoprob_pipe: GeoProbPipe, results: Results
                       ) -> List[UittredepuntElement]:
    punt_df = results.df_beta_uittredepunten
    punt_gdf = geoprob_pipe.input_data.uittredepunten.gdf

    merge_df = pd.merge(
        left=punt_df[["uittredepunt_id", "vak_id", "beta",
                      "failure_probability", "converged"]],
        right=punt_gdf[["uittredepunt_id", "metrering"]],
        on="uittredepunt_id", how="left"
        )
    vakken_torun: List[int] = []
    run_all: bool = False
    if geoprob_pipe.input_data.app_settings.to_run_vakken_ids:
        vakken_torun = geoprob_pipe.input_data.app_settings.to_run_vakken_ids
    else:
        run_all = True
    dsn_list: List[UittredepuntElement] = []
    for _, punt in merge_df.iterrows():
        if punt["vak_id"] in vakken_torun or run_all:
            dsn_list.append(UittredepuntElement(
                pof=punt["failure_probability"],
                M_value=punt["metrering"],
                a=0.9,  # TODO Haal deze vanuit Input Data via excel
                converged=punt["converged"]
                ))
    return dsn_list


def _generate_element_list(geoprob_pipe: GeoProbPipe, results: Results
                           ) -> list[VakElement]:
    punt_df = results.df_beta_uittredepunten
    punt_gdf = geoprob_pipe.input_data.uittredepunten.gdf

    df = pd.merge(
        left=punt_df[["uittredepunt_id", "vak_id", "beta",
                      "failure_probability", "converged"]],
        right=punt_gdf[["uittredepunt_id", "metrering"]],
        on="uittredepunt_id", how="left"
        )
    vakken_torun: List[int] = []
    run_all: bool = False
    if geoprob_pipe.input_data.app_settings.to_run_vakken_ids:
        vakken_torun = geoprob_pipe.input_data.app_settings.to_run_vakken_ids
    else:
        run_all = True
    vakken_gdf = geoprob_pipe.input_data.vakken.gdf
    element_list: List[VakElement] = []

    for _, vak in vakken_gdf.iterrows():
        if vak.id in vakken_torun or run_all:
            df_vak = df.loc[df["vak_id"] == vak["id"]]
            dsn_list = []

            for _, row in df_vak.iterrows():
                dsn_list.append(UittredepuntElement(
                    pof=row["failure_probability"],
                    beta=row["beta"],
                    M_value=row["metrering"],
                    a=0.9,
                    converged=row["converged"]))

            element_list.append(VakElement(
                id=vak["id"],
                M_van=vak["m_start"],
                M_tot=vak["m_end"],
                a=0.9,  # TODO Haal deze vanuit Input Data via excel
                dL=300,
                list_dsn=dsn_list
            ))
    return element_list


def construct_df_beta_per_vak(geoprob_pipe: GeoProbPipe,
                              results: Results) -> pd.DataFrame:
    element_list = _generate_element_list(geoprob_pipe=geoprob_pipe,
                                          results=results)
    vakken_list = []
    for element in element_list:
        vakken_dict = {
            "vak_id": element.id,
            "a": element.a,
            "invloedsfactor_belasting": element.invloedsfactor_belasting,
            "method": "Max of dsn with N_vak",
            "converged": element.Conv_max_dsn,
            "pof": element.Pf_max_dsn.pof,
            "beta": element.Pf_max_dsn.beta,
            "method2": "Window 50m over vak",
            "upper_bound_pof_50m": element.Pf_window_50m[0].pof,
            "lower_bound_beta_50m": element.Pf_window_50m[0].beta,
            "lower_bound_pof_50m": element.Pf_window_50m[1].pof,
            "upper_bound_beta_50m": element.Pf_window_50m[1].beta,
            "method3": "Window 100m over vak",
            "upper_bound_pof_100m": element.Pf_window_50m[0].pof,
            "lower_bound_beta_100m": element.Pf_window_100m[0].beta,
            "lower_bound_pof_100m": element.Pf_window_50m[1].pof,
            "upper_bound_beta_100m": element.Pf_window_100m[1].beta,
            "method4": "Window 200m over vak",
            "upper_bound_pof_200m": element.Pf_window_50m[0].pof,
            "lower_bound_beta_200m": element.Pf_window_200m[0].beta,
            "lower_bound_pof_200m": element.Pf_window_50m[1].pof,
            "upper_bound_beta_200m": element.Pf_window_200m[1].beta,
            "method5": "Window 300m over vak",
            "upper_bound_pof_300m": element.Pf_window_50m[0].pof,
            "lower_bound_beta_300m": element.Pf_window_300m[0].beta,
            "lower_bound_pof_300m": element.Pf_window_50m[1].pof,
            "upper_bound_beta_300m": element.Pf_window_300m[1].beta,
            "method6": "Scaled over individual sections",
            "upper_bound_pof_scaled": element.Pf_scaled[0].pof,
            "lower_bound_beta_scaled": element.Pf_scaled[0].beta,
            "lower_bound_pof_scaled": element.Pf_scaled[1].pof,
            "upper_bound_beta_scaled": element.Pf_scaled[1].beta,
            }
        vakken_list.append(vakken_dict)

    return pd.DataFrame(vakken_list)


def construct_df_beta_per_traject(geoprob_pipe: GeoProbPipe,
                                  results: Results) -> pd.DataFrame:
    dsn_list = _generate_dsn_list(geoprob_pipe=geoprob_pipe, results=results)
    vakken_list = _generate_element_list(geoprob_pipe=geoprob_pipe,
                                         results=results)

    traject = TrajectElement(
        list_vakken=vakken_list, list_dsn=dsn_list, dL=300.0
    )
    traject_list = [
        {
            "method": "Sum of vakken",
            "upper_bound_pof": traject.Pf_max_vak[0].pof,
            "lower_bound_beta": traject.Pf_max_vak[0].beta,
            "lower_boud_pof": traject.Pf_max_vak[1].pof,
            "upper_bound_beta": traject.Pf_max_vak[1].beta},
        {
            "method": "Window 50m over traject",
            "upper_bound_pof": traject.Pf_window_50m[0].pof,
            "lower_bound_beta": traject.Pf_window_50m[0].beta,
            "lower_boud_pof": traject.Pf_window_50m[1].pof,
            "upper_bound_beta": traject.Pf_window_50m[1].beta
        }, {
            "method": "Window 100m over traject",
            "upper_bound_pof": traject.Pf_window_100m[0].pof,
            "lower_bound_beta": traject.Pf_window_100m[0].beta,
            "lower_boud_pof": traject.Pf_window_100m[1].pof,
            "upper_bound_beta": traject.Pf_window_100m[1].beta
        }, {
            "method": "Window 200m over traject",
            "upper_bound_pof": traject.Pf_window_200m[0].pof,
            "lower_bound_beta": traject.Pf_window_200m[0].beta,
            "lower_boud_pof": traject.Pf_window_200m[1].pof,
            "upper_bound_beta": traject.Pf_window_200m[1].beta
        }, {
            "method": "Window 300m over traject",
            "upper_bound_pof": traject.Pf_window_300m[0].pof,
            "lower_bound_beta": traject.Pf_window_300m[0].beta,
            "lower_boud_pof": traject.Pf_window_300m[1].pof,
            "upper_bound_beta": traject.Pf_window_300m[1].beta
        }, {
            "method": "Scaled over individual sections",
            "upper_bound_pof": traject.Pf_scaled[0].pof,
            "lower_bound_beta": traject.Pf_scaled[0].beta,
            "lower_boud_pof": traject.Pf_scaled[1].pof,
            "upper_bound_beta": traject.Pf_scaled[1].beta
        }
    ]
    return pd.DataFrame(traject_list)


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
