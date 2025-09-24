"""Test module for piping.py"""

import pytest
from . import piping

## testcase model 4a
# k = 40 #m/d
# D = 50 #m
# c1 = 10 #d
# c3 = 50 #d
# L1 = 150 #m
# L2 = 45 #m
# L3 = 3000.0 #m
# x_but = 0.0 #m
# x_bit = 45.0 #m
# lambda1 = 141.4213562373095
# lambda3 = 316.22776601683793319988935444327
# W1 = 111.14536276273107
# W3 = 316.2277623787640000
# W_tot4a = 472.373125141495
# r_but = 0.76470853898
# r_bit = 0.66944486371
# r(-150.0) = 1.0
# r(3045.0) = 0.0
# r(-50.0) = 0.8579165276194
# r(55.0) = 0.648606379956042
# r(90.0) = 0.580648922902315
# r(22.5) = 0.717076701341341
# piping input
# D70 = 2.7E-4 m


def test_calc_Dcover():
    assert piping.calc_d_deklaag(0.0, 2.0) == 0.1
    assert piping.calc_d_deklaag(2.0, 1.0) == 1.0


def test_calc_h_exit():
    assert piping.calc_h_exit(0.1, 2.0) == 2.0
    assert piping.calc_h_exit(0.0, 0.1) == 0.1
    assert piping.calc_h_exit(0.0, 0.000001) == 0.000001
    assert piping.calc_h_exit(0.0, 0.0) == 0.0

def test_calc_lengte_voorland():
    assert piping.calc_lengte_voorland(500.0, 200.0) == 300.0
    assert piping.calc_lengte_voorland(200.0, 300.0) == 100.0
    assert piping.calc_lengte_voorland(0.0, 1.0) == 1.0
    assert piping.calc_lengte_voorland(1.0, 0.0) == 1.0
    assert piping.calc_lengte_voorland(0.0, 0.0) == 0.0

def test_calc_lambda_achterland():
    assert piping.calc_lambda_achterland(50.0*40.0, 10.0) == pytest.approx(141.4213562373095, 0.0001)
    assert piping.calc_lambda_achterland(50.0*40.0, 50.0) == pytest.approx(316.22776601683793, 0.0001)

def test_calc_lambda_voorland():
    assert piping.calc_lambda_voorland(50.0*40.0, 10.0) == pytest.approx(141.4213562373095, 0.0001)
    assert piping.calc_lambda_voorland(50.0*40.0, 50.0) == pytest.approx(316.22776601683793, 0.0001)

def test_calc_dh_red():
    assert piping.calc_dh_red(5.0, 2.0, 0.3, 10.0) == pytest.approx((3.0-0.3*10), 0.0001)

def test_calc_W_achterland():
    assert piping.calc_W_achterland(piping.calc_lambda_achterland(50.0*40.0, 10.0), 150.0) == pytest.approx(111.14536276273107, 0.0001)
    assert piping.calc_W_achterland(piping.calc_lambda_achterland(50.0*40.0, 50.0), 3500.0) == pytest.approx(316.2277623787640000, 0.0001)

def test_calc_W_voorland():
    assert piping.calc_W_voorland(piping.calc_lambda_achterland(50.0*40.0, 10.0), 150.0) == pytest.approx(111.14536276273107, 0.0001)
    assert piping.calc_W_voorland(piping.calc_lambda_achterland(50.0*40.0, 50.0), 3500.0) == pytest.approx(316.2277623787640000, 0.0001)

def test_calc_L_kwelweg():
    assert piping.calc_L_kwelweg(500.0, 200.0) == 700.0
    assert piping.calc_L_kwelweg(0.0, 0.0) == 0.0
    assert piping.calc_L_kwelweg(100.1, 0.4) == 100.5

def test_calc_dphi_c_u():
    assert piping.calc_dphi_c_u(6.0, 15.0, 9.81) == pytest.approx(
        3.174, 0.0001
    )
    assert piping.calc_dphi_c_u(0.0, 15.0, 9.81) == 0.0
    assert piping.calc_dphi_c_u(2.36690, 16.5, 9.81) == pytest.approx(
        1.614, 0.0001
    )

def test_calc_i_exit():
    assert piping.calc_i_exit(0.1,0.1,0.1) == 0.0
    assert piping.calc_i_exit(0.0,1.0,1.0) == -1.0
    assert piping.calc_i_exit(2.0,1.0,1.0) == 1.0
    with pytest.raises(ZeroDivisionError):
        piping.calc_i_exit(2.0,1.0,0.0)

def test_calc_phi_exit():
    assert piping.calc_phi_exit(0.0,0.5,1.0) == 0.5
    assert piping.calc_phi_exit(1.0,1.0,1.0) == 1.0
    assert piping.calc_phi_exit(2.0,1.0,1.0) == 1.0
    assert piping.calc_phi_exit(0.0,0.1,1.0) == 0.1

