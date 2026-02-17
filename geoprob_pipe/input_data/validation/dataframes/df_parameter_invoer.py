from typing import List
# from pandera.pandas import DataFrameSchema, Column, Check
from geoprob_pipe.input_data.validation.dataframes.validation_objects import FailureQuery


FAILURE_QUERIES: List[FailureQuery] = [
    FailureQuery(
        query="distribution_type == 'cdf_curve' and fragility_values_ref.isnull()",
        msg="Geen referentie naar de fragility values gespecificeerd voor deze rij. Dit is vereist bij distributie "
            "type 'cdf_curve'."
    ),
    FailureQuery(
        query="distribution_type in ['normal', 'log_normal'] and mean.isnull()",
        msg="Geen gemiddelde waarde gespecificeerd voor deze rij. Dit is vereist bij distributie types 'normal' en "
            "'log_normal'."
    ),
    FailureQuery(
        query="distribution_type in ['normal', 'log_normal'] and variation.isnull() and deviation.isnull()",
        msg="Geen variatie coefficient of standaard deviatie gespecificeerd voor deze rij. Dit is vereist bij "
            "distributie types 'normal' en 'log_normal'."
    ),
]


# DISTRIBUTION_TYPE_CDF_CURVE = DataFrameValidation(
#     label="df_parameter_invoer",
#     label_humanized="Parameter invoer",
#     schemas=[
#         ValidationSchema(
#             label_humanized="Validatie voor distributie type 'cdf_curve'",
#             query="distribution_type == 'cdf_curve'",
#             schema=DataFrameSchema(columns={"fragility_values_ref": Column(str)},
#         )),
#         ValidationSchema(
#             label_humanized="Validatie voor distributie type 'normal' en 'log_normal'",
#             query="distribution_type == 'normal' or distribution_type == 'log_normal'",
#             schema=DataFrameSchema(
#                 columns={
#                     "variation": Column(float, nullable=True, checks=Check(lambda s: s > 10)),
#                     "deviation": Column(float, nullable=True),
#                 },
#                 checks=[
#                     Check(lambda df: df["variation"].notna() | df["deviation"].notna(),
#                           name="variation_or_deviation_provided"),
#                 ],
#         )),
#     ]
# )
#
#
# DF_PARAMETER_INVOER_VALIDATION: List[DataFrameValidation] = [
#     DISTRIBUTION_TYPE_CDF_CURVE,
# ]
#
#
# obj = DataFrameSchema(
#     columns={
#         "variation": Column(float, nullable=True, checks=Check(lambda item: item > 10)),
#     },
# )
