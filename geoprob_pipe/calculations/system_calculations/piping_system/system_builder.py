from importlib.metadata import metadata
from geoprob_pipe.calculations.system_calculations.system_base_objects.base_system_build import BaseSystemBuilder
from geoprob_pipe.calculations.system_calculations.piping_system.reliability_calculation import (
    PipingSystemReliabilityCalculation)
from typing import List, Dict, Union, Any
from geoprob_pipe.globals import ALLOWED_DISPERSION_TYPES
from geoprob_pipe.input_data.data_validation import is_number
from geoprob_pipe.input_data.ondergrond_scenario import OndergrondScenario
from geoprob_pipe.input_data.uittredepunt import Uittredepunt
from geoprob_pipe.input_data.utils import generate_parameter_dict
from geoprob_pipe.input_data.vak import VakCollection, Vak
from pandas import DataFrame, notna, Series
from probabilistic_library import FragilityValue


def generate_parameter_dict_for_constant(attr_name: str, df_overview_row: Series) -> dict:
    return generate_parameter_dict(attr_name, df_overview_row, df_row=None)


def enforce_lower_upper_bounds(parameter_dict: dict, id_print: str) -> None:
    # Note: only applicable to input parameters (variables and constants)

    # Value (mean) is accessed differently for deterministic and stochastic parameters
    attr_value = parameter_dict["value"] if parameter_dict["distribution"] == "deterministic" else parameter_dict[
        "mean"]

    # Make sure the attribute value is a number (int/float) before checking bounds
    if not is_number(attr_value):
        raise ValueError(
            f"Value of parameter '{parameter_dict["name"]}' ({id_print}) should be a number (int/float) since "
            f"lower/upper bounds were specified, but it's {attr_value} of type {type(attr_value)}")

    # Check if value lies within upper and lower bounds in parameter_dict (if specified)
    if notna(parameter_dict["lower_bound_mean"]):
        if not is_number(parameter_dict["lower_bound_mean"]):
            raise ValueError(
                f"Lower bound of parameter {parameter_dict["name"]} should be a number (int/float) but got "
                f"{parameter_dict["lower_bound_mean"]} of type {type(parameter_dict["lower_bound_mean"])}")
        if not (parameter_dict["lower_bound_mean"] <= attr_value):
            raise ValueError(
                f"Parameter '{parameter_dict["name"]}' ({id_print}) has a mean value that exceeds the lower bound "
                f"(value: {attr_value} < lower bound: {parameter_dict["lower_bound_mean"]})")

    if notna(parameter_dict["upper_bound_mean"]):
        if not is_number(parameter_dict["upper_bound_mean"]):
            raise ValueError(
                f"Upper bound of parameter {parameter_dict["name"]} should be a number (int/float) but got "
                f"{parameter_dict["upper_bound_mean"]} of type {type(parameter_dict["upper_bound_mean"])}")
        if not (attr_value <= parameter_dict["upper_bound_mean"]):
            raise ValueError(
                f"Parameter '{parameter_dict["name"]}' ({id_print}) has a mean value that exceeds the upper bound "
                f"(value: {attr_value} > upper bound: {parameter_dict["upper_bound_mean"]})")


