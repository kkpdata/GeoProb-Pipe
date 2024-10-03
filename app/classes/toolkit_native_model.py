"""
This script is native to the Probabilistic Toolkit, but with some minor changes.
Changes can be found by searching for "## changed""

The original script is placed on your machine when installing the Toolkit:
C:\\Program Files (x86)\\Deltares\\Probabilistic Toolkit\\bin\\Python\\toolkit_model.py

This script has only been tested in combination with version 2023.2.343.0 of the Probabilistic Toolkit
"""

import inspect

from app.helper_functions import toolkit_native_functions


class ToolkitNative:

    def __init__(self, PATH_TO_PTK_SERVER):
        self._exited = False
        toolkit_native_functions.Initialize(PATH_TO_PTK_SERVER)

    # destructor
    def __del__(self):
        if not self._exited:
            toolkit_native_functions.Exit()

    def load(self, file_name):
        toolkit_native_functions.Load(file_name)
        return ToolkitProject()

    def save(self, file_name):
        toolkit_native_functions.Save(file_name)

    def exit(self):
        if not self._exited:
            toolkit_native_functions.Exit()
            self._exited = True


class ToolkitProject:

    def __init__(self):
        self._identifier = None
        self._design_points = None
        self._uncertainty_variables = None
        self._realizations = None

    def validate(self):
        return toolkit_native_functions.Validate()

    def run(self):
        toolkit_native_functions.Run()
        self._design_points = None
        self._realizations = None

    @property
    def identifier(self):
        if self._identifier is None:
            self._identifier = toolkit_native_functions.GetIdentifier()
        return self._identifier

    @identifier.setter
    def identifier(self, identifier):
        self._identifier = identifier
        toolkit_native_functions.SetIdentifier(identifier)

    @property
    def model(self):
        return Model()

    @property
    def settings(self):
        return Settings()

    @property
    def uncertainty_variable(self):
        return UncertaintyStochast(0)

    @property
    def uncertainty_variables(self):
        if self._uncertainty_variables is None:
            count = toolkit_native_functions.GetUncertaintyStochasts()
            self._uncertainty_variables = []
            for i in range(count):
                self._uncertainty_variables.append(UncertaintyStochast(i))
        return self._uncertainty_variables

    def get_uncertainty_variable(self, variable):
        if type(variable) is Stochast:
            variable = variable.name
        elif type(variable) is ResponseStochast:
            variable = variable.name

        vars = [var for var in self.uncertainty_variables if var.name == variable]
        if len(vars) > 0:
            return vars[0]
        else:
            return None

    @property
    def design_point(self):
        return DesignPoint(0)

    @property
    def design_points(self):
        if self._design_points is None:
            count = toolkit_native_functions.GetDesignPoints()
            self._design_points = []
            for i in range(count):
                self._design_points.append(DesignPoint(i))
        return self._design_points

    @property
    def realizations(self):
        if self._realizations is None:
            count = toolkit_native_functions.GetRealizations(0)
            self._realizations = []
            for i in range(count):
                self._realizations.append(Realization(i, 0))
        return self._realizations


