"""Tests for piping limit state calculations in piping_lm.py. There are three functions to be tested:
- limit_state_wbi
- limit_state_model4a
- limit_state_moria

"""

from pathlib import Path

import pytest

from . import piping_lm

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
input_keys_lm_wbi = [
    "L_kwelweg",
    "buitenwaterstand",
    "polderpeil",
    "mv_exit",
    "top_zand",
    "r_exit",
    "k_wvp",
    "D_wvp",
    "d70",
    "gamma_sat_deklaag",
    "modelfactor_u",
    "modelfactor_h",
    "modelfactor_p",
    "modelfactor_ff",
    "modelfactor_3d",
    "modelfactor_aniso",
    "modelfactor_ml",
    "i_c_h",
    "r_c_deklaag",
    "d70_m",
    "gamma_korrel",
    "v",
    "theta",
    "eta",
    "g",
    "gamma_water",
]

output_keys_lm_wbi = [
    "z_u",
    "z_h",
    "z_p",
    "z_combin",
    "h_exit",
    "phi_exit",
    "dphi_c_u",
    "i_exit",
    "dh_c",
    "dh_red",
]

input_keys_lm_model4a = [
    "L_intrede",
    "L_but",
    "L_bit",
    "L_achterland",
    "buitenwaterstand",
    "polderpeil",
    "mv_exit",
    "top_zand",
    "kD_wvp",
    "D_wvp",
    "d70",
    "gamma_sat_deklaag",
    "c_voorland",
    "c_achterland",
    "modelfactor_u",
    "modelfactor_h",
    "modelfactor_p",
    "modelfactor_ff",
    "modelfactor_3d",
    "modelfactor_aniso",
    "modelfactor_ml",
    "i_c_h",
    "r_c_deklaag",
    "d70_m",
    "gamma_korrel",
    "v",
    "theta",
    "eta",
    "g",
    "gamma_water",
]

output_keys_lm_model4a = [
    "z_u",
    "z_h",
    "z_p",
    "z_combin",
    "h_exit",
    "r_exit",
    "phi_exit",
    "d_deklaag",
    "dphi_c_u",
    "i_exit",
    "L_voorland",
    "lambda_voorland",
    "W_voorland",
    "L_kwelweg",
    "dh_c",
    "dh_red",
]

input_keys_lm_moria = [
    "L_intrede",
    "L_but",
    "buitenwaterstand",
    "buitenwaterstand_gemiddeld",
    "polderpeil",
    "mv_exit",
    "lambda_voorland",
    "phi_exit_gemiddeld",
    "r_exit",
    "top_zand",
    "k_wvp",
    "D_wvp",
    "d70",
    "gamma_sat_deklaag",
    "modelfactor_u",
    "modelfactor_h",
    "modelfactor_p",
    "modelfactor_ff",
    "modelfactor_3d",
    "modelfactor_aniso",
    "modelfactor_ml",
    "i_c_h",
    "r_c_deklaag",
    "d70_m",
    "gamma_korrel",
    "v",
    "theta",
    "eta",
    "g",
    "gamma_water",
]

