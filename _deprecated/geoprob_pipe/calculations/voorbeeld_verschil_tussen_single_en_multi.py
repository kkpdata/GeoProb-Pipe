# TODO Nu Should Klein: Onderstaande toont aan dat je single project moet gebruiken. Zou goed zijn om te verwijzen naar dit.

from probabilistic_library import (
    ReliabilityProject, ReliabilityMethod, DistributionType, DesignPoint, CombineProject, CombinerMethod, CombineType)
from geoprob_pipe.calculations.system_calculations.example_parallel_system.limit_state_functions import (
    limit_state_example_1, limit_state_example_2, system_variable_setup)
from typing import Optional
from collections import Counter


class SingleProjectCalculation:

    def __init__(self):
        # Placeholders
        self.project: Optional[ReliabilityProject] = None
        self.design_point_z1: Optional[DesignPoint] = None
        self.design_point_z2: Optional[DesignPoint] = None
        self.combine_project: Optional[CombineProject] = None
        self.design_point_system: Optional[DesignPoint] = None

        # Logic
        self.setup_project()
        self.assign_variables()
        self.generate_design_point_z1()
        self.generate_design_point_z2()
        self.generate_design_point_system()

    def setup_project(self):
        self.project = ReliabilityProject()
        self.project.settings.reliability_method = ReliabilityMethod.form
        self.project.settings.variation_coefficient = 0.02
        self.project.settings.maximum_iterations = 50

    def assign_variables(self):
        self.project.model = system_variable_setup

        self.project.variables["a"].distribution = DistributionType.uniform
        self.project.variables["a"].minimum = -1
        self.project.variables["a"].maximum = 1

        self.project.variables["b"].distribution = DistributionType.uniform
        self.project.variables["b"].minimum = -1
        self.project.variables["b"].maximum = 1

        self.project.variables["c"].distribution = DistributionType.normal
        self.project.variables["c"].mean = 0.1
        self.project.variables["c"].deviation = 0.8

    def generate_design_point_z1(self):
        self.project.model = limit_state_example_1
        self.project.run()
        self.design_point_z1 = self.project.design_point

    def generate_design_point_z2(self):
        self.project.model = limit_state_example_2
        self.project.run()
        self.design_point_z2 = self.project.design_point

    def generate_design_point_system(self):
        self.combine_project = CombineProject()
        self.combine_project.design_points.append(self.design_point_z1)
        self.combine_project.design_points.append(self.design_point_z2)
        self.combine_project.settings.combiner_method = CombinerMethod.importance_sampling
        self.combine_project.settings.combine_type = CombineType.parallel
        self.combine_project.run()
        self.design_point_system = self.combine_project.design_point


class MultipleProjectCalculation:

    def __init__(self):
        # Placeholders
        self.project_z1: Optional[ReliabilityProject] = None
        self.design_point_z1: Optional[DesignPoint] = None
        self.project_z2: Optional[ReliabilityProject] = None
        self.design_point_z2: Optional[DesignPoint] = None
        self.combine_project: Optional[CombineProject] = None
        self.design_point_system: Optional[DesignPoint] = None

        # Logic
        self.project_and_design_point_z1()
        self.project_and_design_point_z2()
        self.generate_design_point_system()

    def project_and_design_point_z1(self):
        self.project_z1 = ReliabilityProject()
        self.project_z1.settings.reliability_method = ReliabilityMethod.form
        self.project_z1.settings.variation_coefficient = 0.02
        self.project_z1.settings.maximum_iterations = 50

        self.project_z1.model = limit_state_example_1

        self.project_z1.variables["a"].distribution = DistributionType.uniform
        self.project_z1.variables["a"].minimum = -1
        self.project_z1.variables["a"].maximum = 1

        self.project_z1.variables["b"].distribution = DistributionType.uniform
        self.project_z1.variables["b"].minimum = -1
        self.project_z1.variables["b"].maximum = 1

        self.project_z1.run()
        self.design_point_z1 = self.project_z1.design_point

    def project_and_design_point_z2(self):
        self.project_z2 = ReliabilityProject()
        self.project_z2.settings.reliability_method = ReliabilityMethod.form
        self.project_z2.settings.variation_coefficient = 0.02
        self.project_z2.settings.maximum_iterations = 50

        self.project_z2.model = limit_state_example_2

        self.project_z2.variables["b"].distribution = DistributionType.uniform
        self.project_z2.variables["b"].minimum = -1
        self.project_z2.variables["b"].maximum = 1

        self.project_z2.variables["c"].distribution = DistributionType.normal
        self.project_z2.variables["c"].mean = 0.1
        self.project_z2.variables["c"].deviation = 0.8

        self.project_z2.run()
        self.design_point_z2 = self.project_z2.design_point

    def generate_design_point_system(self):
        self.combine_project = CombineProject()
        self.combine_project.design_points.append(self.design_point_z1)
        self.combine_project.design_points.append(self.design_point_z2)
        self.combine_project.settings.combiner_method = CombinerMethod.importance_sampling
        self.combine_project.settings.combine_type = CombineType.parallel
        self.combine_project.run()
        self.design_point_system = self.combine_project.design_point


single = SingleProjectCalculation()
print(f"{single.design_point_z1.reliability_index=}")
print(f"{single.design_point_z2.reliability_index=}")
print(f"{single.design_point_system.reliability_index=}")
print(Counter([alpha.variable.name for alpha in single.design_point_system.alphas]))

print(f"")

multi = MultipleProjectCalculation()
print(f"{multi.design_point_z1.reliability_index=}")
print(f"{multi.design_point_z2.reliability_index=}")
print(f"{multi.design_point_system.reliability_index=}")
print(Counter([alpha.variable.name for alpha in multi.design_point_system.alphas]))