class Model:

    def __init__(self):
        self._submodels = None
        self._variables = None
        self._response_variables = None
        self._input_file = None
        self._script_file = None
        self._method = None

    @property
    def input_file(self):
        if self._input_file is None:
            self._input_file = toolkit_native_functions.GetModelInputFile()
        return self._input_file

    @input_file.setter
    def input_file(self, input_file):
        self._input_file = input_file
        toolkit_native_functions.SetModelInputFile(input_file)
        self._variables = None  ## changed
        self._response_variables = None  ## changed

    @property
    def script_file(self):
        if self._script_file is None:
            self._script_file = toolkit_native_functions.GetModelScriptFile()
        return self._script_file

    @script_file.setter
    def script_file(self, script_file):
        self._script_file = script_file
        toolkit_native_functions.SetModelScriptFile(script_file)
        self._variables = None
        self._response_variables = None

    @property
    def method(self):
        if self._method is None:
            self._method = toolkit_native_functions.GetModelMethod()
        return self._method

    @method.setter
    def method(self, method):
        self._method = method
        toolkit_native_functions.SetModelMethod(method)
        self._variables = None
        self._response_variables = None

    def set_function(self, function):
        self._script_file = inspect.getfile(function)
        self._method = inspect.getmethod(function)
        toolkit_native_functions.SetModelScriptFile(self._script_file)
        toolkit_native_functions.SetModelMethod(self._method)
        self._variables = None
        self._response_variables = None

    @property
    def submodels(self):
        if self._submodels is None:
            names = toolkit_native_functions.GetSubModels()
            self._submodels = []
            for name in names:
                if not name == "":
                    self._submodels.append(SubModel(name))
        return self._submodels

    def get_submodel(self, name):
        models = [model for model in self.submodels if model.name == name]
        if len(models) > 0:
            return models[0]
        else:
            return None

    @property
    def variables(self):
        if self._variables is None:
            names = toolkit_native_functions.GetVariables()
            self._variables = []
            for name in names:
                if not name == "":
                    if "." in name and len(self.submodels) > 0:
                        submodel = self.get_submodel(name[0 : name.index(".")])
                        self._variables.append(Stochast(name, submodel))
                    else:
                        self._variables.append(Stochast(name, None))
        return self._variables

    def get_variable(self, name):
        vars = [var for var in self.variables if var.name == name]
        if len(vars) == 0 and len(self.submodels) > 0:
            vars = [var for var in self.variables if var.fullname == name]

        if len(vars) > 0:
            return vars[0]
        else:
            return None

    @property
    def response_variables(self):
        if self._response_variables is None:
            names = toolkit_native_functions.GetResponseVariables()
            self._response_variables = []
            for name in names:
                if not name == "":
                    self._response_variables.append(ResponseStochast(name))
        return self._response_variables

    def get_response_variable(self, name):
        vars = [var for var in self.response_variables if var.name == name]
        if len(vars) > 0:
            return vars[0]
        else:
            return None

    def run(self):
        toolkit_native_functions.RunEmpty()


class SubModel:

    def __init__(self, name):
        self._name = name
        self._input_file = None
        self._script_file = None
        self._method = None

    @property
    def name(self):
        return self._name

    @property
    def input_file(self):
        if self._input_file is None:
            self._input_file = toolkit_native_functions.GetSubModelInputFile(self._name)
        return self._input_file

    @input_file.setter
    def input_file(self, input_file):
        self._input_file = input_file
        toolkit_native_functions.SetSubModelInputFile(self._name, input_file)

    @property
    def script_file(self):
        if self._script_file is None:
            self._script_file = toolkit_native_functions.GetSubModelScriptFile(self._name)
        return self._script_file

    @script_file.setter
    def script_file(self, script_file):
        self._script_file = script_file
        toolkit_native_functions.SetSubModelScriptFile(self._name, script_file)

    @property
    def method(self):
        if self._method is None:
            self._method = toolkit_native_functions.GetSubModelMethod(self._name)
        return self._method

    @method.setter
    def method(self, method):
        self._method = method
        toolkit_native_functions.SetSubModelMethod(self._name, method)

    def set_function(self, function):
        self._script_file = inspect.getfile(function)
        self._method = inspect.getmethod(function)
        toolkit_native_functions.SetSubModelScriptFile(self._name, self._script_file)
        toolkit_native_functions.SetSubModelMethod(self._name, self._method)

    def run(self):
        toolkit_native_functions.RunSubModelEmpty(self._name)


