from geoprob_pipe.calculations.system_calculations.system_base_objects.base_system_build import BaseSystemBuilder
from geoprob_pipe.calculations.system_calculations.piping_system.reliability_calculation import (
    PipingSystemReliabilityCalculation)
from typing import List, Dict, Union, Any
from geoprob_pipe.globals import ALLOWED_DISPERSION_TYPES
from geoprob_pipe.helper_functions.data_validation import enforce_lower_upper_bounds
from geoprob_pipe.helper_functions.parameter_functions import generate_parameter_dict_for_constant
from geoprob_pipe.input_data.ondergrond_scenario import OndergrondScenario
from geoprob_pipe.input_data.uittredepunt import Uittredepunt
from geoprob_pipe.input_data.vak import VakCollection, Vak
from pandas import DataFrame, notna
from probabilistic_library import FragilityValue


class PipingSystemBuilder(BaseSystemBuilder):

    def __init__(self):
        super().__init__()
        self.system_class = PipingSystemReliabilityCalculation

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


# project.input_data.uittredepunten[0].variables.__dict__.keys()
# Out[10]: dict_keys(['L_intrede', 'L_but', 'L_bit', 'mv_exit', 'polderpeil'])
# project.input_data.uittredepunten[0].vak.variables.__dict__.keys()
# Out[11]: dict_keys(['mv_achterland_vak', 'L_achterland', 'c_voorland'])
# project.input_data.uittredepunten[0].vak.ondergrond_scenarios[0].variables.__dict__.keys()
# Out[17]: dict_keys(['ondergrondscenario_kans', 'top_zand', 'gamma_sat_deklaag', 'D_wvp', 'kD_wvp', 'd70', 'c_achterland'])

