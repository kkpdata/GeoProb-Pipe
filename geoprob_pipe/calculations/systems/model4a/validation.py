from geoprob_pipe.calculations.systems.mappers.initial_input import INITIAL_INPUT_MODEL4A
from geoprob_pipe.utils.df_validation import ColumnValidation, requirements
from geoprob_pipe.calculations.systems.validation import GAMMA_KORREL


PARAMETER = ColumnValidation(column_name="parameter", requirements=[
        requirements.IsIn(values=[item["name"] for item in INITIAL_INPUT_MODEL4A])])


MODEL4A_VALIDATION_REQUIREMENTS = {
    "Parameter invoer": [PARAMETER, GAMMA_KORREL]
}