class Stochast:

    def __init__(self, name, submodel):

        self._fullname = name
        if not submodel is None:
            name = name[len(submodel.name) + 1 :]
        self._name = name
        self._submodel = submodel
        self._clear_values()

    @property
    def name(self):
        return self._name

    @property
    def fullname(self):
        return self._fullname

    @property
    def submodel(self):
        return self._submodel

    def _clear_values(self):
        self._distribution = None
        self._mean = None
        self._deviation = None
        self._variation = None
        self._shift = None
        self._shift_b = None
        self._minimum = None
        self._maximum = None
        self._rate = None
        self._shape = None
        self._shape_b = None
        self._scale = None
        self._location = None
        self._observations = None
        self._design_fraction = None
        self._design_factor = None
        self._design_value = None

    def clear(self):
        toolkit_native_functions.ClearVariable(self._fullname)
        self._clear_values()

    def get_quantile(self, quantile):
        return toolkit_native_functions.GetVariableQuantile(self._fullname, quantile)

    @property
    def distribution(self):
        if self._distribution is None:
            self._distribution = toolkit_native_functions.GetVariableDistribution(self._fullname)
        return self._distribution

    @distribution.setter
    def distribution(self, value):
        self._distribution = value
        toolkit_native_functions.SetVariableDistribution(self._fullname, value)

    @property
    def mean(self):
        if self._mean is None:
            self._mean = toolkit_native_functions.GetVariableValue(self._fullname, "mean")
        return self._mean

    @mean.setter
    def mean(self, value):
        self._mean = value
        toolkit_native_functions.SetVariableValue(self._fullname, "mean", value)

    @property
    def deviation(self):
        if self._deviation is None:
            self._deviation = toolkit_native_functions.GetVariableValue(self._fullname, "deviation")
        return self._deviation

    @deviation.setter
    def deviation(self, value):
        self._deviation = value
        self._variation = None
        toolkit_native_functions.SetVariableValue(self._fullname, "deviation", value)

    @property
    def variation(self):
        if self._variation is None:
            self._variation = toolkit_native_functions.GetVariableValue(self._fullname, "variation")
        return self._variation

    @variation.setter
    def variation(self, value):
        self._variation = value
        self._deviation = None
        toolkit_native_functions.SetVariableValue(self._fullname, "variation", value)

    @property
    def shift(self):
        if self._shift is None:
            self._shift = toolkit_native_functions.GetVariableValue(self._fullname, "shift")
        return self._shift

    @shift.setter
    def shift(self, value):
        self._shift = value
        toolkit_native_functions.SetVariableValue(self._fullname, "shift", value)

    @property
    def shift_b(self):
        if self._shift_b is None:
            self._shift_b = toolkit_native_functions.GetVariableValue(self._fullname, "shift_b")
        return self._shift_b

    @shift_b.setter
    def shift_b(self, value):
        self._shift_b = value
        toolkit_native_functions.SetVariableValue(self._fullname, "shift_b", value)

    @property
    def minimum(self):
        if self._minimum is None:
            self._minimum = toolkit_native_functions.GetVariableValue(self._fullname, "minimum")
        return self._minimum

    @minimum.setter
    def minimum(self, value):
        self._minimum = value
        toolkit_native_functions.SetVariableValue(self._fullname, "minimum", value)

    @property
    def maximum(self):
        if self._maximum is None:
            self._maximum = toolkit_native_functions.GetVariableValue(self._fullname, "maximum")
        return self._maximum

    @maximum.setter
    def maximum(self, value):
        self._maximum = value
        toolkit_native_functions.SetVariableValue(self._fullname, "maximum", value)

    @property
    def shape(self):
        if self._shape is None:
            self._shape = toolkit_native_functions.GetVariableValue(self._fullname, "shape")
        return self._shape

    @shape.setter
    def shape(self, value):
        self._shape = value
        toolkit_native_functions.SetVariableValue(self._fullname, "shape", value)

    @property
    def shape_b(self):
        if self._shape_b is None:
            self._shape_b = toolkit_native_functions.GetVariableValue(self._fullname, "shape_b")
        return self._shape_b

    @shape_b.setter
    def shape_b(self, value):
        self._shape_b = value
        toolkit_native_functions.SetVariableValue(self._fullname, "shape_b", value)

    @property
    def scale(self):
        if self._scale is None:
            self._scale = toolkit_native_functions.GetVariableValue(self._fullname, "scale")
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        toolkit_native_functions.SetVariableValue(self._fullname, "scale", value)

    @property
    def rate(self):
        if self._rate is None:
            self._rate = toolkit_native_functions.GetVariableValue(self._fullname, "rate")
        return self._rate

    @rate.setter
    def rate(self, value):
        self._rate = value
        toolkit_native_functions.SetVariableValue(self._fullname, "rate", value)

    @property
    def observations(self):
        if self._observations is None:
            self._observations = toolkit_native_functions.GetVariableValue(self._fullname, "observations")
        return self._observations

    @observations.setter
    def observations(self, value):
        self._observations = value
        toolkit_native_functions.SetVariableValue(self._fullname, "observations", value)

    @property
    def design_fraction(self):
        if self._design_fraction is None:
            self._design_fraction = toolkit_native_functions.GetVariableDesignFraction(self._fullname)
        return self._design_fraction

    @design_fraction.setter
    def design_fraction(self, value):
        self._design_fraction = value
        toolkit_native_functions.SetVariableDesignFraction(self._fullname, value)

    @property
    def design_factor(self):
        if self._design_factor is None:
            self._design_factor = toolkit_native_functions.GetVariableDesignFactor(self._fullname)
        return self._design_factor

    @design_factor.setter
    def design_factor(self, value):
        self._design_factor = value
        toolkit_native_functions.SetVariableDesignFactor(self._fullname, value)

    @property
    def design_value(self):
        if self._design_value is None:
            return toolkit_native_functions.GetVariableDesignValue(self._fullname)
        else:
            return self._design_value

    @design_value.setter
    def design_value(self, value):
        self._design_value = value
        toolkit_native_functions.SetVariableDesignValue(self._fullname, value)

    @property
    def location(self):
        if self._location is None:
            self._location = toolkit_native_functions.GetVariableValue(self._fullname, "location")
        return self._location

    @location.setter
    def location(self, value):
        self._location = value
        toolkit_native_functions.SetVariableValue(self._fullname, "location", value)  ## changed

    def set_fragility_reliability_index(self, cond_value, rel_index):
        toolkit_native_functions.SetVariableFragilityValue(self._fullname, "ReliabilityIndex", cond_value, rel_index)

    def set_fragility_prob_failure(self, cond_value, rel_index):
        toolkit_native_functions.SetVariableFragilityValue(self._fullname, "ProbabilityFailure", cond_value, rel_index)

    def set_fragility_prob_non_failure(self, cond_value, rel_index):
        toolkit_native_functions.SetVariableFragilityValue(
            self._fullname, "ProbabilityNonFailure", cond_value, rel_index
        )

    def set_discrete_value(self, cond_value, occurrences):
        toolkit_native_functions.SetVariableDiscreteValue(self._fullname, cond_value, occurrences)

    def set_histogram_value(self, lower, upper, occurrences):
        toolkit_native_functions.SetVariableTableValue(self._fullname, lower, upper, occurrences)

    def get_correlation(self, other):
        if type(other) is Stochast:
            other = other.name
        return toolkit_native_functions.GetCorrelation(self._fullname, other)

    def set_correlation(self, other, correlation):
        if type(other) is Stochast:
            other = other.name
        toolkit_native_functions.SetCorrelation(self._fullname, other, correlation)


