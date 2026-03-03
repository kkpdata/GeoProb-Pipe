from __future__ import annotations
from geoprob_pipe.utils.statistics import convert_failure_probability_to_beta
from pandas import DataFrame, concat
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
        return_dict["method_used"] = "3: Combined Project"
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
        return_dict["method_used"] = "1: Max Limit States"
        return_dict["flow_chart_number"] = 3
        return_dict["failure_probability"] = pof1
        return_dict["beta"] = beta1
        return_dict["converged"] = converged1
        return_dict["advise"] = ("Result is probably a conservative approximation.You could consider to find "
                                 "convergence for the Combine or Reliability method.")
        return DataFrame([return_dict])


# Traceback (most recent call last):
#   File "C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV3\GeoProb-Pipe\geoprob_pipe\calculations\systems\build_and_run.py", line 98, in _worker
#     df_scenario_final = collect_df_beta_scenario_final(calc)
#                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV3\GeoProb-Pipe\geoprob_pipe\results\construct_dataframes.py", line 126, in collect_df_beta_scenario_final
#     return DataFrame([return_dict])
#            ^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV3\.venv\Lib\site-packages\pandas\core\frame.py", line 852, in __init__
#     mgr = ndarray_to_mgr(
#           ^^^^^^^^^^^^^^^
#   File "C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV3\.venv\Lib\site-packages\pandas\core\internals\construction.py", line 282, in ndarray_to_mgr
#     values = _prep_ndarraylike(values, copy=copy)
#              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV3\.venv\Lib\site-packages\pandas\core\internals\construction.py", line 539, in _prep_ndarraylike
#     return _ensure_2d(values)
#            ^^^^^^^^^^^^^^^^^^
#   File "C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV3\.venv\Lib\site-packages\pandas\core\internals\construction.py", line 549, in _ensure_2d
#     raise ValueError(f"Must pass 2-d input. shape={values.shape}")
# ValueError: Must pass 2-d input. shape=(1, 1, 16)


    # Flow chart step 4: B >= 8.0 (of all methods)?
    all_pofs: List[float] = [pof1, pof2, pof3]
    all_methods: List[str] = ["1: Max Limit States", "2: Reliability Project", "3: Combined Project"]
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

    # converged_pofs: List[float] = []
    # converged_methods: List[str] = []
    # converged_betas: List[float] = []
    # all_pofs: List[float] = []
    # all_methods: List[str] = []
    # all_betas: List[float] = []
    # all_converged: List[bool] = []
    #
    # beta1: float = max([dp.reliability_index for dp in calc.results.dps_limit_states])
    # converged1: bool = all([dp.is_converged for dp in calc.results.dps_limit_states])
    # pof1: float = min([dp.probability_failure for dp in calc.results.dps_limit_states])
    # all_converged.append(converged1)
    # all_methods.append("1: Max Limit States")
    # all_pofs.append(pof1)
    # all_betas.append(beta1)
    # if converged1:
    #     converged_methods.append("1: Max Limit States")
    #     converged_pofs.append(pof1)
    #     converged_betas.append(beta1)
    #
    # beta2: float = calc.results.dp_reliability.reliability_index
    # converged2: bool = calc.results.dp_reliability.is_converged
    # pof2: float = calc.results.dp_reliability.probability_failure
    # all_converged.append(converged2)
    # all_methods.append("2: Reliability Project")
    # all_pofs.append(pof2)
    # all_betas.append(beta2)
    # if converged2:
    #     converged_methods.append("2: Reliability Project")
    #     converged_pofs.append(pof2)
    #     converged_betas.append(beta2)
    #
    # beta3: float = calc.results.dp_combine.reliability_index
    # converged3: bool = calc.results.dp_combine.is_converged
    # pof3: float = calc.results.dp_combine.probability_failure
    # all_converged.append(converged3)
    # all_methods.append("3: Combined Project")
    # all_pofs.append(pof3)
    # all_betas.append(beta3)
    # if converged3:
    #     converged_methods.append("3: Combined Project")
    #     converged_pofs.append(pof3)
    #     converged_betas.append(beta3)
    #
    # # Determine final result
    # if converged_pofs.__len__() > 0:
    #     converged: bool = True
    #     index_max_pof = np.argmax(converged_pofs)
    #     method_used = converged_methods[index_max_pof]
    #     method_pof = converged_pofs[index_max_pof]
    #     method_beta = converged_betas[index_max_pof]
    #     final_reason = "Converged"
    # else:
    #     converged: bool = False
    #     index_max_pof = np.argmax(all_pofs)
    #     method_used = all_methods[index_max_pof]
    #     method_pof = all_pofs[index_max_pof]
    #     method_beta = all_betas[index_max_pof]
    #     final_reason = ""  # No reason, because unconverged can be considered not final.
    #
    # # Alternative final reasons
    # if final_reason == "" and converged_pofs.__len__() == 0 and method_beta >= 8.0:
    #     final_reason = "Beta >= 8.0"
    # if converged and method_used == "1: Max Limit States":
    #     final_reason = "Approximation (converged)"
    #
    # return_df = DataFrame([{
    #     "uittredepunt_id": calc.metadata["uittredepunt_id"],
    #     "ondergrondscenario_id": calc.metadata["ondergrondscenario_naam"],  # TODO: id naar naam veranderen?
    #     "vak_id": calc.metadata["vak_id"],
    #     "system_calculation": calc,
    #     "beta1": beta1, "converged1": converged1,
    #     "beta2": beta2, "converged2": converged2,
    #     "beta3": beta3, "converged3": converged3,
    #     "method_used": method_used, "failure_probability": method_pof, "beta": method_beta, "converged": converged,
    #     "final": final_reason,
    # }])
    #
    # return return_df


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

    df_beta_scenarios_final = results.df_beta_scenarios_final.copy(deep=True)
    # df_beta_scenarios_final['final_number'] = df_beta_scenarios_final['final'].map({
    #     'Beta >= 8.0': 4,
    #     'Converged': 3,
    #     'Approximation (converged)': 2,
    # }).fillna(1)

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
    df['advise'] = df['flow_chart_number'].map({
        5: "Consider fine tuning the calculation settings (of e.g. FORM, Importance Sampling, etc)."
    }).fillna("-")
    df['flow_chart_number'] = df['flow_chart_number'].map({5: 11}).fillna(12)

    # Add vak id back to it
    gdf_uittredepunten = geoprob_pipe.input_data.uittredepunten.gdf
    df_uittredepunten = gdf_uittredepunten[["uittredepunt_id", "vak_id"]]
    df = df.merge(df_uittredepunten, left_on="uittredepunt_id", right_on="uittredepunt_id")

    return df[["uittredepunt_id", "vak_id", "converged", "beta", "failure_probability", "advise", "flow_chart_number"]]


