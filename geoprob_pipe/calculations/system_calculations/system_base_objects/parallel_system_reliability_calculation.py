from probabilistic_library import (
    ReliabilityProject, DesignPoint, CombineProject, ReliabilityMethod,
    CombinerMethod, CombineType, Stochast, Settings)
from typing import Optional, Callable, List, Dict, Union
from geoprob_pipe.calculations.system_calculations.system_base_objects._base_system_reliability_calculation import (
    BaseSystemReliabilityCalculation)
import logging
from geoprob_pipe.utils.validation_messages import ValidationMessages
from typing import Tuple
from geoprob_pipe.calculations.system_calculations.piping_system.safe_design_point import SafeDesignPoint


logger = logging.getLogger("geoprob_pipe_logger")


def _alpha_to_plain_live(alpha) -> dict:
    """Read Alpha directly from the live object."""
    var = getattr(alpha, "variable", None)
    if var is not None:
        var_plain = {
            "name": getattr(var, "name", None),
            "distribution": getattr(getattr(var, "distribution", None),
                                    "value", None),
            "mean": getattr(var, "mean", None),
            "minimum": getattr(var, "minimum", None),
            "maximum": getattr(var, "maximum", None),
            "deviation": getattr(var, "deviation", None),
            "variation": getattr(var, "variation", None),
        }
    else:
        var_plain = None

    def _py(x):
        try:
            import numpy as np
            if isinstance(x, (np.floating, np.integer)):
                return x.item()
        except Exception:
            pass
        return x

    return {
        "identifier": getattr(alpha, "identifier", None),
        "alpha": _py(getattr(alpha, "alpha", None)),
        "alpha_correlated": _py(getattr(alpha, "alpha_correlated", None)),
        "influence_factor": _py(getattr(alpha, "influence_factor", None)),
        "index": _py(getattr(alpha, "index", None)),
        "u": _py(getattr(alpha, "u", None)),
        "x": _py(getattr(alpha, "x", None)),
        "variable": var_plain,
    }


def _design_point_to_plain_live(dp) -> dict:
    """Read a DesignPoint directly from the live object, including alphas."""
    def _py(x):
        try:
            import numpy as np
            if isinstance(x, (np.floating, np.integer)):
                return x.item()
        except Exception:
            pass
        return x

    data = {
        "identifier": getattr(dp, "identifier", None),
        "reliability_index": _py(getattr(dp, "reliability_index", None)),
        "probability_failure": _py(getattr(dp, "probability_failure", None)),
        "convergence": _py(getattr(dp, "convergence", None)),
        "is_converged": bool(getattr(dp, "is_converged", False)),
        "total_directions": _py(getattr(dp, "total_directions", None)),
        "total_iterations": _py(getattr(dp, "total_iterations", None)),
        "total_model_runs": _py(getattr(dp, "total_model_runs", None)),
        "alphas": [],
        "messages": [],
        "contributing_design_points": [],   # add if you need nested
    }

    # ✅ pull live alphas right now
    try:
        for a in getattr(dp, "alphas", []):
            data["alphas"].append(_alpha_to_plain_live(a))
    except Exception:
        pass

    # optional: messages
    try:
        msgs = []
        for m in getattr(dp, "messages", []):
            msgs.append(str(m))
        data["messages"] = msgs
    except Exception:
        pass

    return data