class ResponseStochast:

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name


class Settings:

    def __init__(self):
        self._clear_values()

    def _clear_values(self):
        self._method = None
        self._start_method = None
        self._minimum_samples = None
        self._maximum_samples = None
        self._minimum_iterations = None
        self._maximum_iterations = None
        self._relaxation_factor = None
        self._relaxation_loops = None
        self._variation_coefficient_failure = None
        self._intervals = None
        self._variance_factor = None
        self._start_value = None
        self._variance_loops = None
        self._min_variance_loops = None
        self._fraction_failed = None

    def set_fragility_values(self, values):
        toolkit_native_functions.SetFragilityValues(values)

    @property
    def method(self):
        if self._method is None:
            self._method = toolkit_native_functions.GetSettingMethod()
        return self._method

    @method.setter
    def method(self, value):
        self._method = value
        toolkit_native_functions.SetSettingMethod(value)

    @property
    def start_method(self):
        if self._start_method is None:
            self._start_method = toolkit_native_functions.GetSettingStartMethod()
        return self._start_method

    @method.setter
    def start_method(self, value):
        self._start_method = value
        toolkit_native_functions.SetSettingStartMethod(value)

    @property
    def minimum_samples(self):
        if self._minimum_samples is None:
            self._minimum_samples = toolkit_native_functions.GetSettingValue("minimum_samples")
        return self._minimum_samples

    @minimum_samples.setter
    def minimum_samples(self, value):
        self._minimum_samples = value
        toolkit_native_functions.SetSettingValue("minimum_samples", value)

    @property
    def maximum_samples(self):
        if self._maximum_samples is None:
            self._maximum_samples = toolkit_native_functions.GetSettingValue("maximum_samples")
        return self._maximum_samples

    @maximum_samples.setter
    def maximum_samples(self, value):
        self._maximum_samples = value
        toolkit_native_functions.SetSettingValue("maximum_samples", value)

    @property
    def minimum_iterations(self):
        if self._minimum_iterations is None:
            self._minimum_iterations = toolkit_native_functions.GetSettingValue("minimum_iterations")
        return self._minimum_iterations

    @minimum_iterations.setter
    def minimum_iterations(self, value):
        self._minimum_iterations = value
        toolkit_native_functions.SetSettingValue("minimum_iterations", value)

    @property
    def maximum_iterations(self):
        if self._maximum_iterations is None:
            self._maximum_iterations = toolkit_native_functions.GetSettingValue("maximum_iterations")
        return self._maximum_iterations

    @maximum_iterations.setter
    def maximum_iterations(self, value):
        self._maximum_iterations = value
        toolkit_native_functions.SetSettingValue("maximum_iterations", value)

    @property
    def relaxation_factor(self):
        if self._relaxation_factor is None:
            self._relaxation_factor = toolkit_native_functions.GetSettingValue("relaxation_factor")
        return self._relaxation_factor

    @relaxation_factor.setter
    def relaxation_factor(self, value):
        self._relaxation_factor = value
        toolkit_native_functions.SetSettingValue("relaxation_factor", value)

    @property
    def relaxation_loops(self):
        if self._relaxation_loops is None:
            self._relaxation_loops = toolkit_native_functions.GetSettingValue("relaxation_loops")
        return self._relaxation_loops

    @relaxation_loops.setter
    def relaxation_loops(self, value):
        self._relaxation_loops = value
        toolkit_native_functions.SetSettingValue("relaxation_loops", value)

    @property
    def variation_coefficient_failure(self):
        if self._variation_coefficient_failure is None:
            self._variation_coefficient_failure = toolkit_native_functions.GetSettingValue(
                "variation_coefficient_failure"
            )
        return self._variation_coefficient_failure

    @variation_coefficient_failure.setter
    def variation_coefficient_failure(self, value):
        self._variation_coefficient_failure = value
        toolkit_native_functions.SetSettingValue("variation_coefficient_failure", value)

    @property
    def intervals(self):
        if self._intervals is None:
            self._intervals = toolkit_native_functions.GetSettingValue("intervals")
        return self._intervals

    @intervals.setter
    def intervals(self, value):
        self._intervals = value
        toolkit_native_functions.SetSettingValue("intervals", value)

    @property
    def variance_factor(self):
        if self._variance_factor is None:
            self._variance_factor = toolkit_native_functions.GetSettingValue("variance_factor")
        return self._variance_factor

    @variance_factor.setter
    def variance_factor(self, value):
        self._variance_factor = value
        toolkit_native_functions.SetSettingValue("variance_factor", value)

    @property
    def start_value(self):
        if self._start_value is None:
            self._start_value = toolkit_native_functions.GetSettingValue("start_value")
        return self._start_value

    @start_value.setter
    def start_value(self, value):
        self._start_value = value
        toolkit_native_functions.SetSettingValue("start_value", value)

    @property
    def variance_loops(self):
        if self._variance_loops is None:
            self._variance_loops = toolkit_native_functions.GetSettingValue("variance_loops")
        return self._variance_loops

    @variance_loops.setter
    def variance_loops(self, value):
        self._variance_loops = value
        toolkit_native_functions.SetSettingValue("variance_loops", value)

    @property
    def min_variance_loops(self):
        if self._min_variance_loops is None:
            self._min_variance_loops = toolkit_native_functions.GetSettingValue("min_variance_loops")
        return self._min_variance_loops

    @min_variance_loops.setter
    def min_variance_loops(self, value):
        self._min_variance_loops = value
        toolkit_native_functions.SetSettingValue("min_variance_loops", value)

    @property
    def fraction_failed(self):
        if self._fraction_failed is None:
            self._fraction_failed = toolkit_native_functions.GetSettingValue("fraction_failed")
        return self._fraction_failed

    @fraction_failed.setter
    def fraction_failed(self, value):
        self._fraction_failed = value
        toolkit_native_functions.SetSettingValue("fraction_failed", value)

    def get_variable_settings(self, stochast):
        if type(stochast) is Stochast:
            stochast = stochast.name
        return StochastSettings(stochast)