def construct_df_beta_per_vak(results: Results):

    # Gather data
    df_beta_uittredepunten = results.df_beta_uittredepunten.copy(deep=True)

    # Minimale beta van beta uittredepunten per vak
    df: DataFrame = df_beta_uittredepunten.loc[df_beta_uittredepunten.groupby('vak_id')['beta'].idxmin()]
    df = df.drop(columns=["flow_chart_number"])

    # Determine vak flow chart number
    flow_chart_number = df_beta_uittredepunten.groupby('uittredepunt_id', as_index=False)["flow_chart_number"].min()
    # print(f"{flow_chart_number.columns=}")
    df = df.merge(flow_chart_number, on="uittredepunt_id", how="left")
    # print(f"{df.columns=}")
    df['advise'] = df['flow_chart_number'].map({
        11: "Consider fine tuning the calculation settings (of e.g. FORM, Importance Sampling, etc)."
    }).fillna("-")
    df['flow_chart_number'] = df['flow_chart_number'].map({11: 21}).fillna(22)

    # # Gather data
    # df_beta_scenarios_final = results.df_beta_uittredepunten.copy(deep=True)
    # df_beta_scenarios_final = df_beta_scenarios_final.drop(columns=["converged"])
    # # B > 8 can have no convergence, but is considered final. Therefore, drop col
    # df_beta_scenarios_final['final_number'] = df_beta_scenarios_final['final'].map({
    #     'Beta >= 8.0': 4, 'Converged': 3, 'Approximation (converged)': 2}).fillna(1)
    #
    # # Minimale beta van beta uittredepunten per vak
    # df: DataFrame = df_beta_scenarios_final.loc[df_beta_scenarios_final.groupby('vak_id')['beta'].idxmin()]
    # df = df.drop(columns=["final_number"])
    #
    # # Add advise to further calculate where necessary
    # final_number = df_beta_scenarios_final.groupby('vak_id', as_index=False)["final_number"].min()
    # df = df.merge(final_number, on="vak_id", how="left")
    # df['advies_verder_rekenen'] = df['final_number'].map({1: "Ja"}).fillna("")

    return df[["uittredepunt_id", "vak_id", "beta", "failure_probability", "advise"]]
