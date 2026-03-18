import pytest
from geoprob_pipe.calculations.physical_components import model4a

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


def test_class_4a():
    model = model4a.Model4a(
        kD=40.0*50.0, D=50.0, c1=10.0, c3=50.0, L1=150.0, L3=3000.0, x_but=0.0, x_bit=45.0
    )
    assert model.lambda1 == pytest.approx(141.4213562373095, abs=0.0001)
    assert model.lambda3 == pytest.approx(316.22776601683793319988935444327, abs=0.0001)
    assert model.W1 == pytest.approx(111.14536276273107, abs=0.0001)
    assert model.W3 == pytest.approx(316.2277623787640000, abs=0.0001)
    assert model.W_rad == 0.44 * 50.0
    assert model.respons(-150.0)[0] == 1.00
    assert model.respons(0.0)[0] == pytest.approx(0.76470853898, abs=0.0001)
    assert model.respons(0.0)[1] == pytest.approx(0.76470853898, abs=0.0001)
    assert model.respons(0.0)[2] == pytest.approx(0.66944486371, abs=0.0001)
    assert model.respons(-50.0)[0] == pytest.approx(0.8579165276, abs=0.0001)
    assert model.respons(55.0)[0] == pytest.approx(0.648606379956042, abs=0.0001)
    assert model.respons(90.0)[0] == pytest.approx(0.580648922902315, abs=0.0001)
    assert model.respons(22.5)[0] == pytest.approx(0.717076701341341, abs=0.0001)
