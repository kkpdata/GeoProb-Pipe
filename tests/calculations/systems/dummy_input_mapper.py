from tests.calculations.system_calculations.moria.dummy_input import DUMMY_INPUT as DUMMY_INPUT_MORIA
from tests.calculations.system_calculations.wbi.dummy_input import DUMMY_INPUT as DUMMY_INPUT_WBI
from tests.calculations.system_calculations.system.dummy_input import DUMMY_INPUT as DUMMY_INPUT_MODEL4A

# TODO: Dynamisch maken? Forceren dat naamgeving overeenkomt en we dynamisch importeren?


DUMMY_INPUT_MAPPER = {
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
