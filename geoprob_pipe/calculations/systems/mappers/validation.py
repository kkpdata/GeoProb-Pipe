""" The below defined validation is additional to that inside geoprob_pipe.input_data.df_validation.
The difference is that here it is model-specific, whereas the other it is generic to the specific dataframe. """

from geoprob_pipe.calculations.systems.moria.validation import MORIA_VALIDATION_REQUIREMENTS
from geoprob_pipe.calculations.systems.model4a.validation import MODEL4A_VALIDATION_REQUIREMENTS
from geoprob_pipe.calculations.systems.wbi.validation import WBI_VALIDATION_REQUIREMENTS


VALIDATION_MAPPER = {
    "model4a": MODEL4A_VALIDATION_REQUIREMENTS,  # TODO: Extend majorly
    "wbi": WBI_VALIDATION_REQUIREMENTS,  # TODO: Extend majorly
    "moria": MORIA_VALIDATION_REQUIREMENTS,  # TODO: Extend majorly
}
