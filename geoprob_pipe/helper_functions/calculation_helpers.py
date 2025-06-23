from concurrent.futures import ThreadPoolExecutor
from typing import Callable

import pandas as pd
from probabilistic_library import CombineProject, CombinerMethod, CombineType

from geoprob_pipe.classes.ondergrond_scenario import OndergrondScenario
from geoprob_pipe.classes.reliability_calculation import (
    CombinedReliabilityCalculation,
    ReliabilityCalculation,
)
from geoprob_pipe.classes.uittredepunt import Uittredepunt
from geoprob_pipe.classes.vak import VakCollection


def _result_dict(reliability_calculation: CombinedReliabilityCalculation|ReliabilityCalculation) -> dict:
    """Helper function to convert a ReliabilityCalculation instance to a dictionary for easy access"""
    return {
        "uittredepunt": reliability_calculation.id["uittredepunt"],
        "ondergrondscenario": reliability_calculation.id["ondergrondscenario"],
        "reliability_calculation": reliability_calculation,
        "converged": reliability_calculation.is_converged,
        "beta": reliability_calculation.beta,
        "alphas": reliability_calculation.alphas,
        "influence_factors": reliability_calculation.influence_factors,
    }


def start_calculations(list_reliability_calculations: list[ReliabilityCalculation]) -> None:
    def run_reliability_calculation(reliability_calculation: ReliabilityCalculation) -> None:
        try:
            reliability_calculation.run()
        except Exception as e:
            print(f"ERROR: could not run running reliability calculation {reliability_calculation.id}: {e}")

    with ThreadPoolExecutor() as executor:
        executor.map(run_reliability_calculation, list_reliability_calculations)


def build_and_run_unique_model_calculations(model: Callable, vak_collection: VakCollection, df_overview_parameters: pd.DataFrame, df_settings: pd.DataFrame) -> pd.DataFrame:
    
    # Notes:
    #   1. Due to limitations in the probabilistic_library, we cannot first set up all calculations and then run them. After setting up calculations for each model (uplift/heave/piping), we need to run them immediately before setting up the next model.
    #   2. Not all combinations of uittredepunten and ondergrondscenarios are valid, so we need a helper-loop through the vakken which holds the valid combinations
    #   3. Nested for-loops are inefficient but used on purpose since there are no heavy calculations and it's easily understandable        
    
    list_calculations = []
    for vak in vak_collection.values():
        for uittredepunt in vak.uittredepunten:
            for ondergrond_scenario in vak.ondergrond_scenarios:
                list_calculations.append(
                    ReliabilityCalculation(
                        uittredepunt,
                        ondergrond_scenario,
                        model,
                        df_overview_parameters[df_overview_parameters["parameter_type"] == "constant"],
                        df_settings
                    )
                )
        start_calculations(list_calculations)
        
    # Return the calculations in a DataFrame for easy access. The DataFrame is sorted by uittredepunt and by ondergrondscenario    
    return pd.DataFrame([_result_dict(calc) for calc in list_calculations]).sort_values(by=["uittredepunt", "ondergrondscenario"]).reset_index(drop=True)


# FIXME docstring
def build_and_run_combined_calculations(df_group: pd.DataFrame, uittredepunt: Uittredepunt, ondergrond_scenario: OndergrondScenario) -> pd.Series:
    """_summary_

    Args:
        df_group (pd.DataFrame): all three models (uplift/heave/piping) for a unique combination of uittredepunt and ondergrondscenario 

    Returns:
        pd.Series: Series containing the combined reliability calculation result for the unique combination of uittredepunt and ondergrondscenario
    """
    
    # Extract the model results of uplift/heave/piping from the DataFrame group
    models = {row["model"]: row["reliability_calculation"] for _, row in df_group.iterrows()}

    # Set up and run combined project
    combined_project = CombineProject()
    combined_project.design_points.append(models["uplift"].design_point)
    combined_project.design_points.append(models["heave"].design_point)
    combined_project.design_points.append(models["piping"].design_point)
    combined_project.settings.combine_type = CombineType.parallel
    combined_project.settings.combiner_method = CombinerMethod.importance_sampling
    combined_project.run()
    
    return pd.Series(_result_dict(CombinedReliabilityCalculation(combined_project, uittredepunt, ondergrond_scenario)))
    
