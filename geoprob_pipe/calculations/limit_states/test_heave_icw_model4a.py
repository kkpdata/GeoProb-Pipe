## Get data for testing
from pathlib import Path

import pytest

from . import heave_icw_model4a

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
input_keys_calc_z_heave = [
    "L_achterland",  # L_achterland
    "c_voorland",  # c_voorland
    "c_achterland",  # c_achterland
    "L_intrede",  # L_intrede
    "L_but",  # L_but
    "L_bit",  # L_bit
    "polderpeil",  # polderpeil
    "buitenwaterstand",  # buitenwaterstand
    "mv_exit",  # mv_exit
    "top_zand",  # top_zand
    "kD_wvp",  # kD_wvp
    "modelfactor_h",  # modelfactor_h
    "i_c_h",  # i_c_h
    "D_wvp",  # D_wvp
]

output_key_calc_z_heave = [
    "z_h",  # z_h
    "L_voorland",  # lengte_voorland
    "r_exit",  # r_exit
    "phi_exit",  # phi_exit
    "h_exit",  # h_exit
    "d_deklaag",  # d_deklaag
    "i_exit",  # i_exit
]

# global variables - also defined in teststet excel file
# G = 9.81  # m/s^2
# V = 1.33e-6  # m^2/s
# ETA = 0.25  # [-]
# THETA = 37.0  # grd
# GAMMA_KORREL = 26.0  # kN/m^3
# D70_M = 2.08e-4  # m

# setup test construct
data_calc_z_heave = get_data()
inputs_calc_z_heave = data_calc_z_heave[input_keys_calc_z_heave].to_dict(
    orient="records"
)
expected_outputs_calc_z_heave = data_calc_z_heave[output_key_calc_z_heave].to_dict(
    orient="records"
)


@pytest.mark.parametrize(
    "inputs, expected", zip(inputs_calc_z_heave, expected_outputs_calc_z_heave)
)
def test_calc_z_heave(inputs, expected):
    """Test calc_dh_c function with multiple test cases from excel file"""
    result = heave_icw_model4a.z_heave(
        L_achterland=inputs["L_achterland"],
        c_voorland=inputs["c_voorland"],
        c_achterland=inputs["c_achterland"],
        L_intrede=inputs["L_intrede"],
        L_but=inputs["L_but"],
        L_bit=inputs["L_bit"],
        polderpeil=inputs["polderpeil"],
        buitenwaterstand=inputs["buitenwaterstand"],
        mv_exit=inputs["mv_exit"],
        top_zand=inputs["top_zand"],
        kD_wvp=inputs["kD_wvp"],
        modelfactor_h=inputs["modelfactor_h"],
        i_c_h=inputs["i_c_h"],
        D_wvp=inputs["D_wvp"],
    )
    assert result[0] == pytest.approx(expected["z_h"], 0.01)
    assert result[1] == pytest.approx(expected["L_voorland"], 0.01)
    assert result[2] == pytest.approx(expected["r_exit"], 0.01)
    assert result[3] == pytest.approx(expected["phi_exit"], 0.01)
    assert result[4] == pytest.approx(expected["h_exit"], 0.01)
    assert result[5] == pytest.approx(expected["d_deklaag"], 0.01)
    assert result[6] == pytest.approx(expected["i_exit"], 0.01)
