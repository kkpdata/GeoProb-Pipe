""" The below defined validation is additional to that inside geoprob_pipe.input_data.df_validation.
The difference is that here it is model-specific, whereas the other it is generic to the specific dataframe. """

from geoprob_pipe.calculations.systems.moria.validation import MORIA_VALIDATION_REQUIREMENTS

VALIDATION_MAPPER = {
    "model4a": {},  # TODO
    "wbi": {},  # TODO
    "moria": MORIA_VALIDATION_REQUIREMENTS,  # TODO: Extend majorly
}
