"""Test module for piping_functions.py"""

import pytest

from app.helper_functions import piping_functions

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
    assert piping_functions.calc_Dcover(0.0, 2.0) == 0.1
    assert piping_functions.calc_Dcover(2.0, 1.0) == 1.0


def test_calc_h_exit():
    assert piping_functions.calc_h_exit(0.1, 2.0) == 2.0
    assert piping_functions.calc_h_exit(0.0, 0.1) == 0.1
    assert piping_functions.calc_h_exit(0.0, 0.000001) == 0.000001
    assert piping_functions.calc_h_exit(0.0, 0.0) == 0.0


def test_calc_dH_red():
    assert piping_functions.calc_dH_red(5.0, 2.0, 0.3, 10.0) == 0.0


def test_calc_d_pot_c_u():
    assert piping_functions.calc_d_pot_c_u(6.0, 15.0, 9.81) == pytest.approx(
        3.174, 0.0001
    )
    assert piping_functions.calc_d_pot_c_u(0.0, 15.0, 9.81) == 0.0
    assert piping_functions.calc_d_pot_c_u(2.36690, 16.5, 9.81) == pytest.approx(
        1.614, 0.0001
    )


def test_calc_Z_u():
    assert piping_functions.calc_Z_u(1.614127, 3.18087, 2.466904, 1.0) == pytest.approx(
        0.900157, 0.0001
    )
    assert piping_functions.calc_Z_u(3.1743, 7.04412, -0.5, 1.0) == pytest.approx(
        -4.3698, 0.0001
    )


def test_calc_F_u():
    assert piping_functions.calc_F_u(3.1743, 7.0441, -0.500) == pytest.approx(
        0.4208, 0.0001
    )
    assert piping_functions.calc_F_u(1.6141, 1.5, 1.5) == 8.00
    assert piping_functions.calc_F_u(2.0, 1.5, 1.48) == pytest.approx(100.000, 0.001)


def test_calc_F_u_macro():
    assert piping_functions.calc_F_u_macro(2.0, 15.0, 9.81, 1.5, 1.0) == pytest.approx(
        1.2232415902140672, 0.0001
    )
    assert piping_functions.calc_F_u_macro(2.0, 15.0, 9.81, 1.5, 1.5) == 8.00


def test_calc_i_optredend():
    assert piping_functions.calc_i_optredend(4.0, 2.0, 1.0) == 2.0
    assert piping_functions.calc_i_optredend(4.0, 2.0, 2.0) == 1.0
    assert piping_functions.calc_i_optredend(4.0, 2.0, 0.1) == 20.0


def test_calc_Z_h():
    assert piping_functions.calc_Z_h(0.5, 0.5, 1.0) == 0.0
    assert piping_functions.calc_Z_h(0.5, 0.1, 1.0) == 0.4
    assert piping_functions.calc_Z_h(0.5, 0.51, 1.0) == pytest.approx(-0.01, 0.0001)
    assert piping_functions.calc_Z_h(0.5, 0.55, 1.1) == 0.0


def test_calc_F_h():
    assert piping_functions.calc_F_h(0.5, 0.5) == 1.0
    assert piping_functions.calc_F_h(0.5, 0.1) == 5.0
    assert piping_functions.calc_F_h(0.5, 0.51) == pytest.approx((0.5 / 0.51), 0.0001)
    assert piping_functions.calc_F_h(0.5, 1.0) == 0.5


def test_calc_dH_sellmeijer_inc_calc_settings():
    assert piping_functions.calc_dH_sellmeijer_inc_calc_settings(
        2.530e-04,  # m
        19.24,  # m/d
        27.5,  # m
        108.157096,  # m
        9.81,  # m/s^2
        0.00000133,  # viscosity
        37.0,  # grd
        0.25,  # [-]
        2.08e-4,  # m
        26.0,
    ) == pytest.approx(6.50006e00, 0.0001)


def test_calc_dH_sellmeijer():
    assert piping_functions.calc_dH_sellmeijer(
        3.50e-04,
        41.4,
        50.0,
        238.0892,
        9.81,  # m  # m/d  # m  # m  # m/s^2
    ) == pytest.approx(10.1276, 0.0001)
    assert piping_functions.calc_dH_sellmeijer(
        2.530e-04,  # m
        19.24,  # m/d
        27.5,  # m
        108.157096,  # m
        9.81,  # m/s^2
    ) == pytest.approx(6.50006e00, 0.0001)


def test_Z_p():
    assert piping_functions.calc_Z_p(5.0, 5.0, 1.0) == 0.0
    assert piping_functions.calc_Z_p(6.5, 7.5, 1.0) == -1.0
    assert piping_functions.calc_Z_p(6.5, 7.5, 1.2) == pytest.approx(0.3, 0.001)


def test_calc_F_p():
    assert piping_functions.calc_F_p(5.0, 5.0) == 1.0
    assert piping_functions.calc_F_p(6.5, 7.5) == pytest.approx(
        0.8666666666666667, 0.0001
    )
    assert piping_functions.calc_F_p(1.0, 10.0) == pytest.approx(0.1, 0.0001)
    assert piping_functions.calc_F_p(1.0, 0.0) == 100.0
