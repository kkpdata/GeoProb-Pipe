from probabilistic_library import (
    ReliabilityProject, DesignPoint, CombineProject, ReliabilityMethod,
    CombinerMethod, CombineType, Stochast, Settings)
from typing import Optional, Callable, List, Dict, Union, Tuple
from geoprob_pipe.utils.validation_messages import ValidationMessages
# noinspection PyPep8Naming
from geoprob_pipe.utils.loggers import TmpAppConsoleHandler as logger


DEFAULT_RELIABILITY_SETTINGS: Dict[str, Union[str, float, int]] = {
    "reliability_method": ReliabilityMethod.form.__str__(),
    "variation_coefficient": 0.02,
    "maximum_iterations": 1000,
    "relaxation_factor": 0.4,
}


class SystemSetup:

    def __init__(
            self,
            distributions: List[Dict],
            correlations: List[Tuple[str, str, float]],
            reliability_settings: Dict[str, Union[str, float, int]],

            # Following will be assigned in children
            variables_function: Optional[Callable] = None,
            system_limit_states: Optional[List[Callable]] = None,
            project_limit_state: Optional[Callable] = None,

    ):
        self.distributions: List[Dict] = distributions
        self.correlations: List[Tuple[str, str, float]] = correlations
        self.reliability_settings: Dict[str, Union[str, float, int]] = reliability_settings
        if self.reliability_settings is None or self.reliability_settings.__len__() == 0:
            self.reliability_settings = DEFAULT_RELIABILITY_SETTINGS

        # Assigned by children:
        self.variables_function: Optional[Callable] = variables_function
        self.system_limit_states: Optional[List[Callable]] = system_limit_states
        self.project_limit_state: Optional[Callable] = project_limit_state
        # TODO: At some point combine the variables function and the project_limit_state? I think that can be done.


class SystemResults:

    def __init__(self):

        self.reliability_project = ReliabilityProject()  # Initiated for later use
        # -> Used for all reliability project calculations, i.e. the system limit states and the project limit state.
        self.dps_limit_states: List[DesignPoint] = []  # Placeholder
        self.dp_reliability: Optional[DesignPoint] = None  # Placeholder

        self.combine_project = CombineProject()  # Initiated for later use
        self.dp_combine: Optional[DesignPoint] = None  # Placeholder


class SystemCalculation:
    """ Performs """

    def __init__(
            self,
            distributions: List[Dict],
            correlations: List[Tuple[str, str, float]],
            reliability_settings: Dict[str, Union[str, float, int]] = None,

            # Following will be assigned in children
            variables_function: Optional[Callable] = None,
            system_limit_states: Optional[List[Callable]] = None,
            project_limit_state: Optional[Callable] = None,
    ):

        if reliability_settings is None:
            reliability_settings = DEFAULT_RELIABILITY_SETTINGS


        self.validation_messages = ValidationMessages()
        self.metadata = {}

        self.setup = SystemSetup(
            distributions=distributions, correlations=correlations, reliability_settings=reliability_settings,
            variables_function=variables_function, system_limit_states=system_limit_states,
            project_limit_state=project_limit_state)
        self.results = SystemResults()  # Initiation of empty object

    def run(self):
        _apply_settings(self)
        _apply_distributions(self)
        _apply_correlations(self)
        _generate_dps_limit_states(self)
        _generate_dp_reliability(self)
        _generate_dp_combine(self)


def _apply_settings(system_calculation: SystemCalculation):
    """ Applies the settings of both the Reliability Project and the Combine Project, where the former can be user
    defined settings. """

    # Reliability Project
    for attr_name, value in system_calculation.setup.reliability_settings.items():
        if attr_name not in Settings().__dir__():
            raise ValueError(
                f"Attribute '{attr_name}' not found in the ReliabilityCalculation.Settings-class. "
                f"Available attributes are:\n"
                f"{Settings().__dir__()}")
        setattr(system_calculation.results.reliability_project.settings, str(attr_name), value)

    # Combine Project
    system_calculation.results.combine_project.settings.combiner_method = CombinerMethod.importance_sampling
    system_calculation.results.combine_project.settings.combiner_method = CombineType.parallel


