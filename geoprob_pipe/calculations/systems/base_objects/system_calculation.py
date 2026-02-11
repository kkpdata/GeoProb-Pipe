from probabilistic_library import (
    ReliabilityProject, DesignPoint, CombineProject, ReliabilityMethod,
    CombinerMethod, CombineType, Stochast, Settings)
from typing import Optional, Callable, List, Dict, Union, Tuple, cast
import logging
from geoprob_pipe.utils.validation_messages import ValidationMessages


logger = logging.getLogger("geoprob_pipe_logger")


class SystemCalculation:
    """ Pre-defined system reliability calculation for parallel systems. """

    def __init__(
            self,
            distributions: List[Dict],
            correlations: List[Tuple[str, str, float]],
            project_settings: Dict[str, Union[str, float, int]],
            # For assigning in children
            ls_separate: Optional[List[Callable]] = None,
            ls_single: Optional[Callable] = None,
            variables_setup_function: Optional[Callable] = None
    ):
        """

        :param distributions:
        :param correlations:
        :param project_settings: ReliabilityProject settings for the limit
            state design points.
        :param ls_separate: Limit states (plural) for Uplift, Heave and
            Sellmeijer that will be calculated separately in
            ReliabilityProjects and then combined in a CombineProject.
        :param ls_single: Limit state (singular) that has already combined
            Uplift, Heave and Sellmeijer in its function, and will be
            calculated as ReliabilityProject. According to Deltares this
            method is preferential to ls_separate.
        :param variables_setup_function: Dummy functie waarmee variabele namen
            worden geïnitieerd.
        """

        # Mutable arguments
        if project_settings is None:
            project_settings = {}
        if correlations is None:
            correlations = []

        self.validation_messages = ValidationMessages()
        self.metadata = {}

        # Input arguments
        self.given_project_settings: Dict[str, Union[str, float, int]] = (
            project_settings)
        self.given_variables_setup_function: Callable = cast(
            Callable, variables_setup_function)
        self.given_ls_separate: List[Callable] = cast(
            List[Callable], ls_separate)
        self.given_ls_single: Callable = cast(Callable, ls_single)
        self.given_distributions: List[Dict] = distributions
        self.given_correlations: List[Tuple[str, str, float]] = correlations
        # TODO Nu Should Klein: I.p.v. dict maak gebruik van
        # Distributie-objecten. Minder fout gevoelig.

        # Placeholders
        self.model_design_points: List[DesignPoint] = []
        self.single_design_point: Optional[DesignPoint] = None

    def run(self):
        """ Performs all logic of the system reliability calculation.
        """
        self._setup_project()
        self._apply_settings()
        self._assign_variables()
        self._assign_project_correlations()
        self._generate_model_design_points()
        self._generate_system_design_point()
        self._generate_single_design_point()

    def _setup_project(self):
        """ Sets up the ReliabilityProject-object. This will be used
        for all model design points.
        """
        self.project = ReliabilityProject()
        self.project.settings.reliability_method = ReliabilityMethod.form

        # Some base settings, may be overwritten through self._apply_settings
        self.project.settings.reliability_method = 'form'
        self.project.settings.variation_coefficient = 0.02
        self.project.settings.maximum_iterations = 1000
        self.project.settings.relaxation_factor = 0.75

    def _apply_settings(self):
        """
        Set up the settings of the ReliabilityProject

        Note: all supported settings can be found in probabilistic_library
        .reliability.Settings.__dir__
        """
        for attr_name, value in self.given_project_settings.items():

            if attr_name not in Settings().__dir__():
                raise ValueError(
                    f"Attribute '{attr_name}' not found in the ReliabilityCalculation.Settings-class. "
                    f"Available attributes are:\n"
                    f"{Settings().__dir__()}")

            setattr(self.project.settings, str(attr_name), value)

    def _assign_variables(self):
        self.project.model = self.given_variables_setup_function

        # Validate all system variables have a distribution provided
        system_variable_keys = _system_variable_keys(self)
        for var_item in self.project.variables:
            var_item: Stochast
            if var_item.name not in system_variable_keys:
                raise KeyError(
                    """
                               """
                    f"The system variable '{var_item.name}' has no"
                    " distribution provided in system_variable_distributions-list."
                    " Please do so before running the system.")

        for item in self.given_distributions:
            name = item['name']

            # Check if variable exists
            if self.project.variables[name] is None:
                self.validation_messages.add_warning(
                    msg=f"The variable '{name}' is unknown in the ReliabilityProject, i.e. in the given "
                        f"'system_variables_setup'-function. For now this application skips unnecessary variables. If "
                        f"the variable is necessary, revisit your 'system_variables_setup'-function and the limit state "
                        f"functions.")
                # TODO Nu Should Klein: Feedback aan gebruiker dat er validation messages zijn.
                continue

            self.project.variables[name].distribution = item['distribution_type']

            # Key-worded arguments for uniform
            if 'minimum' in item.keys():
                self.project.variables[name].minimum = item['minimum']
            if 'maximum' in item.keys():
                self.project.variables[name].maximum = item['maximum']

            # Key-worded arguments for deterministic, normal and/or log_normal
            if 'mean' in item.keys():
                self.project.variables[name].mean = item['mean']
            if 'deviation' in item.keys():
                self.project.variables[name].deviation = item['deviation']
            if 'variation' in item.keys():
                self.project.variables[name].variation = item['variation']

            # Key-worded arguments for cdf-curve
            if 'fragility_values' in item.keys():
                self.project.variables[name].fragility_values.extend(item['fragility_values'])

    def _assign_project_correlations(self):
        for correlation in self.given_correlations:
            self.project.correlation_matrix[
                correlation[0],  # Parameter name A
                correlation[1]   # Parameter name B
            ] = correlation[2]   # Correlation value between 0.0 and 1.0

    def _generate_model_design_points(self):
        for model_callable in self.given_ls_separate:
            self.project.model = model_callable
            self._assign_project_correlations()
            self.project.run()
            design_point = self.project.design_point
            design_point.identifier = model_callable.__name__
            self.model_design_points.append(design_point)

    def _generate_system_design_point(self):
        self.combine_project = CombineProject()
        for design_point in self.model_design_points:
            self.combine_project.design_points.append(design_point)
        self.combine_project.settings.combiner_method = CombinerMethod.importance_sampling
        self.combine_project.settings.combine_type = CombineType.parallel
        self.combine_project.run()
        self.combine_project.design_point.identifier = "system"
        self.system_design_point = self.combine_project.design_point

    def _generate_single_design_point(self):
        model_callable = self.given_ls_single
        self.project.model = model_callable
        self._assign_project_correlations()
        self.project.run()
        design_point = self.project.design_point
        design_point.identifier = model_callable.__name__
        self.single_design_point = design_point


def _system_variable_keys(self: SystemCalculation) -> List[str]:
    return [item['name'] for item in self.given_distributions]
