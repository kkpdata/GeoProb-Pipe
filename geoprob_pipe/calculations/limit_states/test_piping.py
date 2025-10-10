## Get data for testing
from pathlib import Path

import pytest

from . import piping

testset_path = Path(
    Path(__file__).resolve(strict=True).parents[3],
    "tests/testset",
    "testset_limitstate_piping.xlsx",
)


def get_data():
    """Get data for testing"""
    import pandas as pd

    data = pd.read_excel(testset_path, sheet_name="Blad1", header=0)
    return data


# define input and output keys
input_keys_calc_z_piping = [
    "c_voorland",  # c_voorland
    "buitenwaterstand",  # buitenwaterstand
    "polderpeil",  # polderpeil
    "mv_exit",  # mv_exit
    "L_but",  # L_but
    "L_intrede",  # L_intrede
    "modelfactor_p",  # modelfactor_h
    "d70",  # d70
    "D_wvp",  # D_wvp
    "kD_wvp",  # kD_wvp
    "top_zand",  # top_zand
    "gamma_water",  # GAMMA_WATER not in excel file, use global variable
    "g",  # G
    "v",  # V
    "theta",  # THETA
    "eta",  # ETA
    "d70_m",  # D70_M
    "gamma_korrel",  # GAMMA_KORREL
    "r_c_deklaag",  # r_c_deklaag
]

output_key_calc_z_piping = [
    "z_p",  # z_p
    "L_voorland",  # lengte_voorland
    "lambda_voorland",  # lambda_voorland
    "W_voorland",  # W_voorland
    "L_kwelweg",  # L_kwelweg
    "dh_c",  # dh_c
    "h_exit",  # h_exit
    "d_deklaag",  # d_deklaag
    "dh_red",  # dh_red
]

# global variables
# G = 9.81  # m/s^2
# V = 1.33e-6  # m^2/s
# ETA = 0.25  # [-]
# THETA = 37.0  # grd
# GAMMA_KORREL = 26.0  # kN/m^3
# GAMMA_WATER = 9.81  # kN/m^3
# D70_M = 2.08e-4  # m

# setup test construct
data_calc_z_piping = get_data()
inputs_calc_z_piping = data_calc_z_piping.loc[:, input_keys_calc_z_piping]
# add global variables in dataframe in the right order
# inputs_calc_z_piping["g"] = G
# inputs_calc_z_piping["v"] = V
# inputs_calc_z_piping["eta"] = ETA
# inputs_calc_z_piping["theta"] = THETA
# inputs_calc_z_piping["gamma_korrel"] = GAMMA_KORREL
# inputs_calc_z_piping["gamma_water"] = GAMMA_WATER
# inputs_calc_z_piping["d70_m"] = D70_M
# reorder columns
# input_keys_right_order = [
#     "c_voorland",  # c_voorland
#     "h",  # buitenwaterstand
#     "pp",  # polderpeil
#     "mv",  # mv_exit
#     "DIST_BUT",  # L_but
#     "DIST_L_GEOM",  # L_intrede
#     "mp",  # modelfactor_h
#     "D70",  # d70
#     "D_zand",  # D_wvp
#     "kD_WVP",  # kD_wvp
#     "top_zand",  # top_zand
#     "gamma_water",
#     "g",
#     "v",
#     "theta",
#     "eta",
#     "d70_m",
#     "gamma_korrel",
#     "rc",  # r_c_deklaag
# ]
inputs_calc_z_piping_dict = inputs_calc_z_piping.to_dict(orient="records")
expected_outputs_calc_z_piping = data_calc_z_piping[output_key_calc_z_piping].to_dict(
    orient="records"
)


@pytest.mark.parametrize(
    "inputs, expected", zip(inputs_calc_z_piping_dict, expected_outputs_calc_z_piping)
)
def test_calc_z_piping(inputs, expected):
    """Test calc_dh_c function with multiple test cases from excel file"""
    result = piping.z_piping(
        c_voorland=inputs["c_voorland"],
        buitenwaterstand=inputs["buitenwaterstand"],
        polderpeil=inputs["polderpeil"],
        mv_exit=inputs["mv_exit"],
        L_but=inputs["L_but"],
        L_intrede=inputs["L_intrede"],
        modelfactor_p=inputs["modelfactor_p"],
        d70=inputs["d70"],
        D_wvp=inputs["D_wvp"],
        kD_wvp=inputs["kD_wvp"],
        top_zand=inputs["top_zand"],
        gamma_water=inputs["gamma_water"],
        g=inputs["g"],
        v=inputs["v"],
        theta=inputs["theta"],
        eta=inputs["eta"],
        d70_m=inputs["d70_m"],
        gamma_korrel=inputs["gamma_korrel"],
        r_c_deklaag=inputs["r_c_deklaag"],
    )
    assert result[0] == pytest.approx(expected["z_p"], 0.01)
    assert result[1] == pytest.approx(expected["L_voorland"], 0.01)
    assert result[2] == pytest.approx(expected["lambda_voorland"], 0.01)
    assert result[3] == pytest.approx(expected["W_voorland"], 0.01)
    assert result[4] == pytest.approx(expected["L_kwelweg"], 0.01)
    assert result[5] == pytest.approx(expected["dh_c"], 0.01)
    assert result[6] == pytest.approx(expected["h_exit"], 0.01)
    assert result[7] == pytest.approx(expected["d_deklaag"], 0.01)
    assert result[8] == pytest.approx(expected["dh_red"], 0.01)