def _apply_distributions(system_calculation: SystemCalculation):
    """ Both initiates the variables and applies the distributions. """

    def _initiatie_variables():
        system_calculation.results.reliability_project.model = system_calculation.setup.variables_function

    def _system_variable_keys() -> List[str]:
        return_array = []
        for item in system_calculation.setup.distributions:
            return_array.append(item['name'])
        return return_array

    def _validate_distributions_are_provided():
        """ Validate all system variables have a distribution provided. """
        system_variable_keys = _system_variable_keys()
        for var_item in system_calculation.results.reliability_project.variables:
            var_item: Stochast
            if var_item.name not in system_variable_keys:
                raise KeyError(
                    f"The system variable '{var_item.name}' has no distribution provided in "
                    f"system_variable_distributions-list. Please do so before running the system.")

    def _apply_distributions_on_variables():
        for item in system_calculation.setup.distributions:
            name = item['name']

            # Check if variable exists
            if system_calculation.results.reliability_project.variables[name] is None:
                system_calculation.validation_messages.add_warning(
                    msg=f"The variable '{name}' is unknown in the ReliabilityProject, i.e. in the given "
                        f"'system_variables_setup'-function. For now this application skips unnecessary variables. If "
                        f"the variable is necessary, revisit your 'system_variables_setup'-function and the limit state "
                        f"functions.")
                # TODO Nu Should Klein: Feedback aan gebruiker dat er validation messages zijn.
                continue

            system_calculation.results.reliability_project.variables[name].distribution = item['distribution_type']

            # Key-worded arguments for uniform
            if 'minimum' in item.keys():
                system_calculation.results.reliability_project.variables[name].minimum = item['minimum']
            if 'maximum' in item.keys():
                system_calculation.results.reliability_project.variables[name].maximum = item['maximum']

            # Key-worded arguments for deterministic, normal and/or log_normal
            if 'mean' in item.keys():
                system_calculation.results.reliability_project.variables[name].mean = item['mean']
            if 'deviation' in item.keys():
                system_calculation.results.reliability_project.variables[name].deviation = item['deviation']
            if 'variation' in item.keys():
                system_calculation.results.reliability_project.variables[name].variation = item['variation']

            # Key-worded arguments for cdf-curve
            if 'fragility_values' in item.keys():
                system_calculation.results.reliability_project.variables[name].fragility_values.extend(
                    item['fragility_values'])

    _initiatie_variables()
    _validate_distributions_are_provided()
    _apply_distributions_on_variables()


def _apply_correlations(system_calculation: SystemCalculation):
    """ Correlations will be applied to the Reliability Project. """

    for correlation in system_calculation.setup.correlations:
        system_calculation.results.reliability_project.correlation_matrix[
            correlation[0],  # Parameter name A
            correlation[1]  # Parameter name B
        ] = correlation[2]  # Correlation value between 0.0 and 1.0


def _generate_dps_limit_states(system_calculation: SystemCalculation):
    """ Generates the design points for the limit states separately, i.e. uplift, heave and Sellmeijer. It uses the
    Reliability Project for this. """

    for model_callable in system_calculation.setup.system_limit_states:
        system_calculation.results.reliability_project.model = model_callable
        _apply_correlations(system_calculation=system_calculation)
        # noinspection PyBroadException
        try:
            system_calculation.results.reliability_project.run()
        except Exception:
            logger.error("Run failed in _generate_dps_limit_states")
        design_point = system_calculation.results.reliability_project.design_point
        if design_point is None:
            logger.debug(f"For limit state: {model_callable}")
            raise TypeError("Design_point is NoneType, run has failed.")
        design_point.identifier = model_callable.__name__
        system_calculation.results.dps_limit_states.append(design_point)


