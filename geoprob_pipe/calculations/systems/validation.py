from geoprob_pipe.utils.df_validation import ColumnValidation, requirements, ValidationRequirement, filters


FILTER_IS_NOT_CDF_CURVE = filters.is_in(column="distribution_type", values=['deterministic', 'log_normal', 'normal'])


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


D70 = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=-0.00001, right=0.001, filters=filters.combine(
            filters.is_in(column="parameter", values=["d70"]),
            FILTER_IS_NOT_CDF_CURVE))])


D70_M = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=-0.00001, right=0.001, filters=filters.combine(
            filters.is_in(column="parameter", values=["d70_m"]),
            FILTER_IS_NOT_CDF_CURVE))])


ETA = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=0.1, right=0.9, filters=filters.combine(
            filters.is_in(column="parameter", values=["eta"]),
            FILTER_IS_NOT_CDF_CURVE))])


G = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=5, right=20, filters=filters.combine(
            filters.is_in(column="parameter", values=["g"]),
            FILTER_IS_NOT_CDF_CURVE))])


GAMMA_KORREL = ColumnValidation(column_name="mean", requirements=[
    ValidationRequirement(
        requirement=requirements.is_in_range(left=23.0, right=29.0, inclusive="both"),
        failure_msg="De parameter 'gamma_korrel' hoort 26.0 te zijn. "
                    "De applicatie vereist dat deze tussen 23.0 en 29.0 is. ",
        filters=filters.combine(filters.is_in(column="parameter", values=["gamma_korrel"]),
                                FILTER_IS_NOT_CDF_CURVE))])


GAMMA_SAT_DEKLAAG = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=9.81, right=25, filters=filters.combine(
            filters.is_in(column="parameter", values=["gamma_sat_deklaag"]),
            FILTER_IS_NOT_CDF_CURVE))])


GAMMA_WATER = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=5, right=20, filters=filters.combine(
            filters.is_in(column="parameter", values=["gamma_water"]),
            FILTER_IS_NOT_CDF_CURVE))])


I_C_H = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=0.05, right=1.0, filters=filters.combine(
            filters.is_in(column="parameter", values=["i_c_h"]),
            FILTER_IS_NOT_CDF_CURVE))])


K_WVP = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=1, right=400, filters=filters.combine(
            filters.is_in(column="parameter", values=["k_wvp"]),
            FILTER_IS_NOT_CDF_CURVE))])


LAMBDA_VOORLAND = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=0, right=5_000, filters=filters.combine(
            filters.is_in(column="parameter", values=["lambda_voorland"]),
            FILTER_IS_NOT_CDF_CURVE))])


MODELFACTOR_3D = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=0.5, right=5, filters=filters.combine(
            filters.is_in(column="parameter", values=["modelfactor_3d"]),
            FILTER_IS_NOT_CDF_CURVE))])


MODELFACTOR_ANISO = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=0.5, right=5, filters=filters.combine(
            filters.is_in(column="parameter", values=["modelfactor_aniso"]),
            FILTER_IS_NOT_CDF_CURVE))])


MODELFACTOR_FF = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=0.5, right=5, filters=filters.combine(
            filters.is_in(column="parameter", values=["modelfactor_ff"]),
            FILTER_IS_NOT_CDF_CURVE))])


MODELFACTOR_H = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=0.5, right=5, filters=filters.combine(
            filters.is_in(column="parameter", values=["modelfactor_h"]),
            FILTER_IS_NOT_CDF_CURVE))])


MODELFACTOR_ML = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=0.5, right=5, filters=filters.combine(
            filters.is_in(column="parameter", values=["modelfactor_ml"]),
            FILTER_IS_NOT_CDF_CURVE))])


MODELFACTOR_P = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=0.5, right=5, filters=filters.combine(
            filters.is_in(column="parameter", values=["modelfactor_p"]),
            FILTER_IS_NOT_CDF_CURVE))])


MODELFACTOR_U = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=0.5, right=5, filters=filters.combine(
            filters.is_in(column="parameter", values=["modelfactor_u"]),
            FILTER_IS_NOT_CDF_CURVE))])


MV_EXIT = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=-99, right=999, filters=filters.combine(
            filters.is_in(column="parameter", values=["mv_exit"]),
            FILTER_IS_NOT_CDF_CURVE))])


PHI_EXIT_GEMIDDELD = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=-99, right=999, filters=filters.combine(
            filters.is_in(column="parameter", values=["phi_exit_gemiddeld"]),
            FILTER_IS_NOT_CDF_CURVE))])


POLDERPEIL = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=-99, right=999, filters=filters.combine(
            filters.is_in(column="parameter", values=["polderpeil"]),
            FILTER_IS_NOT_CDF_CURVE))])


R_C_DEKLAAG = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=0, right=2, filters=filters.combine(
            filters.is_in(column="parameter", values=["r_c_deklaag"]),
            FILTER_IS_NOT_CDF_CURVE))])


R_EXIT = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=0.0, right=1.0, filters=filters.combine(
            filters.is_in(column="parameter", values=["r_exit"]),
            FILTER_IS_NOT_CDF_CURVE))])


THETA = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=15, right=60, filters=filters.combine(
            filters.is_in(column="parameter", values=["theta"]),
            FILTER_IS_NOT_CDF_CURVE))])


TOP_ZAND = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=-99, right=999, filters=filters.combine(
            filters.is_in(column="parameter", values=["top_zand"]),
            FILTER_IS_NOT_CDF_CURVE))])


V = ColumnValidation(column_name="mean", requirements=[
    requirements.IsInRange(
        left=0.0000001, right=0.00001, filters=filters.combine(
            filters.is_in(column="parameter", values=["v"]),
            FILTER_IS_NOT_CDF_CURVE))])
