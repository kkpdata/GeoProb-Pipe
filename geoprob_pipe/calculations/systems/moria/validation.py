from geoprob_pipe.calculations.systems.mappers.initial_input import INITIAL_INPUT_MORIA
from geoprob_pipe.utils.df_validation import ColumnValidation, requirements, filters
from geoprob_pipe.calculations.systems.validation import (
    GAMMA_KORREL, D_WVP, L_BUT, L_INTREDE, BUITENWATERSTAND, FILTER_IS_NOT_CDF_CURVE)


PARAMETER = ColumnValidation(column_name="parameter", requirements=[
        requirements.IsIn(values=[item["name"] for item in INITIAL_INPUT_MORIA])])


BUITENWATERSTAND_GEMIDDELD = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=-99, right=999, filters=filters.combine(
            filters.is_in(column="parameter", values=["buitenwaterstand_gemiddeld"]),
            FILTER_IS_NOT_CDF_CURVE))])


MORIA_VALIDATION_REQUIREMENTS = {
    "Parameter invoer": [
        PARAMETER,
        D_WVP, L_BUT, L_INTREDE, BUITENWATERSTAND, BUITENWATERSTAND_GEMIDDELD, GAMMA_KORREL,
    ]
}
