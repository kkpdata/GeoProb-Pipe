import pytest

from app.helper_functions import calibration_WBI


def test_calc_Beta_u():
    assert calibration_WBI.calc_Beta_u(1.0, -4.5) == pytest.approx(
        4.23688951104391, 0.0001
    )


def test_calc_Beta_h():
    assert calibration_WBI.calc_Beta_h(1.0, -4.5) == pytest.approx(
        4.88385890279972, 0.0001
    )


def test_calc_Beta_p():
    assert calibration_WBI.calc_Beta_p(1.00, -4.5) == pytest.approx(
        5.12372780228843, 0.0001
    )


def test_calc_SF_u():
    assert calibration_WBI.calc_SF_u(-4.23688951104391, -4.5) == pytest.approx(
        1.0000, 0.0001
    )


def test_calc_SF_h():
    assert calibration_WBI.calc_SF_h(-4.88385890279972, -4.5) == pytest.approx(
        1.0000, 0.0001
    )


def test_calc_SF_p():
    assert calibration_WBI.calc_SF_p(-5.12372780228843, -4.5) == pytest.approx(
        1.0000, 0.0001
    )


def test_class_reliability_dike_trajectory():
    model = calibration_WBI.ReliabilityDikeTrajectory(
        T=10000.0, w=0.24, L=3000.0, a=0.9, b=300.0
    )
    assert model.Pnorm == pytest.approx(0.0001, 0.0001)
    assert model.PfailureMechanism == pytest.approx(2.4e-5, 0.0001)
    assert model.Pcross == pytest.approx(2.4e-6, 0.0001)
    assert model.Bnorm == pytest.approx(-3.719016485, 0.001)
    assert model.BfailureMechanism == pytest.approx(-4.065157, 0.001)
    assert model.Bcross == pytest.approx(-4.573344477, 0.001)
    assert model.Ndsn == pytest.approx(10.0, 0.0001)
    assert model.SF_u == pytest.approx(1.441429, 0.0001)
    assert model.SF_h == pytest.approx(1.088987, 0.0001)
    assert model.SF_p == pytest.approx(1.141315, 0.0001)
