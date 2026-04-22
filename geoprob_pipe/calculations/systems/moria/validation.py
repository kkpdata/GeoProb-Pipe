from geoprob_pipe.calculations.systems.mappers.initial_input import INITIAL_INPUT_MORIA
from geoprob_pipe.utils.df_validation import ColumnValidation, requirements


PARAMETER = ColumnValidation(column_name="parameter", requirements=[
        requirements.IsIn(values=[item["name"] for item in INITIAL_INPUT_MORIA])])


MORIA_VALIDATION_REQUIREMENTS = {
    "Parameter invoer": [PARAMETER]
}