## Get data for testing calc_dh_c function
from pathlib import Path
testset_path = Path(
    Path(__file__).resolve(strict=True).parent,
    "testset",
    "testset_limitstate_piping.xlsx",
)

def get_data_calc_dh_c():
    """Get data for testing calc_dh_c function"""
    import pandas as pd
    data = pd.read_excel(testset_path, sheet_name="Blad1", header=0)
    return data

# define input and output keys for calc_dh_c function
input_keys_calc_dh_c = [
    "D70",  # i1
    "D_zand",  # i2
    "kD_WVP",  # i3
    "L_kwelweg" # i4
    "gamma_w",  # i5
    "g", # i6
    "v", # i7
    "theta", # i8
    "d70m" # i9
    "gamma_korrel"  # i10
]

output_key_calc_dh_c = ["dHc_piping"]  # expected output

# global variables for calc_dh_c function
g = 9.81  # m/s^2
v = 1.33e-6  # m^2/s
theta = 37.0  # grd
gamma_korrel = 26.0  # kN/m^3


# def test_calc_Z_u():
#     assert piping.calc_Z_u(1.614127, 3.18087, 2.466904, 1.0) == pytest.approx(
#         0.900157, 0.0001
#     )
#     assert piping.calc_Z_u(3.1743, 7.04412, -0.5, 1.0) == pytest.approx(
#         -4.3698, 0.0001
#     )


# def test_calc_F_u():
#     assert piping.calc_F_u(3.1743, 7.0441, -0.500) == pytest.approx(
#         0.4208, 0.0001
#     )
#     assert piping.calc_F_u(1.6141, 1.5, 1.5) == 8.00
#     assert piping.calc_F_u(2.0, 1.5, 1.48) == pytest.approx(100.000, 0.001)


# def test_calc_F_u_macro():
#     assert piping.calc_F_u_macro(2.0, 15.0, 9.81, 1.5, 1.0) == pytest.approx(
#         1.2232415902140672, 0.0001
#     )
#     assert piping.calc_F_u_macro(2.0, 15.0, 9.81, 1.5, 1.5) == 8.00


# def test_calc_i_optredend():
#     assert piping.calc_i_optredend(4.0, 2.0, 1.0) == 2.0
#     assert piping.calc_i_optredend(4.0, 2.0, 2.0) == 1.0
#     assert piping.calc_i_optredend(4.0, 2.0, 0.1) == 20.0


# def test_calc_Z_h():
#     assert piping.calc_Z_h(0.5, 0.5, 1.0) == 0.0
#     assert piping.calc_Z_h(0.5, 0.1, 1.0) == 0.4
#     assert piping.calc_Z_h(0.5, 0.51, 1.0) == pytest.approx(-0.01, 0.0001)
#     assert piping.calc_Z_h(0.5, 0.55, 1.1) == 0.0


# def test_calc_F_h():
#     assert piping.calc_F_h(0.5, 0.5) == 1.0
#     assert piping.calc_F_h(0.5, 0.1) == 5.0
#     assert piping.calc_F_h(0.5, 0.51) == pytest.approx((0.5 / 0.51), 0.0001)
#     assert piping.calc_F_h(0.5, 1.0) == 0.5


# def test_calc_dH_sellmeijer_inc_calc_settings():
#     assert piping.calc_dH_sellmeijer_inc_calc_settings(
#         2.530e-04,  # m
#         19.24,  # m/d
#         27.5,  # m
#         108.157096,  # m
#         9.81,  # m/s^2
#         0.00000133,  # viscosity
#         37.0,  # grd
#         0.25,  # [-]
#         2.08e-4,  # m
#         26.0,
#     ) == pytest.approx(6.50006e00, 0.0001)


# def test_calc_dH_sellmeijer():
#     assert piping.calc_dH_sellmeijer(
#         3.50e-04,
#         41.4,
#         50.0,
#         238.0892,
#         9.81,  # m  # m/d  # m  # m  # m/s^2
#     ) == pytest.approx(10.1276, 0.0001)
#     assert piping.calc_dH_sellmeijer(
#         2.530e-04,  # m
#         19.24,  # m/d
#         27.5,  # m
#         108.157096,  # m
#         9.81,  # m/s^2
#     ) == pytest.approx(6.50006e00, 0.0001)


# def test_Z_p():
#     assert piping.calc_Z_p(5.0, 5.0, 1.0) == 0.0
#     assert piping.calc_Z_p(6.5, 7.5, 1.0) == -1.0
#     assert piping.calc_Z_p(6.5, 7.5, 1.2) == pytest.approx(0.3, 0.001)


# def test_calc_F_p():
#     assert piping.calc_F_p(5.0, 5.0) == 1.0
#     assert piping.calc_F_p(6.5, 7.5) == pytest.approx(
#         0.8666666666666667, 0.0001
#     )
#     assert piping.calc_F_p(1.0, 10.0) == pytest.approx(0.1, 0.0001)
#     assert piping.calc_F_p(1.0, 0.0) == 100.0
