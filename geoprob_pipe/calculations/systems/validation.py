from geoprob_pipe.utils.df_validation import ColumnValidation, requirements, ValidationRequirement, filters


GAMMA_KORREL = ColumnValidation(column_name="mean", requirements=[
    ValidationRequirement(
        requirement=requirements.is_in_range(left=23.0, right=29.0, inclusive="both"),
        failure_msg=f"De parameter 'gamma_korrel' hoort 26.0 te zijn. "
                    f"De applicatie vereist dat deze tussen 23.0 en 29.0 is. ",
        filters=filters.is_in(column="parameter", values=["gamma_korrel"])
    )
])