class ParallelSystemReliabilityCalculation(BaseSystemReliabilityCalculation):
    """ Pre-defined system reliability calculation for parallel systems. In the example below for a parallel system for
    Piping. Note however that for Piping there is already a predefined system in
    `geoprob_pipe.calculations.system_calculations.piping_system`.

    Usage by
    - Calling the object;
    - inserting the system setup variable that initiate all variable names;
    - inserting the variable distributions;
    - inserting the system models, i.e. the parallel limit states;
    - and after that calling the run-method.
    See examples in child classes.
    """

    def __init__(
            self,
            system_variable_distributions: List[Dict],
            system_models: Optional[List[Callable]] = None,  # For assigning in children
            system_variables_setup_function: Optional[Callable] = None,  # For assigning in children
            project_settings: Dict[str, Union[str, float, int]] = None
    ):
        """

        :param system_variables_setup_function: Dummy functie waarmee variabele namen worden geïnitieerd.
        :param system_variable_distributions:
        :param system_models:
        :param project_settings: ReliabilityProject settings for the limit state design points.
        """

        # Mutable arguments
        if project_settings is None:
            project_settings = {}

        self.validation_messages = ValidationMessages()
        self.metadata = {}

        # Input arguments
        self.given_project_settings: Dict[str, Union[str, float, int]] = project_settings
        self.given_system_variables_setup_function: Callable = system_variables_setup_function
        self.given_system_models: List[Callable] = system_models
        self.given_system_variable_distributions: List[Dict] = system_variable_distributions
        # TODO Later Should Klein: I.p.v. dict maak gebruik van Distributie-objecten. Minder fout gevoelig.

        # Placeholders
        self.project: Optional[ReliabilityProject] = None
        self.model_design_points: List[DesignPoint] = []
        self.combine_project: Optional[CombineProject] = None
        self.system_design_point: Optional[DesignPoint] = None

    def run(self):
        """ Performs all logic of the system reliability calculation. """
        self._setup_project()
        self._apply_settings()
        self.project.settings.reliability_method = 'form'
        self.project.settings.maximum_iterations = 100
        self.project.settings.relaxation_factor = 0.75
        self._assign_variables()
        self._generate_model_design_points()
        self._generate_system_design_point()

    def export_result(self) -> Tuple[List[dict], dict]:
        """
        Split the results from the calculation and convert them to dicts
        ready to be pickled.
        """
        model_plain = [_design_point_to_plain_live(dp) for dp in self.model_design_points]
        system_plain = _design_point_to_plain_live(self.system_design_point)
        return model_plain, system_plain

    def import_results(self, result: Tuple[List[dict], dict]):
        """
        Add the results into the class after rehydrating.
        """
        model_plain_list, system_plain = result
        self.model_design_points = [SafeDesignPoint.from_plain(dp) for dp in model_plain_list]
        self.system_design_point = SafeDesignPoint.from_plain(system_plain)

    def _setup_project(self):
        """ Sets up the ReliabilityProject-object. This will be used for all model design points. """
        self.project = ReliabilityProject()
        self.project.settings.reliability_method = ReliabilityMethod.form

        # Some base settings, may be overwritten through self._apply_settings
        self.project.settings.variation_coefficient = 0.02
        self.project.settings.maximum_iterations = 50

    def _apply_settings(self):
        """
        Set up the settings of the ReliabilityProject

        Note: all supported settings can be found in probabilistic_library.reliability.Settings.__dir__
        """
        for attr_name, value in self.given_project_settings.items():

            if attr_name not in Settings().__dir__():
                raise ValueError(
                    f"Attribute '{attr_name}' not found in the ReliabilityCalculation.Settings-class. "
                    f"Available attributes are:\n"
                    f"{Settings().__dir__()}")

            setattr(self.project.settings, str(attr_name), value)

    def _assign_variables(self):
        self.project.model = self.given_system_variables_setup_function

        # Validate all system variables have a distribution provided
        system_variable_keys = _system_variable_keys(self)
        for var_item in self.project.variables:
            var_item: Stochast
            if var_item.name not in system_variable_keys:
                raise KeyError(
                    f"The system variable '{var_item.name}' has no distribution provided in "
                    f"system_variable_distributions-list. Please do so before running the system.")

        for item in self.given_system_variable_distributions:
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

    def _generate_model_design_points(self):
        for model_callable in self.given_system_models:
            self.project.model = model_callable
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


def _system_variable_keys(self: ParallelSystemReliabilityCalculation) -> List[str]:
    return [item['name'] for item in self.given_system_variable_distributions]

