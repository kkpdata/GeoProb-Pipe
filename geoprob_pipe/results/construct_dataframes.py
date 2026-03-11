from __future__ import annotations
from geoprob_pipe.utils.statistics import convert_failure_probability_to_beta
import pandas as pd
from geoprob_pipe.results.assemblage.objects import (
    UittredepuntElement, VakElement, TrajectElement)
from pandas import DataFrame, concat
import numpy as np
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from geoprob_pipe.results import Results
    from geoprob_pipe import GeoProbPipe
    from geoprob_pipe.calculations.systems.base_objects.system_calculation import \
        SystemCalculation
    from probabilistic_library import DesignPoint
    from geoprob_pipe.calculations.systems.build_and_run import CalcResult


def collect_df_beta_limit_state(calculation: SystemCalculation) -> DataFrame:

    def create_row(dp: DesignPoint, model_name):
        return {
            "uittredepunt_id": calculation.metadata["uittredepunt_id"],
            "ondergrondscenario_id": calculation.metadata["ondergrondscenario_naam"],  # TODO: id naar naam veranderen?
            "vak_id": calculation.metadata["vak_id"],
            "limit_state": model_name,
            "converged": dp.is_converged,
            "beta": round(dp.reliability_index, 3),
            "failure_probability": dp.probability_failure,
            "convergence": dp.convergence,
            "total_iterations": dp.total_iterations,
            "total_model_runs": dp.total_model_runs,
        }

    rows = []
    for design_point, model in zip(calculation.results.dps_limit_states, calculation.setup.system_limit_states):
        rows.append(create_row(dp=design_point, model_name=model.__name__))
    df = DataFrame(rows).sort_values(by=["uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(drop=True)
    return df


def combine_df_beta_per_limit_state(calc_results: List[CalcResult]) -> DataFrame:
    assert calc_results.__len__() > 0
    df = concat((result.df_limit_state for result in calc_results), ignore_index=True)
    return df


def collect_df_beta_scenario_rp(calc: SystemCalculation) -> DataFrame:
    return DataFrame([{
        "uittredepunt_id": calc.metadata["uittredepunt_id"],
        "ondergrondscenario_id": calc.metadata["ondergrondscenario_naam"],  # TODO: id naar naam veranderen?
        "vak_id": calc.metadata["vak_id"],
        "system_calculation": calc,
        "converged": calc.results.dp_reliability.is_converged,
        "beta": round(calc.results.dp_reliability.reliability_index, 3),
        "failure_probability": calc.results.dp_reliability.probability_failure,
        "convergence": calc.results.dp_reliability.convergence,
        "total_model_runs": calc.results.dp_reliability.total_model_runs,
        "total_iterations": calc.results.dp_reliability.total_iterations,
    }])


def collect_df_beta_scenario_cp(calc: SystemCalculation) -> DataFrame:
    return DataFrame([{
        "uittredepunt_id": calc.metadata["uittredepunt_id"],
        "ondergrondscenario_id": calc.metadata["ondergrondscenario_naam"],  # TODO: id naar naam veranderen?
        "vak_id": calc.metadata["vak_id"],
        "system_calculation": calc,
        "converged": calc.results.dp_combine.is_converged,
        "beta": round(calc.results.dp_combine.reliability_index, 3),
        "failure_probability": calc.results.dp_combine.probability_failure,
        "convergence": calc.results.dp_combine.convergence,
        "total_model_runs": calc.results.dp_combine.total_model_runs,
    }])


def collect_df_beta_scenario_final(calc: SystemCalculation) -> DataFrame:
    """ Converts a SystemCalculation-object to a single-row DataFrame with the final result of the scenario
    calculations. Because there are several calculation methods, and the preferred result also depends on convergence,
    we use the below flow chart to determine the final result.

    .. image:: /_static/flow-chart-final-result-scenario-calculations.png
       :alt: Flow chart final result scenario calculations
       :align: center

    :param calc:
    :return:
    """

    # Base DataFrame-row to return
    beta1: float = calc.results.dp_combine.reliability_index
    converged1: bool = calc.results.dp_combine.is_converged
    beta2: float = calc.results.dp_reliability.reliability_index
    converged2: bool = calc.results.dp_reliability.is_converged
    beta3: float = max([dp.reliability_index for dp in calc.results.dps_limit_states])
    converged3: bool = all([dp.is_converged for dp in calc.results.dps_limit_states])
    return_dict = {
        "uittredepunt_id": calc.metadata["uittredepunt_id"],
        "ondergrondscenario_id": calc.metadata["ondergrondscenario_naam"],  # TODO: id naar naam veranderen?
        "vak_id": calc.metadata["vak_id"],
        "system_calculation": calc,
        "beta1": beta1, "converged1": converged1,
        "beta2": beta2, "converged2": converged2,
        "beta3": beta3, "converged3": converged3,
    }

    # Flow chart step 1: Combine Project converged?
    pof1: float = calc.results.dp_combine.probability_failure
    if converged1:
        return_dict["method_used"] = "1: Combine Project"
        return_dict["flow_chart_number"] = 1
        return_dict["failure_probability"] = pof1
        return_dict["beta"] = beta1
        return_dict["converged"] = converged1
        return_dict["advise"] = "-"
        return DataFrame([return_dict])

    # Flow chart step 2: Reliability Project converged?
    pof2: float = calc.results.dp_reliability.probability_failure
    if converged2:
        return_dict["method_used"] = "2: Reliability Project"
        return_dict["flow_chart_number"] = 2
        return_dict["failure_probability"] = pof2
        return_dict["beta"] = beta2
        return_dict["converged"] = converged2
        return_dict["advise"] = "-"
        return DataFrame([return_dict])

    # Flow chart step 3: Separate Limit States all converged?
    pof3: float = min([dp.probability_failure for dp in calc.results.dps_limit_states])
    if converged3:
        return_dict["method_used"] = "3: Max Limit States"
        return_dict["flow_chart_number"] = 3
        return_dict["failure_probability"] = pof3
        return_dict["beta"] = beta3
        return_dict["converged"] = converged3
        return_dict["advise"] = ("Result is probably a conservative approximation.You could consider to find "
                                 "convergence for the Combine or Reliability method.")
        return DataFrame([return_dict])

    # Flow chart step 4: B >= 8.0 (of all methods)?
    all_pofs: List[float] = [pof3, pof2, pof1]
    all_methods: List[str] = ["3: Max Limit States", "2: Reliability Project", "1: Combine Project"]
    all_betas: List[float] = [beta3, beta2, beta1]
    index_max_pof = np.argmax(all_pofs)
    if beta1 >= 8.0 and beta2 >= 8.0 and beta3 >= 8.0:
        return_dict["method_used"] = all_methods[index_max_pof]
        return_dict["flow_chart_number"] = 4
        return_dict["failure_probability"] = all_pofs[index_max_pof]
        return_dict["beta"] = all_betas[index_max_pof]
        return_dict["converged"] = False
        return_dict["advise"] = "Result is that positive, no reason to fine tune."
        return DataFrame([return_dict])

    # No positive result
    return_dict["method_used"] = all_methods[index_max_pof]
    return_dict["flow_chart_number"] = 5
    return_dict["failure_probability"] = all_pofs[index_max_pof]
    return_dict["beta"] = all_betas[index_max_pof]
    return_dict["converged"] = False
    return_dict["advise"] = "Consider fine tuning the calculation settings (of e.g. FORM, Importance Sampling, etc)."
    return DataFrame([return_dict])


def combine_df_beta_per_scenario_rp(calc_results: List[CalcResult]) -> DataFrame:
    df = concat((result.df_scenario_rp for result in calc_results), ignore_index=True)
    df = df.sort_values(["uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(drop=True)
    return df


def combine_df_beta_per_scenario_cp(calc_results: List[CalcResult]) -> DataFrame:
    df = concat((result.df_scenario_cp for result in calc_results), ignore_index=True)
    df = df.sort_values(["uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(drop=True)
    return df


def combine_df_beta_per_scenario_final(calc_results: List[CalcResult]) -> DataFrame:
    df = concat((result.df_scenario_final for result in calc_results), ignore_index=True)
    df = df.sort_values(["uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(drop=True)
    return df


def calculate_df_beta_per_uittredepunt(geoprob_pipe: GeoProbPipe, results: Results) -> DataFrame:
    """ Generates the DataFrame of the final result for the exit points.

    Because there is an automated decision-making in the scenario calculations (see flow chart over there), for the exit
    points the flow chart is extended below.

    .. image:: /_static/flow-chart-final-result-uittredepunt-calculations.png
       :alt: Flow chart final result exit point calculations
       :align: center

    :param geoprob_pipe:
    :param results:
    :return:
    """

    df_beta_scenarios_final = results.df_beta_scenarios_final.copy(deep=True)

    # Sum TODO: also sum scenario probabilities here, error when sum != 1.0
    df = df_beta_scenarios_final.assign(
        failure_probability=df_beta_scenarios_final.apply(
            lambda row: row['failure_probability'] * geoprob_pipe.input_data.scenarios.scenario_kans(
                vak_id=row['vak_id'], scenario_naam=row['ondergrondscenario_id']
            ), axis=1)).groupby('uittredepunt_id', as_index=False)[
        'failure_probability'].sum()
    df["beta"] = df["failure_probability"].apply(lambda failure_prob: convert_failure_probability_to_beta(failure_prob))

    # Determine when uittredepunt is converged (when all scenarios are converged)
    conv = df_beta_scenarios_final.groupby('uittredepunt_id', as_index=False)["converged"].all()
    df_scen: pd.DataFrame = df.merge(conv, on="uittredepunt_id", how="left")

    # Determine uittredepunt flow_chart_number
    flow_chart_number = df_beta_scenarios_final.groupby('uittredepunt_id', as_index=False)["flow_chart_number"].max()
    df_scen = df_scen.merge(flow_chart_number, on="uittredepunt_id", how="left")
    df_scen['advise'] = df_scen['flow_chart_number'].map({5: "Consider fine tuning on scenario-level."}).fillna("-")
    df_scen['flow_chart_number'] = df_scen['flow_chart_number'].map({5: 11}).fillna(12)

    # Add vak id back to it
    gdf_uittredepunten = geoprob_pipe.input_data.uittredepunten.gdf
    df_uittredepunten = gdf_uittredepunten[["uittredepunt_id", "vak_id"]]
    df_scen = df_scen.merge(df_uittredepunten, left_on="uittredepunt_id",
                            right_on="uittredepunt_id")

    return df_scen[["uittredepunt_id", "vak_id", "converged", "beta",
                    "failure_probability", "advise", "flow_chart_number"]]


def _generate_point_list(geoprob_pipe: GeoProbPipe, results: Results
                         ) -> List[UittredepuntElement]:
    """Generates a list of all the points as a list `UittredepuntElement`
    objects.

    Args:
        geoprob_pipe: GeoprobPipe object.
        results: Resutls object.

    Returns:
        List[UittredepuntElement]: List with all generated objects.
    """
    punt_df = results.df_beta_uittredepunten
    punt_gdf = geoprob_pipe.input_data.uittredepunten.gdf

    merge_df = pd.merge(
        left=punt_df[["uittredepunt_id", "vak_id", "beta", "flow_chart_number",
                      "failure_probability", "converged", "advise"]],
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
    for _, point in merge_df.iterrows():
        if point["vak_id"] in vakken_torun or run_all:
            dsn_list.append(UittredepuntElement(
                pf=point["failure_probability"],
                m_value=point["metrering"],
                a=0.9,  # TODO Haal deze vanuit Input Data via excel
                converged=point["converged"],
                flow_chart_number=point["flow_chart_number"],
                advise=point["advise"]
                ))
    return dsn_list


def _generate_element_list(geoprob_pipe: GeoProbPipe, results: Results
                           ) -> list[VakElement]:
    """Generates a lsit of all elements in a traject as `VakElement` objects.

    Args:
        geoprob_pipe: GeoprobPipe object.
        results: Resutls object.

    Returns:
        list[VakElement]: List of generated objects.
    """
    punt_df = results.df_beta_uittredepunten
    punt_gdf = geoprob_pipe.input_data.uittredepunten.gdf

    df = pd.merge(
        left=punt_df[["uittredepunt_id", "vak_id", "beta",
                      "failure_probability", "converged",
                      "flow_chart_number", "advise"]],
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

            for _, point in df_vak.iterrows():
                dsn_list.append(UittredepuntElement(
                    pf=point["failure_probability"],
                    beta=point["beta"],
                    m_value=point["metrering"],
                    a=1.0,  # TODO Haal deze vanuit Input Data via excel
                    converged=point["converged"],
                    flow_chart_number=point["flow_chart_number"],
                    advise=point["advise"]))

            element_list.append(VakElement(
                id=vak["id"],
                m_van=vak["m_start"],
                m_tot=vak["m_end"],
                a=1.0,  # TODO Haal deze vanuit Input Data via excel
                delta_length=300,
                point_list=dsn_list
            ))
    return element_list


def construct_df_beta_WBI_vak(
        geoprob_pipe: GeoProbPipe, results: Results
        ) -> pd.DataFrame:
    element_list = _generate_element_list(geoprob_pipe=geoprob_pipe,
                                          results=results)
    vakken_list = []
    for element in element_list:
        vakken_dict = {
            "m_van": element.m_van,
            "m_tot": element.m_tot,
            "lengte": element.length,
            "vak_id": element.id,
            "pf_dsn(max)": element.pf_max_dsn[0].pf,
            "beta_dsn": element.pf_max_dsn[0].beta,
            "a": element.a,
            "delta_L": element.delta_length,
            "N_vak": element.N_vak,
            "pf_vak": element.pf_max_dsn[1].pf,
            "beta_vak": element.pf_max_dsn[1].beta,
            "converged": element.conv_max_dsn,
            "flow_chart_number": element.flow_chart_number,
            "advise": element.advise}
        vakken_list.append(vakken_dict)

    return pd.DataFrame(vakken_list)


def construct_df_beta_window50_vak(
        geoprob_pipe: GeoProbPipe, results: Results
        ) -> pd.DataFrame:
    element_list = _generate_element_list(geoprob_pipe=geoprob_pipe,
                                          results=results)
    window_list = []
    for element in element_list:
        for window in element.pf_window_50m[2]:
            window_dict = {
                "m_van": window.m_van,
                "m_tot": window.m_tot,
                "lengte": window.length,
                "window_id": window.window_id,
                "vak_id": window.vak_id,
                "pf_dsn": window.pf,
                "pf_dsn(max)": element.pf_window_50m[1].pf,
                "beta_dsn": element.pf_window_50m[1].beta,
                "flow_chart_number_dsn": window.flow_chart_number,
                "delta_L": window.window_size,
                "N_vak": 1,
                "pf_vak": element.pf_window_50m[0].pf,
                "beta_vak": element.pf_window_50m[0].beta,
                "flow_chart_number": element.flow_chart_number,
                "advise": element.advise
                }
            window_list.append(window_dict)

    return pd.DataFrame(window_list)


def construct_df_beta_window100_vak(
        geoprob_pipe: GeoProbPipe, results: Results
        ) -> pd.DataFrame:
    element_list = _generate_element_list(geoprob_pipe=geoprob_pipe,
                                          results=results)
    window_list = []
    for element in element_list:
        for window in element.pf_window_100m[2]:
            window_dict = {
                "m_van": window.m_van,
                "m_tot": window.m_tot,
                "lengte": window.length,
                "window_id": window.window_id,
                "vak_id": window.vak_id,
                "pf_dsn": window.pf,
                "pf_dsn(max)": element.pf_window_100m[1].pf,
                "beta_dsn": element.pf_window_100m[1].beta,
                "flow_chart_number_dsn": window.flow_chart_number,
                "delta_L": window.window_size,
                "N_vak": 1.0,
                "pf_vak": element.pf_window_100m[0].pf,
                "beta_vak": element.pf_window_100m[0].beta,
                "flow_chart_number": element.flow_chart_number,
                "advise": element.advise
                }
            window_list.append(window_dict)

    return pd.DataFrame(window_list)


def construct_df_beta_window200_vak(
        geoprob_pipe: GeoProbPipe, results: Results
        ) -> pd.DataFrame:
    element_list = _generate_element_list(geoprob_pipe=geoprob_pipe,
                                          results=results)
    window_list = []
    for element in element_list:
        for window in element.pf_window_200m[2]:
            window_dict = {
                "m_van": window.m_van,
                "m_tot": window.m_tot,
                "lengte": window.length,
                "window_id": window.window_id,
                "vak_id": window.vak_id,
                "pf_dsn": window.pf,
                "pf_dsn(max)": element.pf_window_200m[1].pf,
                "beta_dsn": element.pf_window_200m[1].beta,
                "flow_chart_number_dsn": window.flow_chart_number,
                "delta_L": window.window_size,
                "N_vak": 1,
                "pf_vak": element.pf_window_200m[0].pf,
                "beta_vak": element.pf_window_200m[0].beta,
                "flow_chart_number": element.flow_chart_number,
                "advise": element.advise
                }
            window_list.append(window_dict)

    return pd.DataFrame(window_list)


def construct_df_beta_window300_vak(
        geoprob_pipe: GeoProbPipe, results: Results
        ) -> pd.DataFrame:
    element_list = _generate_element_list(geoprob_pipe=geoprob_pipe,
                                          results=results)
    window_list = []
    for element in element_list:
        for window in element.pf_window_300m[2]:
            window_dict = {
                "m_van": window.m_van,
                "m_tot": window.m_tot,
                "lengte": window.length,
                "window_id": window.window_id,
                "vak_id": window.vak_id,
                "pf_dsn": window.pf,
                "pf_dsn(max)": element.pf_window_300m[1].pf,
                "beta_dsn": element.pf_window_300m[1].beta,
                "flow_chart_number_dsn": window.flow_chart_number,
                "delta_L": window.window_size,
                "N_vak": 1.0,
                "pf_vak(sum)": element.pf_window_300m[0].pf,
                "beta_vak": element.pf_window_300m[0].beta,
                "flow_chart_number": element.flow_chart_number,
                "advise": element.advise
                }
            window_list.append(window_dict)

    return pd.DataFrame(window_list)


def construct_df_beta_scaled_vak(
        geoprob_pipe: GeoProbPipe, results: Results
        ) -> pd.DataFrame:
    element_list = _generate_element_list(geoprob_pipe=geoprob_pipe,
                                          results=results)
    window_list = []
    for element in element_list:
        for window in element.pf_scaled[2]:
            window_dict = {
                "m_uittredepunt": window.m_uittredepunt,
                "m_van": window.m_van,
                "m_tot": window.m_tot,
                "lengte": window.length,
                "window_id": window.window_id,
                "vak_id": window.vak_id,
                "pf_dsn": window.pf,
                "flow_chart_number_dsn": window.flow_chart_number,
                "a": window.a,
                "delta_L": element.delta_length,
                "N_vak": window.n_vak,
                "pf_vak": element.pf_scaled[0].pf,
                "beta_vak": element.pf_scaled[0].beta,
                "flow_chart_number": element.flow_chart_number,
                "advise": element.advise
                }
            window_list.append(window_dict)

    return pd.DataFrame(window_list)


def construct_df_beta_per_traject(
        geoprob_pipe: GeoProbPipe, results: Results
        ) -> pd.DataFrame:
    dsn_list = _generate_point_list(geoprob_pipe=geoprob_pipe, results=results)
    vakken_list = _generate_element_list(geoprob_pipe=geoprob_pipe,
                                         results=results)

    traject = TrajectElement(
        list_vakken=vakken_list, list_dsn=dsn_list, delta_length=300.0
    )
    traject_list = [
        {
            "method": "WBI methode over traject",
            "upper_bound_pof": traject.pf_max_vak[0].pf,
            "lower_bound_beta": traject.pf_max_vak[0].beta,
            "lower_boud_pof": traject.pf_max_vak[1].pf,
            "upper_bound_beta": traject.pf_max_vak[1].beta},
        {
            "method": "Window 50m over traject",
            "upper_bound_pof": traject.pf_window_50m[0].pf,
            "lower_bound_beta": traject.pf_window_50m[0].beta,
            "lower_boud_pof": traject.pf_window_50m[1].pf,
            "upper_bound_beta": traject.pf_window_50m[1].beta
        }, {
            "method": "Window 100m over traject",
            "upper_bound_pof": traject.pf_window_100m[0].pf,
            "lower_bound_beta": traject.pf_window_100m[0].beta,
            "lower_boud_pof": traject.pf_window_100m[1].pf,
            "upper_bound_beta": traject.pf_window_100m[1].beta
        }, {
            "method": "Window 200m over traject",
            "upper_bound_pof": traject.pf_window_200m[0].pf,
            "lower_bound_beta": traject.pf_window_200m[0].beta,
            "lower_boud_pof": traject.pf_window_200m[1].pf,
            "upper_bound_beta": traject.pf_window_200m[1].beta
        }, {
            "method": "Window 300m over traject",
            "upper_bound_pof": traject.pf_window_300m[0].pf,
            "lower_bound_beta": traject.pf_window_300m[0].beta,
            "lower_boud_pof": traject.pf_window_300m[1].pf,
            "upper_bound_beta": traject.pf_window_300m[1].beta
        }, {
            "method": "Scaled over individual sections",
            "upper_bound_pof": traject.pf_scaled[0].pf,
            "lower_bound_beta": traject.pf_scaled[0].beta,
            "lower_boud_pof": traject.pf_scaled[1].pf,
            "upper_bound_beta": traject.pf_scaled[1].beta
        }
    ]
    return pd.DataFrame(traject_list)


def construct_df_beta_window50_traject(
        geoprob_pipe: GeoProbPipe, results: Results
        ) -> pd.DataFrame:
    dsn_list = _generate_point_list(geoprob_pipe=geoprob_pipe, results=results)
    element_list = _generate_element_list(geoprob_pipe=geoprob_pipe,
                                          results=results)

    traject = TrajectElement(
        list_vakken=element_list, list_dsn=dsn_list, delta_length=50.0
    )
    window_list = []
    for window in traject.pf_window_50m[2]:
        window_dict = {
            "m_van": window.m_van,
            "m_tot": window.m_tot,
            "lengte": window.length,
            "window_id": window.window_id,
            "pf_dsn": window.pf,
            "pf_dsn(max)": traject.pf_window_50m[1].pf,
            "beta_dsn": traject.pf_window_50m[1].beta,
            "flow_chart_number_dsn": window.flow_chart_number,
            "a": 1.0,
            "delta_L": traject.delta_length,
            "N_vak": 1.0,
            "pf_traject(sum)": traject.pf_window_50m[0].pf,
            "beta_traject": traject.pf_window_50m[0].beta,
            "flow_chart_number": window.flow_chart_number,
            "advise": window.advise
            }
        window_list.append(window_dict)

    return pd.DataFrame(window_list)


def construct_df_beta_window100_traject(
        geoprob_pipe: GeoProbPipe, results: Results
        ) -> pd.DataFrame:
    dsn_list = _generate_point_list(geoprob_pipe=geoprob_pipe, results=results)
    element_list = _generate_element_list(geoprob_pipe=geoprob_pipe,
                                          results=results)

    traject = TrajectElement(
        list_vakken=element_list, list_dsn=dsn_list, delta_length=100.0
    )
    window_list = []
    for window in traject.pf_window_100m[2]:
        window_dict = {
            "m_van": window.m_van,
            "m_tot": window.m_tot,
            "lengte": window.length,
            "window_id": window.window_id,
            "pf_dsn": window.pf,
            "pf_dsn(max)": traject.pf_window_100m[1].pf,
            "beta_dsn": traject.pf_window_100m[1].beta,
            "flow_chart_number_dsn": window.flow_chart_number,
            "a": 1.0,
            "delta_L": traject.delta_length,
            "N_vak": 1.0,
            "pf_traject(sum)": traject.pf_window_100m[0].pf,
            "beta_traject": traject.pf_window_100m[0].beta,
            "flow_chart_number": window.flow_chart_number,
            "advise": window.advise
            }
        window_list.append(window_dict)

    return pd.DataFrame(window_list)


def construct_df_beta_window200_traject(
        geoprob_pipe: GeoProbPipe, results: Results
        ) -> pd.DataFrame:
    dsn_list = _generate_point_list(geoprob_pipe=geoprob_pipe, results=results)
    element_list = _generate_element_list(geoprob_pipe=geoprob_pipe,
                                          results=results)

    traject = TrajectElement(
        list_vakken=element_list, list_dsn=dsn_list, delta_length=200.0
    )
    window_list = []
    for window in traject.pf_window_200m[2]:
        window_dict = {
            "m_van": window.m_van,
            "m_tot": window.m_tot,
            "lengte": window.length,
            "window_id": window.window_id,
            "pf_dsn": window.pf,
            "pf_dsn(max)": traject.pf_window_200m[1].pf,
            "beta_dsn": traject.pf_window_200m[1].beta,
            "flow_chart_number_dsn": window.flow_chart_number,
            "a": 1.0,
            "delta_L": traject.delta_length,
            "N_vak": 1.0,
            "pf_traject(sum)": traject.pf_window_200m[0].pf,
            "beta_traject": traject.pf_window_200m[0].beta,
            "flow_chart_number": window.flow_chart_number,
            "advise": window.advise
            }
        window_list.append(window_dict)

    return pd.DataFrame(window_list)


def construct_df_beta_window300_traject(
        geoprob_pipe: GeoProbPipe, results: Results
        ) -> pd.DataFrame:
    dsn_list = _generate_point_list(geoprob_pipe=geoprob_pipe, results=results)
    element_list = _generate_element_list(geoprob_pipe=geoprob_pipe,
                                          results=results)

    traject = TrajectElement(
        list_vakken=element_list, list_dsn=dsn_list, delta_length=300.0
    )
    window_list = []
    for window in traject.pf_window_300m[2]:
        window_dict = {
            "m_van": window.m_van,
            "m_tot": window.m_tot,
            "lengte": window.length,
            "window_id": window.window_id,
            "pf_dsn": window.pf,
            "pf_dsn(max)": traject.pf_window_300m[1].pf,
            "beta_dsn": traject.pf_window_300m[1].beta,
            "flow_chart_number_dsn": window.flow_chart_number,
            "a": 1.0,
            "delta_L": traject.delta_length,
            "N_vak": 1.0,
            "pf_traject(sum)": traject.pf_window_300m[0].pf,
            "beta_traject": traject.pf_window_300m[0].beta,
            "flow_chart_number": window.flow_chart_number,
            "advise": window.advise
            }
        window_list.append(window_dict)

    return pd.DataFrame(window_list)


def construct_df_beta_scaled_traject(
        geoprob_pipe: GeoProbPipe, results: Results
        ) -> pd.DataFrame:
    dsn_list = _generate_point_list(geoprob_pipe=geoprob_pipe, results=results)
    element_list = _generate_element_list(geoprob_pipe=geoprob_pipe,
                                          results=results)

    traject = TrajectElement(
        list_vakken=element_list, list_dsn=dsn_list, delta_length=300.0
    )
    window_list = []
    for window in traject.pf_scaled[2]:
        window_dict = {
            "m_uittredepunt": window.m_uittredepunt,
            "m_van": window.m_van,
            "m_tot": window.m_tot,
            "lengte": window.length,
            "window_id": window.window_id,
            "pf_dsn": window.pf,
            "flow_chart_number_dsn": window.flow_chart_number,
            "a": window.a,
            "delta_L": traject.delta_length,
            "N_vak": window.n_vak,
            "pf_traject": traject.pf_scaled[0].pf,
            "beta_traject": traject.pf_scaled[0].beta,
            "flow_chart_number": window.flow_chart_number,
            "advise": window.advise
            }
        window_list.append(window_dict)

    return pd.DataFrame(window_list)


# def construct_df_beta_per_vak(results: Results) -> DataFrame:
#     """ Constructs the DataFrame of the final result for the vakken.

#     Because there is an automated decision-making in the scenario and exit
#     point calculations (see flow charts over there), for the vakken the flow
#     chart is extended below.

#     .. image:: /_static/flow-chart-final-result-vak-calculations.png
#        :alt: Flow chart final result vak calculations
#        :align: center

#     :param results:
#     :return:
#     """

#     # Gather data
#     df_beta_uittredepunten = results.df_beta_uittredepunten.copy(deep=True)

#     # Minimale beta van beta uittredepunten per vak
#     df: DataFrame = df_beta_uittredepunten.loc[
#         df_beta_uittredepunten.groupby('vak_id')['beta'].idxmin()]
#     df = df.drop(columns=["flow_chart_number"])

#     # Determine vak flow chart number
#     flow_chart_number = df_beta_uittredepunten.groupby(
#         'uittredepunt_id', as_index=False)["flow_chart_number"].min()
#     df = df.merge(flow_chart_number, on="uittredepunt_id", how="left")
#     df['advise'] = df['flow_chart_number'].map(
#         {11: "Consider fine tuning on scenario-level."}).fillna("-")
#     df['flow_chart_number'] = df['flow_chart_number'].map({11: 21}).fillna(22)

#     return df[["vak_id", "beta", "failure_probability", "advise"]]
