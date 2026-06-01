from geoprob_pipe.utils.df_validation import (
    DataFrameValidation, ColumnValidation, ValidationRequirement, requirements)
from pandas import DataFrame


POLDERPEIL = ColumnValidation(column_name="polderpeil", requirements=[
    ValidationRequirement(
        requirement=requirements.is_not_null,
        failure_msg=f"De waarde van het polderpeil moet ingevuld zijn met een numerieke waarde. Eén of meerdere "
                    f"rijen heeft geen waarde."),
    ValidationRequirement(
        requirement=requirements.is_numeric,
        failure_msg=f"De waarde van het polderpeil moet een numerieke waarde hebben. Eén of meerdere rijen voldoet "
                    f"hier niet aan. ",
    ),
    requirements.IsInRange(left=-99, right=999),
])

class ValidationPolderpeilen(DataFrameValidation):

    def __init__(self, df: DataFrame):
        super().__init__(
            df=df,
            label="Polderpeilen",
            required_columns=[],
            columns_validations=[POLDERPEIL]
        )
