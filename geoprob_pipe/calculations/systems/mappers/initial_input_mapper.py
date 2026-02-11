from geoprob_pipe.calculations.systems.moria.initial_input import (
    INITIAL_INPUT as INITIAL_INPUT_MORIA)
from geoprob_pipe.calculations.systems.model4a.initial_input import (
    INITIAL_INPUT as INITIAL_INPUT_MODEL4A)
from geoprob_pipe.calculations.systems.wbi.initial_input import (
    INITIAL_INPUT as INITIAL_INPUT_WBI)

# TODO: Dynamisch maken? Forceren dat naamgeving overeenkomt en
# we dynamisch importeren?


INITIAL_INPUT_MAPPER = {
    # TODO: Dit is nog de oude model 4a logica. Aanpassen?
    "model4a": {
        "label": "Model 4a",
        "input": INITIAL_INPUT_MODEL4A,
    },
    "wbi": {
        "label": "WBI",
        "input": INITIAL_INPUT_WBI,
    },
    "moria": {
        "label": "MORIA",
        "input": INITIAL_INPUT_MORIA,
    },
}