def _generate_dp_reliability(system_calculation: SystemCalculation):
    """ Generates the design point for the piping limit state, i.e. an encapsulating limit state for uplift, heave
    and Sellmeijer. It uses the Reliability Project for this. """
    model_callable: Callable = system_calculation.setup.project_limit_state
    system_calculation.results.reliability_project.model = model_callable
    _apply_correlations(system_calculation=system_calculation)
    # noinspection PyBroadException
    try:
        system_calculation.results.reliability_project.run()
    except Exception:
        logger.error("Run failed in _generate_dp_reliability")
    design_point = system_calculation.results.reliability_project.design_point
    if design_point is None:
        logger.debug(f"For limit state: {model_callable}")
        raise TypeError("Design_point is NoneType, run has failed.")
    design_point.identifier = model_callable.__name__
    system_calculation.results.dp_reliability = design_point


def _generate_dp_combine(system_calculation: SystemCalculation):
    """ Generates the design point for the Combine Project. """

    for design_point in system_calculation.results.dps_limit_states:
        system_calculation.results.combine_project.design_points.append(design_point)
    system_calculation.results.combine_project.run()
    system_calculation.results.combine_project.design_point.identifier = "system"
    system_calculation.results.dp_combine = system_calculation.results.combine_project.design_point


# class SystemCalculation:
#     """ Pre-defined system reliability calculation for parallel systems. """
#
#     def __init__(
#             self,
#             distributions: List[Dict],
#             correlations: List[Tuple[str, str, float]],
#             project_settings: Dict[str, Union[str, float, int]],
#             # For assigning in children
#             limit_states: Optional[List[Callable]] = None,
#             # combin_limit_state: Optional[Callable] = None,
#             variables_setup_function: Optional[Callable] = None
#     ):
#         """
#
#         :param distributions:
#         :param correlations:
#         :param project_settings: ReliabilityProject settings for the limit
#             state design points.
#         :param limit_states:
#         :param variables_setup_function: Dummy functie waarmee variabele namen
#             worden geïnitieerd.
#         """
#
#         # Mutable arguments
#         if project_settings is None:
#             project_settings = {}
#         if correlations is None:
#             correlations = []
#
#         self.validation_messages = ValidationMessages()
#         self.metadata = {}
#
#         # Input arguments
#         self.given_project_settings: Dict[str, Union[str, float, int]] = (
#             project_settings)
#         self.given_variables_setup_function: Callable = cast(
#             Callable, variables_setup_function)
#         self.given_limit_states: List[Callable] = cast(
#             List[Callable], limit_states)
#         # self.given_combin_limit_state: Callable = cast(
#         #     Callable, combin_limit_state)
#         self.given_distributions: List[Dict] = distributions
#         self.given_correlations: List[Tuple[str, str, float]] = correlations
#         # TODO Nu Should Klein: I.p.v. dict maak gebruik van
#         # Distributie-objecten. Minder fout gevoelig.
#
#         # Placeholders
#         # self.project: Optional[ReliabilityProject] = None
#         self.model_design_points: List[DesignPoint] = []
#         # self.combine_project: Optional[CombineProject] = None
#         # self.system_design_point: Optional[DesignPoint] = None
#
#     def run(self):
#         """ Performs all logic of the system reliability calculation.
#         """
#         self._setup_project()
#         self._apply_settings()
#         self._assign_variables()
#         self._assign_project_correlations()
#         self._generate_model_design_points()
#         self._generate_system_design_point()
#
#     def _setup_project(self):
#         """ Sets up the ReliabilityProject-object. This will be used
#         for all model design points.
#         """
#         self.project = ReliabilityProject()
#         self.project.settings.reliability_method = ReliabilityMethod.form
#
#         # Some base settings, may be overwritten through self._apply_settings
#         self.project.settings.reliability_method = 'form'
#         self.project.settings.variation_coefficient = 0.02
#         self.project.settings.maximum_iterations = 1000
#         self.project.settings.relaxation_factor = 0.75
#
#     def _apply_settings(self):
#         """
#         Set up the settings of the ReliabilityProject
#
#         Note: all supported settings can be found in probabilistic_library
#         .reliability.Settings.__dir__
#         """
#         for attr_name, value in self.given_project_settings.items():
#
#             if attr_name not in Settings().__dir__():
#                 raise ValueError(
#                     f"Attribute '{attr_name}' not found in the ReliabilityCalculation.Settings-class. "
#                     f"Available attributes are:\n"
#                     f"{Settings().__dir__()}")
#
#             setattr(self.project.settings, str(attr_name), value)
#
#     def _assign_variables(self):
#         self.project.model = self.given_variables_setup_function
#
#         # Validate all system variables have a distribution provided
#         system_variable_keys = _system_variable_keys(self)
#         for var_item in self.project.variables:
#             var_item: Stochast
#             if var_item.name not in system_variable_keys:
#                 raise KeyError(
#                     """
#                                """
#                     f"The system variable '{var_item.name}' has no"
#                     " distribution provided in system_variable_distributions-list."
#                     " Please do so before running the system.")
#
#         for item in self.given_distributions:
#             name = item['name']
#
#             # Check if variable exists
#             if self.project.variables[name] is None:
#                 self.validation_messages.add_warning(
#                     msg=f"The variable '{name}' is unknown in the ReliabilityProject, i.e. in the given "
#                         f"'system_variables_setup'-function. For now this application skips unnecessary variables. If "
#                         f"the variable is necessary, revisit your 'system_variables_setup'-function and the limit state "
#                         f"functions.")
#                 # TODO Nu Should Klein: Feedback aan gebruiker dat er validation messages zijn.
#                 continue
#
#             self.project.variables[name].distribution = item['distribution_type']
#
#             # Key-worded arguments for uniform
#             if 'minimum' in item.keys():
#                 self.project.variables[name].minimum = item['minimum']
#             if 'maximum' in item.keys():
#                 self.project.variables[name].maximum = item['maximum']
#
#             # Key-worded arguments for deterministic, normal and/or log_normal
#             if 'mean' in item.keys():
#                 self.project.variables[name].mean = item['mean']
#             if 'deviation' in item.keys():
#                 self.project.variables[name].deviation = item['deviation']
#             if 'variation' in item.keys():
#                 self.project.variables[name].variation = item['variation']
#
#             # Key-worded arguments for cdf-curve
#             if 'fragility_values' in item.keys():
#                 self.project.variables[name].fragility_values.extend(item['fragility_values'])
#
#     def _assign_project_correlations(self):
#         for correlation in self.given_correlations:
#             self.project.correlation_matrix[
#                 correlation[0],  # Parameter name A
#                 correlation[1]   # Parameter name B
#             ] = correlation[2]   # Correlation value between 0.0 and 1.0
#
#     def _generate_model_design_points(self):
#         for model_callable in self.given_limit_states:
#             self.project.model = model_callable
#             self._assign_project_correlations()
#             # noinspection PyBroadException
#             try:
#                 self.project.run()
#             except Exception:
#                 logger.error("Run failed in _generate_model_design_points")
#             design_point = self.project.design_point
#             if design_point is None:
#                 logger.debug(f"For limit state: {model_callable}")
#                 raise TypeError("Design_point is NoneType, run has failed.")
#             design_point.identifier = model_callable.__name__
#             self.model_design_points.append(design_point)
#
#     def _generate_system_design_point(self):
#         self.combine_project = CombineProject()
#         for design_point in self.model_design_points:
#             self.combine_project.design_points.append(design_point)
#         self.combine_project.settings.combiner_method = CombinerMethod.importance_sampling
#         self.combine_project.settings.combine_type = CombineType.parallel
#         self.combine_project.run()
#         self.combine_project.design_point.identifier = "system"
#         self.system_design_point = self.combine_project.design_point


# def _system_variable_keys(self: SystemCalculation) -> List[str]:
#     return_array = []
#     for item in self.given_distributions:
#         print(f"{item=}")
#         return_array.append(item['name'])
#     return return_array
#     # return [item['name'] for item in self.given_distributions]
