import math

import pytest

from app.helper_functions import geohydro_functions

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


def test_calc_lambda():
    assert geohydro_functions.calc_lambda(2000.0, 10.0) == 141.4213562373095


def test_calc_W():
    assert geohydro_functions.calc_W(141.4213562373095, 150.0) == 111.14536276273107


def test_calc_r_BIT():
    assert geohydro_functions.calc_r_BIT(50.0, 35.0, 85.0) == 0.5


def test_calc_r_BUT():
    assert geohydro_functions.calc_r_BUT(50.0, 25.0, 50.0) == 0.6


def test_calc_respons2pot():
    assert geohydro_functions.calc_respons2pot(1.0, 0.5, 6.0) == (1.0 + 2.5)


def test_calc_pot2repons():
    assert geohydro_functions.calc_pot2repons(3.5, 1.0, 6.0) == 0.5


def test_calc_ang_freq():
    assert geohydro_functions.calc_ang_frequency(math.pi) == 2.0


def test_P_from_T():
    assert geohydro_functions.calc_P_from_T(100.0) == 50.0
    assert geohydro_functions.calc_T_from_P(200.0) == 400.0


def test_lambda_cyclic_from_stationary():
    assert (
        geohydro_functions.calc_lambda_cycl_from_stationnary(
            100.0, 8.0, 8e-6, geohydro_functions.calc_ang_frequency(12 * 3600)
        )
        == 18.525960495667167
    )


def test_calc_lambda_cycl():
    assert geohydro_functions.calc_lambda_cycl(
        100.0, 864000.00, 44700.00
    ) == pytest.approx(209.67736723, abs=0.0001)


def test_calc_theta():
    assert geohydro_functions.calc_theta(0.0, 250.0) == pytest.approx(
        0.392699, abs=0.001
    )
    assert geohydro_functions.calc_theta(3.0, 1.0) == pytest.approx(0.0, abs=0.001)
    assert geohydro_functions.calc_theta(1.233296, 1.0) == pytest.approx(
        0.145223, abs=0.001
    )


def test_calc_f():
    assert geohydro_functions.calc_f(0.277242939120909, 1.0) == pytest.approx(
        3.63324765744605, abs=0.1
    )
    assert geohydro_functions.calc_f(2.07506654521457, 1.0) == pytest.approx(
        1.0026721428371, abs=0.001
    )


def test_calc_mean_pot_gradient():
    assert geohydro_functions.calc_mean_pot_gradient(
        100.0, 350.0, 20.0, 1.0, 0.0
    ) == pytest.approx(0.734579328773788, abs=0.0001)
    assert geohydro_functions.calc_mean_pot_gradient(
        100.0, 350.0, 0.0, 1.0, 0.0
    ) == pytest.approx(0.777777777777778, abs=0.0001)
    assert geohydro_functions.calc_mean_pot_gradient(
        100.0, 350.0, 100.0, 1.0, 0.0
    ) == pytest.approx(0.584482339058556, abs=0.0001)
