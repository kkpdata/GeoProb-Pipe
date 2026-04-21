from geoprob_pipe.utils.df_validation import (
    DataFrameValidation, ColumnValidation, IsIn, IsString, ValidationRequirement, is_integer, is_not_null, is_null)
from pandas import DataFrame, Series


def scope_is_traject(df: DataFrame) -> Series:
    return df["scope"].isin(["traject"])


def scope_is_traject_of_uittredepunt(df: DataFrame) -> Series:
    return df["scope"].isin(["traject", "uittredepunt"])


def scope_is_vak_of_uittredepunt(df: DataFrame) -> Series:
    return df["scope"].isin(["vak", "uittredepunt"])


def distribution_type_is_cdf_curve(df: DataFrame) -> Series:
    return df["distribution_type"].isin(["cdf_curve"])


def distribution_type_is_det_log_normal(df: DataFrame) -> Series:
    return df["distribution_type"].isin(['deterministic', 'log_normal', 'normal'])


def distribution_type_is_log_normal_and_dev_is_null(df: DataFrame) -> Series:
    return (df["distribution_type"].isin(['log_normal', 'normal']) &
            df["deviation"].isna())


def distribution_type_is_log_normal_and_var_is_null(df: DataFrame) -> Series:
    return (df["distribution_type"].isin(['log_normal', 'normal']) &
            df["variation"].isna())


PARAMETER = ColumnValidation(column_name="parameter", requirements=[IsString])

SCOPE = ColumnValidation(column_name="scope", requirements=[
    IsString,
    IsIn(values=["traject", "vak", "uittredepunt"]),
])

SCOPE_REFERENTIE = ColumnValidation(column_name="scope_referentie", requirements=[
    ValidationRequirement(
        requirement=is_integer,
        failure_msg=f"De scope referentie moet een integer (geheel getal) zijn wanneer de scope 'vak' "
                    f"of 'uittredepunt' is.",
        df_filter=scope_is_vak_of_uittredepunt),
    ValidationRequirement(
        requirement=is_null,
        failure_msg=f"De scope referentie moet leeg zijn wanneer de scope 'traject' is.",
        df_filter=scope_is_traject),
])

ONDERGRONDSCENARIO_NAAM = ColumnValidation(column_name="ondergrondscenario_naam", requirements=[
    ValidationRequirement(
        requirement=is_null,
        failure_msg=f"De ondergrondscenario naam moet leeg zijn wanneer de scope 'traject' of 'uittredepunt' is.",
        df_filter=scope_is_traject_of_uittredepunt),
])

DISTRIBUTION_TYPE = ColumnValidation(column_name="distribution_type", requirements=[
    IsString,
    IsIn(values=["deterministic", "log_normal", "normal", "cdf_curve"]),
])

MEAN = ColumnValidation(column_name="mean", requirements=[
    ValidationRequirement(
        requirement=is_not_null,
        failure_msg=f"De mean moet ingevuld zijn wanneer het distributie "
                    f"type 'deterministic', 'log_normal' of 'normal' is.",
        df_filter=distribution_type_is_det_log_normal),
])

VARIATION = ColumnValidation(column_name="variation", requirements=[
    ValidationRequirement(
        requirement=is_not_null,
        failure_msg=f"De variatie coefficient moet ingevuld zijn wanneer het distributie "
                    f"type 'log_normal' of 'normal' is en standaard deviatie ook niet ingevuld is.",
        df_filter=distribution_type_is_log_normal_and_dev_is_null),
])

DEVIATION = ColumnValidation(column_name="deviation", requirements=[
    ValidationRequirement(
        requirement=is_not_null,
        failure_msg=f"De standaard deviatie moet ingevuld zijn wanneer het distributie "
                    f"type 'log_normal' of 'normal' is en variatie coefficient ook niet ingevuld is.",
        df_filter=distribution_type_is_log_normal_and_var_is_null),
])

MINIMUM = ColumnValidation(column_name="minimum", requirements=[
    ValidationRequirement(
        requirement=is_null,
        failure_msg=f"De minimum-kolom is momenteel nog buiten gebruik. Laat deze kolom leeg."),
])

MAXIMUM = ColumnValidation(column_name="maximum", requirements=[
    ValidationRequirement(
        requirement=is_null,
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
