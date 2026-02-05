from geoprob_pipe.calculations.systems.moria.system_builder import MoriaSystemBuilder
from geoprob_pipe.calculations.systems.piping_system.system_builder import PipingSystemBuilder
from geoprob_pipe.calculations.systems.piping_wbi.system_builder import WBISystemBuilder
from geoprob_pipe.calculations.limit_states.piping_lm import limit_state_moria
from geoprob_pipe.calculations.systems.piping_system.limit_state_functions import limit_state_model4a
# TODO: Dynamisch maken? Forceren dat naamgeving overeenkomt en we dynamisch importeren?


SYSTEM_CALCULATION_MAPPER = {
    "model4a": {
        "label": "Model 4a",
        "system_builder": PipingSystemBuilder,
        "system_return_parameter_keys": [
            "z_u", "z_h", "z_p", "z_combin", "h_exit", "r_exit", "phi_exit", "d_deklaag", "dphi_c_u", "i_exit",
            "L_voorland", "lambda_voorland", "W_voorland", "L_kwelweg", "dh_c", "dh_red"],
        "limit_state_function": limit_state_model4a,
    },
    "wbi": {
        "label": "WBI",
        "system_builder": WBISystemBuilder,
    },
    "moria": {
        "label": "MORIA",
        "system_builder": MoriaSystemBuilder,
        "system_return_parameter_keys": [
            "z_u", "z_h", "z_p", "z_combin", "h_exit", "phi_exit", "d_deklaag", "dphi_c_u", "i_exit",
            "L_voorland", "W_voorland", "L_kwelweg", "kD_wvp", "dh_c", "dh_red"],
        "limit_state_function": limit_state_moria,
    },
}
