from probabilistic_library import (
    CombineProject,
    CombinerMethod,
    CombineType,
    CompareType,
    DistributionType,
    ReliabilityMethod,
    ReliabilityProject,
    StandardNormal,
)


class ScenarioCalculation:
    """ScenarioCalculation class containing calculation settings and results for 1 uittredepunt"""

    def __init__(self):
        
        self.name = None
        self.uittredepunt = None
        self.scenario = None
    
        self.reliability_project = self._setup_reliability_project()
    

    

    
    def _setup_reliability_project(self) -> None:
        reliability_project = ReliabilityProject()
        
        # Set settings
        reliability_project.settings.reliability_method = ReliabilityMethod.form
        reliability_project.settings.relaxation_factor = 0.75
        reliability_project.settings.start_value = 0
        reliability_project.settings.variation_coefficient = 0.01
        reliability_project.settings.maximum_iterations = 100
        reliability_project.settings.save_realizations = True

        # Set model (uplift, heave or piping)
        reliability_project.model = Zu
        
        # Set variables
        project.variables["k"].distribution = DistributionType.log_normal
        project.variables["k"].mean = Uittredepunten_scenario.iloc[i]['k_WVP [m/dag]']
        project.variables["k"].variation = Uittredepunten_scenario.iloc[i]['VC_k_WVP [-]']
        project.variables["k"].design_quantile = 0.95
        ...etc...
    
    def plot_fragility_curve(self):
        raise NotImplementedError()

    @property
    def variables(self):
        return self.reliability_project.variables

    # FIXME add properties:
    # self.beta = None
    # self.failure_probability = None
    # self.waterlevels = None
    # self.influence_factors = None
    # self.alphas = None

class ScenarioCalculationSet:
    """ScenarioCalculationSet class containing multiple ScenarioCalculation instances"""

    def __init__(self, list_scenario_calculations: list[ScenarioCalculation]) -> None:
        self.calculations = list_scenario_calculations