class StochastSettings:

    def __init__(self, name):
        self._name = name
        self._clear_values()

    def _clear_values(self):
        self._start_value = None

    @property
    def name(self):
        return self._name

    @property
    def start_value(self):
        if self._start_value is None:
            self._start_value = toolkit_native_functions.GetStartValue(self._name)
        return self._start_value

    @start_value.setter
    def start_value(self, value):
        self._start_value = value
        toolkit_native_functions.SetStartValue(self._name, value)


class UncertaintyStochast:

    def __init__(self, index):
        self._index = index
        self._name = None

    @property
    def name(self):
        if self._name is None:
            self._name = toolkit_native_functions.GetUncertaintyStochastName(self._index)
        return self._name

    def get_quantile(self, quantile):
        return toolkit_native_functions.GetUncertaintyStochastQuantile(self._index, quantile)


class DesignPoint:

    def __init__(self, index):
        self._index = index
        self._clear_values()

    def _clear_values(self):
        self._identifiers = None
        self._reliability_index = None
        self._probability_failure = None
        self._convergence = None
        self._realizations = None

    @property
    def identifiers(self):
        if self._identifiers is None:
            self._identifiers = toolkit_native_functions.GetNumericIdentifiers(self._index)
        return self._identifiers

    @property
    def reliability_index(self):
        if self._reliability_index is None:
            self._reliability_index = toolkit_native_functions.GetReliabilityIndex(self._index)
        return self._reliability_index

    @property
    def probability_failure(self):
        if self._probability_failure is None:
            self._probability_failure = toolkit_native_functions.GetProbabilityFailure(self._index)
        return self._probability_failure

    @property
    def convergence(self):
        if self._convergence is None:
            self._convergence = toolkit_native_functions.GetConvergence(self._index)
        return self._convergence

    def get_alpha(self, stochast):
        if type(stochast) is Stochast:
            stochast = stochast.fullname
        return Alpha(stochast, self._index)

    @property
    def realizations(self):
        if self._realizations is None:
            count = toolkit_native_functions.GetRealizations(self._index)
            self._realizations = []
            for i in range(count):
                self._realizations.append(Realization(i, self._index))
        return self._realizations


