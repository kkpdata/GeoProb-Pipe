from geoprob_pipe.utils.df_validation import ColumnValidation, requirements, ValidationRequirement, filters


FILTER_IS_NOT_CDF_CURVE = filters.is_in(column="distribution_type", values=['deterministic', 'log_normal', 'normal'])


GAMMA_KORREL = ColumnValidation(column_name="mean", requirements=[
    ValidationRequirement(
        requirement=requirements.is_in_range(left=23.0, right=29.0, inclusive="both"),
        failure_msg=f"De parameter 'gamma_korrel' hoort 26.0 te zijn. "
                    f"De applicatie vereist dat deze tussen 23.0 en 29.0 is. ",
        filters=filters.combine(filters.is_in(column="parameter", values=["gamma_korrel"]),
                                FILTER_IS_NOT_CDF_CURVE))])


D_WVP = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=0.2, right=1_000,
        filters=filters.combine(
            filters.is_in(column="parameter", values=["D_wvp"]),
            FILTER_IS_NOT_CDF_CURVE))])


L_BUT = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=1, right=2_000,
        filters=filters.combine(
            filters.is_in(column="parameter", values=["L_but"]),
            FILTER_IS_NOT_CDF_CURVE))])


L_INTREDE = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=2, right=5_000,
        filters=filters.combine(
            filters.is_in(column="parameter", values=["L_intrede"]),
            FILTER_IS_NOT_CDF_CURVE))])


BUITENWATERSTAND = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=-99, right=999, filters=filters.combine(
            filters.is_in(column="parameter", values=["buitenwaterstand"]),
            FILTER_IS_NOT_CDF_CURVE))])
