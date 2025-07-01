import pandas as pd
from probabilistic_library import CombineProject, CombinerMethod, CombineType
from geoprob_pipe.input_data.ondergrond_scenario import OndergrondScenario
from geoprob_pipe.classes.reliability_calculation import CombinedReliabilityCalculation
from geoprob_pipe.input_data.uittredepunt import Uittredepunt
import logging
from geoprob_pipe.calculations.utils import _result_dict


logger = logging.getLogger("geoprob_pipe_logger")


def build_and_run_combined_calculation(
        df_group: pd.DataFrame,
        uittredepunt: Uittredepunt,
        ondergrond_scenario: OndergrondScenario
) -> pd.Series:
    """

    :param df_group: All three models (uplift/heave/piping) for a unique combination of uittredepunt and
        ondergrondscenario
    :param uittredepunt:
    :param ondergrond_scenario:
    :return: Series containing the combined reliability calculation result for the unique combination of uittredepunt
        and ondergrondscenario
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
    # TODO Nu Should Middel: Implementeer ThreadPoolExecutor voor 'run combined'.

    return pd.Series(_result_dict(CombinedReliabilityCalculation(combined_project, uittredepunt, ondergrond_scenario)))
