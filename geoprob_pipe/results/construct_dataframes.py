from __future__ import annotations
from geoprob_pipe.utils.statistics import convert_failure_probability_to_beta
from pandas import DataFrame, merge
from geoprob_pipe.results.assemblage.objects import (
    KansElement, UittredepuntElement, VakElement, TrajectElement)
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from geoprob_pipe.results import Results
    from geoprob_pipe import GeoProbPipe
    from probabilistic_library import DesignPoint


def collect_df_beta_per_limit_state(geoprob_pipe: GeoProbPipe) -> DataFrame:

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
    for calculation in geoprob_pipe.calculations:
        for design_point, model in zip(calculation.model_design_points, calculation.given_system_models):
            rows.append(create_row(calc=calculation, dp=design_point, model_name=model.__name__))
    df = DataFrame(rows).sort_values(by=["uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(drop=True)
    return df


def collect_df_beta_per_scenario(geoprob_pipe: GeoProbPipe) -> DataFrame:

    def create_row(calc):
        return {
            "uittredepunt_id": calc.metadata["uittredepunt_id"],
            "ondergrondscenario_id": calc.metadata["ondergrondscenario_naam"],  # TODO: id naar naam veranderen?
            # "ondergrondscenario": calc.metadata["ondergrondscenario"],
            "vak_id": calc.metadata["vak_id"],
            "system_calculation": calc,
            "converged": calc.system_design_point.is_converged,
            "beta": round(calc.system_design_point.reliability_index, 2),
            "failure_probability": calc.system_design_point.probability_failure,
            "convergence": calc.system_design_point.convergence,
            "total_model_runs": calc.system_design_point.total_model_runs,
            "total_iterations": calc.system_design_point.total_iterations,
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
            lambda row: row['failure_probability'] * geoprob_pipe.input_data.scenarios.scenario_kans(
                vak_id=row['vak_id'], scenario_naam=row['ondergrondscenario_id']
            ), axis=1)).groupby('uittredepunt_id', as_index=False)[
        'failure_probability'].sum()
    df["beta"] = df["failure_probability"].apply(lambda failure_prob: convert_failure_probability_to_beta(failure_prob))

    # Add vak id back to it
    gdf_uittredepunten = geoprob_pipe.input_data.uittredepunten.gdf
    df_uittredepunten = gdf_uittredepunten[["uittredepunt_id", "vak_id"]]
    df = df.merge(df_uittredepunten, left_on="uittredepunt_id", right_on="uittredepunt_id")

    return df[["uittredepunt_id", "vak_id", "beta", "failure_probability"]]


def _generate_dsn_list(geoprob_pipe: GeoProbPipe, results: Results
                       ) -> List[UittredepuntElement]:
    punt_df = results.df_beta_uittredepunten
    punt_gdf = geoprob_pipe.input_data.uittredepunten.gdf

    merge_df = merge(
        left=punt_df[["uittredepunt_id", "vak_id", "beta",
                      "failure_probability"]],
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
                a=0.9  # TODO Haal dezen vanuit Input Data via excel
                ))
    return dsn_list


def _generate_element_list(geoprob_pipe: GeoProbPipe, results: Results
                           ) -> list[VakElement]:
    punt_df = results.df_beta_uittredepunten
    punt_gdf = geoprob_pipe.input_data.uittredepunten.gdf

    df = merge(
        left=punt_df[["uittredepunt_id", "vak_id", "beta",
                      "failure_probability"]],
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
                    a=0.9))

            element_list.append(VakElement(
                id=vak["id"],
                M_van=vak["m_start"],
                M_tot=vak["m_end"],
                a=0.9,  # TODO Haal dezen vanuit Input Data via excel
                dL=300,
                list_dsn=dsn_list
            ))
    return element_list


def construct_df_beta_per_vak(geoprob_pipe: GeoProbPipe, results: Results):
    vakken_dict = {}
    element_list = _generate_element_list(geoprob_pipe=geoprob_pipe,
                                          results=results)
    vakken_list = []
    for element in element_list:
        vakken_dict = {
            "vak_id": element.id,
            "a": element.a,
            "invloedsfactor_belasting": element.invloedsfactor_belasting,
            "method": "Max of dsn with N_vak",
            "failure_probability": element.Pf_max_dsn.pof,
            "beta": element.Pf_max_dsn.beta,
            "method2": "Window 50m over vak",
            "failure_probability2": element.Pf_window_50m.pof,
            "beta2": element.Pf_window_50m.beta,
            "method3": "Window 100m over vak",
            "failure_probability3": element.Pf_window_100m.pof,
            "beta3": element.Pf_window_100m.beta,
            "method4": "Window 250m over vak",
            "failure_probability4": element.Pf_window_250m.pof,
            "beta4": element.Pf_window_250m.beta,
            "method5": "Window 500m over vak",
            "failure_probability5": element.Pf_window_500m.pof,
            "beta5": element.Pf_window_500m.beta,
            "method6": "Scaled over individual sections",
            "beta6": element.Pf_scaled.beta,
            "failure_probability6": element.Pf_scaled.pof
            }
        vakken_list.append(vakken_dict)

    return DataFrame(vakken_list)


def construct_df_beta_per_traject(geoprob_pipe: GeoProbPipe,
                                  results: Results) -> DataFrame:
    dsn_list = _generate_dsn_list(geoprob_pipe=geoprob_pipe, results=results)
    vakken_list = _generate_element_list(geoprob_pipe=geoprob_pipe,
                                         results=results)

    traject = TrajectElement(
        list_vakken=vakken_list, list_dsn=dsn_list, dL=300.0
    )
    traject_list = []
    traject_list.append({
        "method": "Sum of vakken",
        "beta": traject.Pf_sum_max_vak.beta,
        "failure_probability": traject.Pf_sum_max_vak.pof})
    traject_list.append({
        "method": "Window 50m over traject",
        "beta": traject.Pf_window_50m.beta,
        "failure_probability": traject.Pf_window_50m.pof})
    traject_list.append({
        "method": "Window 100m over traject",
        "beta": traject.Pf_window_100m.beta,
        "failure_probability": traject.Pf_window_100m.pof})
    traject_list.append({
        "method": "Window 250m over traject",
        "beta": traject.Pf_window_250m.beta,
        "failure_probability": traject.Pf_window_250m.pof})
    traject_list.append({
        "method": "Window 500m over traject",
        "beta": traject.Pf_window_500m.beta,
        "failure_probability": traject.Pf_window_500m.pof})
    traject_list.append({
        "method": "Scaled over individual sections",
        "beta": traject.Pf_scaled.beta,
        "failure_probability": traject.Pf_scaled.pof})
    return DataFrame(traject_list)


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
