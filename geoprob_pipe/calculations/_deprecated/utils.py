# from geoprob_pipe.classes.reliability_calculation import CombinedReliabilityCalculation, ReliabilityCalculation
#
#
# def _result_dict(reliability_calculation: CombinedReliabilityCalculation|ReliabilityCalculation) -> dict:
#     """ Helper function to convert a ReliabilityCalculation instance to a dictionary for easy access. """
#     return {
#         "uittredepunt_id": reliability_calculation.id["uittredepunt"],
#         "uittredepunt": reliability_calculation.uittredepunt,
#         "ondergrondscenario_id": reliability_calculation.id["ondergrondscenario"],
#         "ondergrondscenario": reliability_calculation.ondergrond_scenario,
#         "reliability_calculation": reliability_calculation,
#         "converged": reliability_calculation.is_converged,
#         "beta": reliability_calculation.beta,
#         "failure_probability": reliability_calculation.reliability_project.design_point.probability_failure,
#         "alphas": reliability_calculation.alphas,
#         "influence_factors": reliability_calculation.influence_factors,
#     }
