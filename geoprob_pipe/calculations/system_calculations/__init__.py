from geoprob_pipe.calculations.system_calculations.piping_moria.dummy_input import PIPING_DUMMY_INPUT as DUMMY_INPUT_MORIA
from geoprob_pipe.calculations.system_calculations.piping_wbi.dummy_input import PIPING_DUMMY_INPUT as DUMMY_INPUT_WBI
from geoprob_pipe.calculations.system_calculations.piping_system.dummy_input import DUMMY_INPUT as DUMMY_INPUT_MODEL4A
# TODO: Dynamisch maken? Forceren dat naamgeving overeenkomt en we dynamisch importeren?


SYSTEM_CALCULATION_MAPPER = {
    "model4a": {
        "label": "Model 4a",
        "dummy_invoer": DUMMY_INPUT_MODEL4A,  # TODO: Dit is nog de oude model 4a logica. Aanpassen?
    },
    "wbi": {
        "label": "WBI",
        "dummy_invoer": DUMMY_INPUT_WBI,
    },
    "moria": {
        "label": "MORIA",
        "dummy_invoer": DUMMY_INPUT_MORIA,
    },
}
