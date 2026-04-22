from geoprob_pipe.utils.df_validation import (
    DataFrameValidation, ColumnValidation, ValidationRequirement, requirements, filters)
from pandas import DataFrame


PARAMETER = ColumnValidation(column_name="parameter", requirements=[requirements.IsString])

SCOPE = ColumnValidation(column_name="scope", requirements=[
    requirements.IsString,
    requirements.IsIn(values=["traject", "vak", "uittredepunt"]),
])

SCOPE_REFERENTIE = ColumnValidation(column_name="scope_referentie", requirements=[
    ValidationRequirement(
        requirement=requirements.is_whole_number,
        failure_msg=f"De scope referentie moet een integer (geheel getal) zijn wanneer de scope 'vak' "
                    f"of 'uittredepunt' is.",
        filters=filters.is_in(column="scope", values=["vak", "uittredepunt"])),
    ValidationRequirement(
        requirement=requirements.is_null,
        failure_msg=f"De scope referentie moet leeg zijn wanneer de scope 'traject' is.",
        filters=filters.is_in(column="scope", values=["traject"])),
])

ONDERGRONDSCENARIO_NAAM = ColumnValidation(column_name="ondergrondscenario_naam", requirements=[
    ValidationRequirement(
        requirement=requirements.is_null,
        failure_msg=f"De ondergrondscenario naam moet leeg zijn wanneer de scope 'traject' of 'uittredepunt' is.",
        filters=filters.is_in("scope", ["traject", "uittredepunt"])),
])

DISTRIBUTION_TYPE = ColumnValidation(column_name="distribution_type", requirements=[
    requirements.IsString,
    requirements.IsIn(values=["deterministic", "log_normal", "normal", "cdf_curve"]),
])

MEAN = ColumnValidation(column_name="mean", requirements=[
    ValidationRequirement(
        requirement=requirements.is_not_null,
        failure_msg=f"De mean moet ingevuld zijn wanneer het distributie "
                    f"type 'deterministic', 'log_normal' of 'normal' is.",
        filters=filters.is_in(column="distribution_type", values=['deterministic', 'log_normal', 'normal'])),
])

VARIATION = ColumnValidation(column_name="variation", requirements=[
    ValidationRequirement(
        requirement=requirements.is_not_null,
        failure_msg=f"De variatie coefficient moet ingevuld zijn wanneer het distributie "
                    f"type 'log_normal' of 'normal' is en standaard deviatie ook niet ingevuld is.",
        filters=filters.combine(
            filters.is_in(column="distribution_type", values=["log_normal", "normal"]),
            filters.is_null(column="deviation")
        )
    ),
])

DEVIATION = ColumnValidation(column_name="deviation", requirements=[
    ValidationRequirement(
        requirement=requirements.is_not_null,
        failure_msg=f"De standaard deviatie moet ingevuld zijn wanneer het distributie "
                    f"type 'log_normal' of 'normal' is en variatie coefficient ook niet ingevuld is.",
        filters=filters.combine(
            filters.is_in(column="distribution_type", values=["log_normal", "normal"]),
            filters.is_null(column="variation")
        )),
])

MINIMUM = ColumnValidation(column_name="minimum", requirements=[
    ValidationRequirement(
        requirement=requirements.is_null,
        failure_msg=f"De minimum-kolom is momenteel nog buiten gebruik. Laat deze kolom leeg."),
])

MAXIMUM = ColumnValidation(column_name="maximum", requirements=[
    ValidationRequirement(
        requirement=requirements.is_null,
        failure_msg=f"De maximum-kolom is momenteel nog buiten gebruik. Laat deze kolom leeg."),
])



class ValidationParameterInvoer(DataFrameValidation):

    def __init__(self, df: DataFrame):
        super().__init__(
            df=df,
            label="Parameter invoer",
            required_columns=[
                "parameter", "scope", "scope_referentie", "ondergrondscenario_naam", "distribution_type", "mean",
                "variation", "deviation", "minimum", "maximum", "fragility_values_ref", "bronnen", "opmerking"],
            columns_validations=[
                PARAMETER, SCOPE, SCOPE_REFERENTIE, ONDERGRONDSCENARIO_NAAM, DISTRIBUTION_TYPE, MEAN, VARIATION,
                DEVIATION, MINIMUM, MAXIMUM,
            ]
        )
