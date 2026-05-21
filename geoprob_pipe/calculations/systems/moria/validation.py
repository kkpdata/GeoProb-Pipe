from geoprob_pipe.calculations.systems.mappers.initial_input import INITIAL_INPUT_MORIA
from geoprob_pipe.utils.df_validation import ColumnValidation, requirements, filters
from geoprob_pipe.calculations.systems.validation import (
    FILTER_IS_NOT_CDF_CURVE, D_WVP, L_BUT, L_INTREDE, BUITENWATERSTAND, D70, D70_M, ETA, G, GAMMA_KORREL,
    GAMMA_SAT_DEKLAAG, GAMMA_WATER, I_C_H, K_WVP, LAMBDA_VOORLAND, MODELFACTOR_3D, MODELFACTOR_ANISO, MODELFACTOR_FF,
    MODELFACTOR_H, MODELFACTOR_ML, MODELFACTOR_P, MODELFACTOR_U, MV_EXIT, PHI_EXIT_GEMIDDELD, POLDERPEIL, R_C_DEKLAAG,
    R_EXIT, THETA, TOP_ZAND, V)


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
        D_WVP, L_BUT, L_INTREDE, BUITENWATERSTAND, BUITENWATERSTAND_GEMIDDELD, D70, D70_M, ETA, G, GAMMA_KORREL,
        GAMMA_SAT_DEKLAAG, GAMMA_WATER, I_C_H, K_WVP, LAMBDA_VOORLAND, MODELFACTOR_3D, MODELFACTOR_ANISO,
        MODELFACTOR_FF, MODELFACTOR_H, MODELFACTOR_ML, MODELFACTOR_P, MODELFACTOR_U, MV_EXIT, PHI_EXIT_GEMIDDELD,
        POLDERPEIL, R_C_DEKLAAG, R_EXIT, THETA, TOP_ZAND, V
    ]
}
