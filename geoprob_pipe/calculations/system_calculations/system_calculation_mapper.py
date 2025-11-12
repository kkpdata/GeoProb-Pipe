from geoprob_pipe.calculations.system_calculations.piping_moria.system_builder import MoriaSystemBuilder
from geoprob_pipe.calculations.system_calculations.piping_system.system_builder import PipingSystemBuilder
from geoprob_pipe.calculations.system_calculations.piping_wbi.system_builder import WBISystemBuilder

# TODO: Dynamisch maken? Forceren dat naamgeving overeenkomt en we dynamisch importeren?


SYSTEM_CALCULATION_MAPPER = {
    "model4a": {
        "label": "Model 4a",
        "system_builder": PipingSystemBuilder,
    },
    "wbi": {
        "label": "WBI",
        "system_builder": WBISystemBuilder,
    },
    "moria": {
        "label": "MORIA",
        "system_builder": MoriaSystemBuilder,
    },
}
