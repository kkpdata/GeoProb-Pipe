from probabilistic_library import (
    ReliabilityProject, DesignPoint, CombineProject, ReliabilityMethod, CombinerMethod, CombineType, DistributionType)
from typing import Optional, Callable, List, Dict
from geoprob_pipe.calculations.limit_state_functions import (
    system_variable_setup, limit_state_example_1, limit_state_example_2)


class ParallelSystemReliabilityCalculation:
    pass

    def __init__(
            self,
            system_variable_distributions: List[Dict],
            system_models: Optional[List[Callable]] = None,  # For assigning in children
            system_variables_setup_function: Optional[Callable] = None,  # For assigning in children
    ):
        """

        :param system_variables_setup_function: Dummy functie waarmee variabele namen worden geïnitieerd.
        :param system_variable_distributions:
        :param system_models:
        """

        # Input arguments
        self.system_variables_setup_function: Callable = system_variables_setup_function
        self.system_models: List[Callable] = system_models
        self.system_variable_distributions: List[Dict] = system_variable_distributions
        # TODO Nu Should Klein: I.p.v. dict maak gebruik van Distributie-objecten. Minder fout gevoelig.

        # Placeholders
        self.project: Optional[ReliabilityProject] = None
        self.model_design_points: List[DesignPoint] = []
        self.combine_project: Optional[CombineProject] = None
        self.system_design_point: Optional[DesignPoint] = None

        # Logic
        self.setup_project()
        self.assign_variables()
        self.generate_model_design_points()
        self.generate_system_design_point()

    def setup_project(self):
        self.project = ReliabilityProject()
        self.project.settings.reliability_method = ReliabilityMethod.form
        self.project.settings.variation_coefficient = 0.02
        self.project.settings.maximum_iterations = 50
        print(f"Finished setting up project")

    def assign_variables(self):
        self.project.model = self.system_variables_setup_function
        for item in self.system_variable_distributions:
            name = item['name']
            self.project.variables[name].distribution = item['distribution_type']

            # uniform
            if 'minimum' in item.keys():
                self.project.variables[name].minimum = item['minimum']
            if 'maximum' in item.keys():
                self.project.variables[name].maximum = item['maximum']

            # normal
            if 'mean' in item.keys():
                self.project.variables[name].mean = item['mean']
            if 'deviation' in item.keys():
                self.project.variables[name].deviation = item['deviation']
        print(f"Finished assigning variables")

    def generate_model_design_points(self):
        for model_callable in self.system_models:
            self.project.model = model_callable
            self.project.run()
            self.model_design_points.append(self.project.design_point)
        print(f"Finished generating model design points")

    def generate_system_design_point(self):
        self.combine_project = CombineProject()
        for design_point in self.model_design_points:
            self.combine_project.design_points.append(design_point)
        self.combine_project.settings.combiner_method = CombinerMethod.importance_sampling
        self.combine_project.settings.combine_type = CombineType.parallel
        self.combine_project.run()
        self.system_design_point = self.combine_project.design_point
        print(f"Finished generating system design point")


obj = PipingSystem(
    system_variables_setup_function=system_variable_setup,
    system_variable_distributions=[
        {
            "name": "a",
            "distribution_type": DistributionType.uniform,
            "minimum": -1,
            "maximum": 1,
        },
        {
            "name": "b",
            "distribution_type": DistributionType.uniform,
            "minimum": -1,
            "maximum": 1,
        },
        {
            "name": "c",
            "distribution_type": DistributionType.normal,
            "mean": 0.1,
            "deviation": 0.8,
        },
    ],
    system_models=[limit_state_example_1, limit_state_example_2]
)
