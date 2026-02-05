from geoprob_pipe.calculations.systems.moria.initial_input import INITIAL_INPUT as INITIAL_INPUT_MORIA
from geoprob_pipe.calculations.systems.model4a.initial_input import INITIAL_INPUT as INITIAL_INPUT_WBI
from geoprob_pipe.calculations.systems.wbi.initial_input import INITIAL_INPUT as INITIAL_INPUT_MODEL4A

# TODO: Dynamisch maken? Forceren dat naamgeving overeenkomt en we dynamisch importeren?


INITIAL_INPUT_MAPPER = {
    "model4a": {
        "label": "Model 4a",
        "dummy_invoer": INITIAL_INPUT_MODEL4A,  # TODO: Dit is nog de oude model 4a logica. Aanpassen?
    },
    "wbi": {
        "label": "WBI",
        "dummy_invoer": INITIAL_INPUT_WBI,
    },
    "moria": {
        "label": "MORIA",
        "dummy_invoer": INITIAL_INPUT_MORIA,
    },
}
