from typing import List
from pandera.pandas import DataFrameSchema, Column
from geoprob_pipe.input_data.validation.dataframes._validation_objects import DataFrameValidation, ValidationSchema


DISTRIBUTION_TYPE_CDF_CURVE = DataFrameValidation(
    label="df_parameter_invoer",
    label_humanized="Parameter invoer",
    schemas=[
        ValidationSchema(
            label_humanized="Validatie voor distributie type 'cdf_curve'",
            query="distribution_type == 'cdf_curve'", schema=DataFrameSchema(
            columns={"fragility_values_ref": Column(str)},
        )),
    ]
)


DF_PARAMETER_INVOER_VALIDATION: List[DataFrameValidation] = [
    DISTRIBUTION_TYPE_CDF_CURVE,
]