class Alpha:

    def __init__(self, name, design_point_index):
        self._name = name
        self._design_point_index = design_point_index
        self._clear_values()

    def _clear_values(self):
        self._alpha_value = None
        self._physical_value = None

    @property
    def alpha_value(self):
        if self._alpha_value is None:
            self._alpha_value = toolkit_native_functions.GetAlpha(self._name, self._design_point_index)
        return self._alpha_value

    @property
    def physical_value(self):
        if self._physical_value is None:
            self._physical_value = toolkit_native_functions.GetAlphaPhysical(self._name, self._design_point_index)
        return self._physical_value


class Realization:

    def __init__(self, index, design_point_index):
        self._index = index
        self._design_point_index = design_point_index
        self._z = None
        self._weight = None
        self._beta = None

    def get_value(self, variable):
        if type(variable) is Stochast:
            variable = variable.fullname
        elif type(variable) is ResponseStochast:
            variable = variable.name

        return toolkit_native_functions.GetRealizationValue(self._index, variable, self._design_point_index)

    @property
    def z(self):
        if self._z is None:
            self._z = toolkit_native_functions.GetRealizationProperty(self._index, "Z", self._design_point_index)
        return self._z

    @property
    def beta(self):
        if self._beta is None:
            self._beta = toolkit_native_functions.GetRealizationProperty(self._index, "Beta", self._design_point_index)
        return self._beta

    @property
    def weight(self):
        if self._weight is None:
            self._weight = toolkit_native_functions.GetRealizationProperty(
                self._index, "Weight", self._design_point_index
            )
        return self._weight
