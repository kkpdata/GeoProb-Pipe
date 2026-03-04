from __future__ import annotations
from geoprob_pipe.utils.statistics import convert_failure_probability_to_beta
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
            "beta": round(dp.reliability_index, 2),
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
        "beta": round(calc.results.dp_reliability.reliability_index, 2),
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
        "beta": round(calc.results.dp_combine.reliability_index, 2),
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
    beta1: float = max([dp.reliability_index for dp in calc.results.dps_limit_states])
    converged1: bool = all([dp.is_converged for dp in calc.results.dps_limit_states])
    beta2: float = calc.results.dp_reliability.reliability_index
    converged2: bool = calc.results.dp_reliability.is_converged
    beta3: float = calc.results.dp_combine.reliability_index
    converged3: bool = calc.results.dp_combine.is_converged
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
    pof3: float = calc.results.dp_combine.probability_failure
    if converged3:
        return_dict["method_used"] = "1: Combine Project"
        return_dict["flow_chart_number"] = 1
        return_dict["failure_probability"] = pof3
        return_dict["beta"] = beta3
        return_dict["converged"] = converged3
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
    pof1: float = min([dp.probability_failure for dp in calc.results.dps_limit_states])
    if converged1:
        return_dict["method_used"] = "3: Max Limit States"
        return_dict["flow_chart_number"] = 3
        return_dict["failure_probability"] = pof1
        return_dict["beta"] = beta1
        return_dict["converged"] = converged1
        return_dict["advise"] = ("Result is probably a conservative approximation.You could consider to find "
                                 "convergence for the Combine or Reliability method.")
        return DataFrame([return_dict])

    # Flow chart step 4: B >= 8.0 (of all methods)?
    all_pofs: List[float] = [pof1, pof2, pof3]
    all_methods: List[str] = ["3: Max Limit States", "2: Reliability Project", "1: Combine Project"]
    all_betas: List[float] = [beta1, beta2, beta3]
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

    # Determine uittredepunt flow_chart_number
    flow_chart_number = df_beta_scenarios_final.groupby('uittredepunt_id', as_index=False)["flow_chart_number"].max()
    df = df.merge(flow_chart_number, on="uittredepunt_id", how="left")
    df['advise'] = df['flow_chart_number'].map({5: "Consider fine tuning on scenario-level."}).fillna("-")
    df['flow_chart_number'] = df['flow_chart_number'].map({5: 11}).fillna(12)

    # Add vak id back to it
    gdf_uittredepunten = geoprob_pipe.input_data.uittredepunten.gdf
    df_uittredepunten = gdf_uittredepunten[["uittredepunt_id", "vak_id"]]
    df = df.merge(df_uittredepunten, left_on="uittredepunt_id", right_on="uittredepunt_id")

    return df[["uittredepunt_id", "vak_id", "converged", "beta", "failure_probability", "advise", "flow_chart_number"]]


def construct_df_beta_per_vak(results: Results) -> DataFrame:
    """ Constructs the DataFrame of the final result for the vakken.

    Because there is an automated decision-making in the scenario and exit point calculations (see flow charts over
    there), for the vakken the flow chart is extended below.

    .. image:: /_static/flow-chart-final-result-vak-calculations.png
       :alt: Flow chart final result vak calculations
       :align: center

    :param results:
    :return:
    """

    # Gather data
    df_beta_uittredepunten = results.df_beta_uittredepunten.copy(deep=True)

    # Minimale beta van beta uittredepunten per vak
    df: DataFrame = df_beta_uittredepunten.loc[df_beta_uittredepunten.groupby('vak_id')['beta'].idxmin()]
    df = df.drop(columns=["flow_chart_number"])

    # Determine vak flow chart number
    flow_chart_number = df_beta_uittredepunten.groupby('uittredepunt_id', as_index=False)["flow_chart_number"].min()
    df = df.merge(flow_chart_number, on="uittredepunt_id", how="left")
    df['advise'] = df['flow_chart_number'].map({11: "Consider fine tuning on scenario-level."}).fillna("-")
    df['flow_chart_number'] = df['flow_chart_number'].map({11: 21}).fillna(22)

    return df[["uittredepunt_id", "vak_id", "beta", "failure_probability", "advise"]]