class PipingSystemBuilder(BaseSystemBuilder):

    def __init__(self):
        super().__init__()
        self.system_class = PipingSystemReliabilityCalculation

    def build_single_instance(
            self,
            vak: Vak,
            uittredepunt,
            ondergrond_scenario,
            df_settings: DataFrame,
            df_constants: DataFrame,
            ):
        project_settings = self.construct_project_settings(df_settings=df_settings)
        calc = PipingSystemReliabilityCalculation(
                        system_variable_distributions=self.construct_system_variable_distributions(
                            vak=vak,
                            uittredepunt=uittredepunt,
                            ondergrond_scenario=ondergrond_scenario,
                            df_constants=df_constants,
                        ),
                        project_settings=project_settings
                    )
        calc.metadata["uittredepunt_id"] = uittredepunt.id
        calc.metadata["ondergrondscenario_id"] = ondergrond_scenario.id
        calc.metadata["ondergrondscenario"] = ondergrond_scenario
        calc.metadata["vak_id"] = vak.id

        metadata_summary = {
            "uittredepunt_id": uittredepunt.id,
            "ondergrondscenario_id": ondergrond_scenario.id,
            "vak_id": vak.id}
        calc.validation_messages.about = f"Calculation {metadata_summary}"
        return calc

    def build_instances(
            self,
            vak_collection: VakCollection,
            df_settings: DataFrame,
            df_constants: DataFrame,
            **kwargs) -> List[PipingSystemReliabilityCalculation]:
        """ """

        project_settings = self.construct_project_settings(df_settings=df_settings)

        list_calculations = []
        for vak in vak_collection.values():
            for uittredepunt in vak.uittredepunten:
                for ondergrond_scenario in vak.ondergrond_scenarios:
                    calc = PipingSystemReliabilityCalculation(
                        system_variable_distributions=self.construct_system_variable_distributions(
                            vak=vak,
                            uittredepunt=uittredepunt,
                            ondergrond_scenario=ondergrond_scenario,
                            df_constants=df_constants,
                        ),
                        project_settings=project_settings
                    )
                    calc.metadata["uittredepunt_id"] = uittredepunt.id
                    calc.metadata["ondergrondscenario_id"] = ondergrond_scenario.id
                    calc.metadata["ondergrondscenario"] = ondergrond_scenario
                    calc.metadata["vak_id"] = vak.id

                    metadata_summary = {
                        "uittredepunt_id": uittredepunt.id,
                        "ondergrondscenario_id": ondergrond_scenario.id,
                        "vak_id": vak.id}
                    calc.validation_messages.about = f"Calculation {metadata_summary}"

                    list_calculations.append(calc)
        return list_calculations

    @staticmethod
    def _construct_variable_distribution_dict(var_dict: Dict[str, Any]) -> Dict:
        # Create the Stochastic variable in the ReliabilityProject
        # Note: all supported variable attributes can be found in probabilistic_library.statistic.Stochast().__dir__()

        var_dist_dict = {"name": var_dict['name'], "distribution_type": var_dict["distribution"]}

        # Deterministic
        if var_dict["distribution"] == "deterministic":
            var_dist_dict['mean'] = var_dict["value"]

        # Other
        else:
            var_dist_dict['mean'] = var_dict["mean"]
            if var_dict["dispersion_type"] == "_stdev":
                var_dist_dict['deviation'] = var_dict["dispersion_value"]
            elif var_dict["dispersion_type"] == "_vc":
                var_dist_dict['variation'] = var_dict["dispersion_value"]
            else:
                raise NotImplementedError(
                    f"Dispersion type '{var_dict["dispersion_type"]}' of variable '{var_dict['name']}' is not "
                    f"implemented. Allowed types: {ALLOWED_DISPERSION_TYPES}")

        # Bounds
        if notna(var_dict["lower_bound_mean"]):
            var_dist_dict['minimum'] = var_dict["lower_bound_mean"]
        if notna(var_dict["upper_bound_mean"]):
            var_dist_dict['maximum'] = var_dict["upper_bound_mean"]

        # Return
        return var_dist_dict

    @staticmethod
    def _construct_buitenwaterstand_cdf_curve(uittredepunt: Uittredepunt) -> Dict:
        """ Bouwt de overschrijdingsfrequentielijn als stochastische variabele op. """

        # Initiate return dict
        var_dist_dict: Dict[str, Union[str, List]] = {"name": 'buitenwaterstand', "distribution_type": "cdf_curve"}

        # Create fragility points
        waterlevel = uittredepunt.overschrijdingsfrequentielijn.overschrijdingsfrequentielijn.level
        exceedance_frequency = uittredepunt.overschrijdingsfrequentielijn.overschrijdingsfrequentielijn.exceedance_frequency
        frag_points = []
        for i in range(0, len(waterlevel)):
            fc = FragilityValue()
            fc.x = waterlevel[i]
            fc.probability_of_failure = exceedance_frequency[i]
            frag_points.append(fc)
        var_dist_dict['fragility_values'] = frag_points
        return var_dist_dict

    def _collect_vak_variables(self, vak: Vak) -> List[Dict]:
        return_list = []
        for var_name, var_dict in vak.variables.__dict__.items():
            enforce_lower_upper_bounds(var_dict, f"Vak ID {vak.id}")
            return_list.append(self._construct_variable_distribution_dict(var_dict=var_dict))
        return return_list

    def _collect_uittredepunt_variables(self, uittredepunt: Uittredepunt) -> List[Dict]:
        return_list = []
        for var_name, var_dict in uittredepunt.variables.__dict__.items():
            enforce_lower_upper_bounds(var_dict, f"Uittredepunt ID {uittredepunt.id}")
            return_list.append(self._construct_variable_distribution_dict(var_dict=var_dict))
        return return_list

    def _collect_ondergrond_scenario_variables(self, ondergrond_scenario: OndergrondScenario) -> List[Dict]:
        return_list = []
        for var_name, var_dict in ondergrond_scenario.variables.__dict__.items():
            enforce_lower_upper_bounds(var_dict, f"Ondergrondscenario ID {ondergrond_scenario.id}")
            return_list.append(self._construct_variable_distribution_dict(var_dict=var_dict))
        return return_list

    def _collect_constants(self, df_constants: DataFrame):
        return_list = []
        for var_name, row in df_constants.iterrows():
            constant_dict = generate_parameter_dict_for_constant(str(var_name), df_overview_row=row)
            enforce_lower_upper_bounds(constant_dict, "located parameter overview sheet")
            return_list.append(self._construct_variable_distribution_dict(var_dict=constant_dict))
        return return_list

    def construct_system_variable_distributions(
            self, vak: Vak, uittredepunt: Uittredepunt, ondergrond_scenario: OndergrondScenario, df_constants: DataFrame, **kwargs
    ) -> List[Dict[str, Union[str, float, int]]]:
        system_variable_distributions = [self._construct_buitenwaterstand_cdf_curve(uittredepunt=uittredepunt)]
        system_variable_distributions.extend(self._collect_vak_variables(vak=vak))
        system_variable_distributions.extend(self._collect_uittredepunt_variables(uittredepunt=uittredepunt))
        system_variable_distributions.extend(self._collect_ondergrond_scenario_variables(
            ondergrond_scenario=ondergrond_scenario))
        system_variable_distributions.extend(self._collect_constants(df_constants=df_constants))
        return system_variable_distributions

    def construct_project_settings(self, df_settings: DataFrame, **kwargs) -> Dict[str, Union[str, float, int]]:
        return {str(attr_name): row['value'] for attr_name, row in df_settings.iterrows()}