output_keys_lm_moria = [
    "z_u",
    "z_h",
    "z_p",
    "z_combin",
    "h_exit",
    "r_exit",
    "phi_exit",
    "d_deklaag",
    "dphi_c_u",
    "i_exit",
    "L_voorland",
    "W_voorland",
    "L_kwelweg",
    "kD_wvp",
    "dh_c",
    "dh_red",
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
test_data = get_data()

# extract inputs and expected outputs for limit_state_wbi
inputs_lm_wbi = test_data.loc[:, input_keys_lm_wbi]

# add global variables in dataframe in the right order
# inputs_lm_wbi["g"] = G
# inputs_lm_wbi["v"] = V
# inputs_lm_wbi["eta"] = ETA
# inputs_lm_wbi["theta"] = THETA
# inputs_lm_wbi["gamma_korrel"] = GAMMA_KORREL
# inputs_lm_wbi["gamma_water"] = GAMMA_WATER
# inputs_lm_wbi["d70_m"] = D70_M

inputs_lm_wbi_dict = inputs_lm_wbi.to_dict(orient="records")
expected_outputs_lm_wbi = test_data[output_keys_lm_wbi].to_dict(orient="records")


@pytest.mark.parametrize(
    "input_data, expected", zip(inputs_lm_wbi_dict, expected_outputs_lm_wbi)
)
def test_limit_state_wbi(input_data, expected):
    """Test limit_state_wbi function"""
    results = piping_lm.limit_state_wbi(
        L_kwelweg=input_data["L_kwelweg"],
        buitenwaterstand=input_data["buitenwaterstand"],
        polderpeil=input_data["polderpeil"],
        mv_exit=input_data["mv_exit"],
        top_zand=input_data["top_zand"],
        r_exit=input_data["r_exit"],
        k_wvp=input_data["k_wvp"],
        D_wvp=input_data["D_wvp"],
        d70=input_data["d70"],
        gamma_sat_deklaag=input_data["gamma_sat_deklaag"],
        modelfactor_u=input_data["modelfactor_u"],
        modelfactor_h=input_data["modelfactor_h"],
        modelfactor_p=input_data["modelfactor_p"],
        modelfactor_ff=input_data["modelfactor_ff"],
        modelfactor_3d=input_data["modelfactor_3d"],
        modelfactor_aniso=input_data["modelfactor_aniso"],
        modelfactor_ml=input_data["modelfactor_ml"],
        i_c_h=input_data["i_c_h"],
        r_c_deklaag=input_data["r_c_deklaag"],
        d70_m=input_data["d70_m"],
        gamma_korrel=input_data["gamma_korrel"],
        v=input_data["v"],
        theta=input_data["theta"],
        eta=input_data["eta"],
        g=input_data["g"],
        gamma_water=input_data["gamma_water"],
    )
    assert results[0] == pytest.approx(expected["z_u"], rel=1e-3)
    assert results[1] == pytest.approx(expected["z_h"], rel=1e-3)
    assert results[2] == pytest.approx(expected["z_p"], rel=1e-3)
    assert results[3] == pytest.approx(expected["z_combin"], rel=1e-3)
    assert results[4] == pytest.approx(expected["h_exit"], rel=1e-3)
    assert results[5] == pytest.approx(expected["phi_exit"], rel=1e-3)
    assert results[6] == pytest.approx(expected["dphi_c_u"], rel=1e-3)
    assert results[7] == pytest.approx(expected["i_exit"], rel=1e-3)
    assert results[8] == pytest.approx(expected["dh_c"], rel=1e-3)
    assert results[9] == pytest.approx(expected["dh_red"], rel=1e-3)


# extract inputs and expected outputs for limit state_model4a
inputs_lm_model4a = test_data.loc[:, input_keys_lm_model4a].to_dict(orient="records")
expected_outputs_lm_model4a = test_data[output_keys_lm_model4a].to_dict(
    orient="records"
)


@pytest.mark.parametrize(
    "input_data, expected", zip(inputs_lm_model4a, expected_outputs_lm_model4a)
)
def test_limit_state_model4a(input_data, expected):
    """Test limit_state_model4a function"""
    results = piping_lm.limit_state_model4a(
        L_intrede=input_data["L_intrede"],
        L_but=input_data["L_but"],
        L_bit=input_data["L_bit"],
        L_achterland=input_data["L_achterland"],
        buitenwaterstand=input_data["buitenwaterstand"],
        polderpeil=input_data["polderpeil"],
        mv_exit=input_data["mv_exit"],
        top_zand=input_data["top_zand"],
        kD_wvp=input_data["kD_wvp"],
        D_wvp=input_data["D_wvp"],
        d70=input_data["d70"],
        gamma_sat_deklaag=input_data["gamma_sat_deklaag"],
        c_voorland=input_data["c_voorland"],
        c_achterland=input_data["c_achterland"],
        modelfactor_u=input_data["modelfactor_u"],
        modelfactor_h=input_data["modelfactor_h"],
        modelfactor_p=input_data["modelfactor_p"],
        modelfactor_ff=input_data["modelfactor_ff"],
        modelfactor_3d=input_data["modelfactor_3d"],
        modelfactor_aniso=input_data["modelfactor_aniso"],
        modelfactor_ml=input_data["modelfactor_ml"],
        i_c_h=input_data["i_c_h"],
        r_c_deklaag=input_data["r_c_deklaag"],
        d70_m=input_data["d70_m"],
        gamma_korrel=input_data["gamma_korrel"],
        v=input_data["v"],
        theta=input_data["theta"],
        eta=input_data["eta"],
        g=input_data["g"],
        gamma_water=input_data["gamma_water"],
    )
    assert results[0] == pytest.approx(expected["z_u"], rel=1e-3)
    assert results[1] == pytest.approx(expected["z_h"], rel=1e-3)
    assert results[2] == pytest.approx(expected["z_p"], rel=1e-3)
    assert results[3] == pytest.approx(expected["z_combin"], rel=1e-3)
    assert results[4] == pytest.approx(expected["h_exit"], rel=1e-3)
    assert results[5] == pytest.approx(expected["r_exit"], rel=1)
    assert results[6] == pytest.approx(expected["phi_exit"], rel=1e-3)
    assert results[7] == pytest.approx(expected["d_deklaag"], rel=1e-3)
    assert results[8] == pytest.approx(expected["dphi_c_u"], rel=1e-3)
    assert results[9] == pytest.approx(expected["i_exit"], rel=1e-3)
    assert results[10] == pytest.approx(expected["L_voorland"], rel=1e-3)
    assert results[11] == pytest.approx(expected["lambda_voorland"], rel=1e-3)
    assert results[12] == pytest.approx(expected["W_voorland"], rel=1e-3)
    assert results[13] == pytest.approx(expected["L_kwelweg"], rel=1e-3)
    assert results[14] == pytest.approx(expected["dh_c"], rel=1e-3)
    assert results[15] == pytest.approx(expected["dh_red"], rel=1e-3)


# extract inputs and expected outputs for limit_state_moria
inputs_lm_moria = test_data.loc[:, input_keys_lm_moria].to_dict(orient="records")
expected_outputs_lm_moria = test_data[output_keys_lm_moria].to_dict(orient="records")


@pytest.mark.parametrize(
    "input_data, expected", zip(inputs_lm_moria, expected_outputs_lm_moria)
)
def test_limit_state_moria(input_data, expected):
    """Test limit_state_moria function"""

    print(f"{input_data=}")
    print(f"{expected=}")

    results = piping_lm.limit_state_moria(
        L_intrede=input_data["L_intrede"],
        L_but=input_data["L_but"],
        buitenwaterstand=input_data["buitenwaterstand"],
        buitenwaterstand_gemiddeld=input_data["buitenwaterstand_gemiddeld"],
        polderpeil=input_data["polderpeil"],
        mv_exit=input_data["mv_exit"],
        lambda_voorland=input_data["lambda_voorland"],
        phi_exit_gemiddeld=input_data["phi_exit_gemiddeld"],
        r_exit=input_data["r_exit"],
        top_zand=input_data["top_zand"],
        k_wvp=input_data["k_wvp"],
        D_wvp=input_data["D_wvp"],
        d70=input_data["d70"],
        gamma_sat_deklaag=input_data["gamma_sat_deklaag"],
        modelfactor_u=input_data["modelfactor_u"],
        modelfactor_h=input_data["modelfactor_h"],
        modelfactor_p=input_data["modelfactor_p"],
        modelfactor_ff=input_data["modelfactor_ff"],
        modelfactor_3d=input_data["modelfactor_3d"],
        modelfactor_aniso=input_data["modelfactor_aniso"],
        modelfactor_ml=input_data["modelfactor_ml"],
        i_c_h=input_data["i_c_h"],
        r_c_deklaag=input_data["r_c_deklaag"],
        d70_m=input_data["d70_m"],
        gamma_korrel=input_data["gamma_korrel"],
        v=input_data["v"],
        theta=input_data["theta"],
        eta=input_data["eta"],
        g=input_data["g"],
        gamma_water=input_data["gamma_water"],
    )

    print(f"{results=}")
    parameters = ["z_u", "z_h", "z_p", "z_combin", "h_exit", "phi_exit", "d_deklaag", "dphi_c_u", "i_exit",
                  "L_voorland", "W_voorland", "L_kwelweg", "kD_wvp", "dh_c", "dh_red"]
    results_str = [f"{label}={value}" for value, label in zip(results, parameters)]

    print(f"{results_str=}")

    for index, parameter in enumerate(parameters):
        assert results[index] == pytest.approx(expected[parameter], rel=1e-3)

    # assert results[0] == pytest.approx(expected["z_u"], rel=1e-3)
    # assert results[1] == pytest.approx(expected["z_h"], rel=1e-3)
    # assert results[2] == pytest.approx(expected["z_p"], rel=1e-3)
    # assert results[3] == pytest.approx(expected["z_combin"], rel=1e-3)
    # assert results[4] == pytest.approx(expected["h_exit"], rel=1e-3)
    # assert results[6] == pytest.approx(expected["phi_exit"], rel=1e-3)
    # assert results[7] == pytest.approx(expected["d_deklaag"], rel=1e-3)
    # assert results[8] == pytest.approx(expected["dphi_c_u"], rel=1e-3)
    # assert results[9] == pytest.approx(expected["i_exit"], rel=1e-3)
    # assert results[10] == pytest.approx(expected["L_voorland"], rel=1e-3)
    # assert results[11] == pytest.approx(expected["W_voorland"], rel=1e-3)
    # assert results[12] == pytest.approx(expected["L_kwelweg"], rel=1e-3)
    # assert results[13] == pytest.approx(expected["kD_wvp"], rel=1e-3)
    # assert results[14] == pytest.approx(expected["dh_c"], rel=1e-3)
    # assert results[15] == pytest.approx(expected["dh_red"], rel=1e-3)
