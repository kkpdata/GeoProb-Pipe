from pathlib import Path

import pandas as pd
import pytest

from app.helper_functions import limitstatepiping_model4a_class_implementation

test_path = Path(
    Path(__file__).resolve(strict=True).parent,
    "testset",
    "testset_limitstate_piping.xlsx",
)


def get_data():
    testdata = pd.read_excel(test_path)
    return testdata


# Define the input variables for the functions for Uplift, Heave and Piping
# dist_L_geom: float
# dist_BUT: float
# dist_BIT: float
# L3_geom: float
# mv: float
# pp: float
# top_zand: float
# gamma_sat_cover: float
# gamma_w: float
# kD: float
# D: float
# d70: float
# c1: float
# c3: float
# mu: float
# mh: float
# mp: float
# i_c_h: float
# rc: float
# h: float
## Class implementation

# input variables
input_keys = [
    "DIST_L_GEOM",
    "DIST_BUT",
    "DIST_BIT",
    "L3_geom",
    "mv",
    "pp",
    "top_zand",
    "gamma_sat_cover",
    "gamma_w",
    "kD_WVP",
    "D_zand",
    "D70",
    "c_1",
    "c_3",
    "mu",
    "mh",
    "mp",
    "i_c_h",
    "rc",
    "h",
]

# Expected output keys
expected_keys = ["Z_u"] + ["Z_h"] + ["Z_p"] + ["L_kwelweg"] + ["dHc_piping"]
testset_keys = input_keys + expected_keys
testset_keys_string = ", ".join(testset_keys)
#print(testset_keys_string)
# Get the test data from the Excel file
testset_df = get_data()[testset_keys]
# Convert the DataFrame to a list of tuples for pytest parametrize
test_data = [tuple(row) for row in testset_df.itertuples(index=False, name=None)]
#print(test_data[:5])

# Test function for LimitStatePipingModel4a
# This function will be called for each row of test data
@pytest.mark.parametrize(
    "i1,i2,i3,i4,i5,i6,i7,i8,i9,i10,i11,i12,i13,i14,i15,i16,i17,i18,i19,i20,Z_u, Z_h, Z_p, expected_L_kwelweg, expected_dHc_piping",
    test_data,
)
def test_LimitStatePipingModel4a(
    i1,
    i2,
    i3,
    i4,
    i5,
    i6,
    i7,
    i8,
    i9,
    i10,
    i11,
    i12,
    i13,
    i14,
    i15,
    i16,
    i17,
    i18,
    i19,
    i20,
    Z_u,
    Z_h,
    Z_p,
    expected_L_kwelweg,
    expected_dHc_piping,
):
    model = limitstatepiping_model4a_class_implementation.LimitStatePipingModel4a(
        dist_L_geom=i1,
        dist_BUT=i2,
        dist_BIT=i3,
        L3_geom=i4,
        mv=i5,
        pp=i6,
        top_zand=i7,
        gamma_sat_cover=i8,
        gamma_w=i9,
        kD=i10,
        D=i11,
        d70=i12,
        c_1=i13,
        c_3=i14,
        mu=i15,
        mh=i16,
        mp=i17,
        i_c_h=i18,
        rc=i19,
        h=i20,
    )
    assert model.Z_u == pytest.approx(Z_u, 0.0001)
    assert model.Z_h == pytest.approx(Z_h, 0.0001)
    assert model.Z_p == pytest.approx(Z_p, 0.0001)
    assert model.L_kwelweg == pytest.approx(expected_L_kwelweg, 0.0001)
    assert model.dhc == pytest.approx(expected_dHc_piping, 0.0001)
    assert limitstatepiping_model4a_class_implementation.Z_u(
        dist_L_geom=i1,
        dist_BUT=i2,
        dist_BIT=i3,
        L3_geom=i4,
        mv=i5,
        pp=i6,
        top_zand=i7,
        gamma_sat_cover=i8,
        gamma_w=i9,
        kD=i10,
        D=i11,
        d70=i12,
        c_1=i13,
        c_3=i14,
        mu=i15,
        mh=i16,
        mp=i17,
        i_c_h=i18,
        rc=i19,
        h=i20,) == pytest.approx(Z_u, 0.0001)
    assert limitstatepiping_model4a_class_implementation.Z_h(
        dist_L_geom=i1,
        dist_BUT=i2,
        dist_BIT=i3,
        L3_geom=i4,
        mv=i5,
        pp=i6,
        top_zand=i7,
        gamma_sat_cover=i8,
        gamma_w=i9,
        kD=i10,
        D=i11,
        d70=i12,
        c_1=i13,
        c_3=i14,
        mu=i15,
        mh=i16,
        mp=i17,
        i_c_h=i18,
        rc=i19,
        h=i20,) == pytest.approx(Z_h, 0.0001)
    assert limitstatepiping_model4a_class_implementation.Z_p(
        dist_L_geom=i1,
        dist_BUT=i2,
        dist_BIT=i3,
        L3_geom=i4,
        mv=i5,
        pp=i6,
        top_zand=i7,
        gamma_sat_cover=i8,
        gamma_w=i9,
        kD=i10,
        D=i11,
        d70=i12,
        c_1=i13,
        c_3=i14,
        mu=i15,
        mh=i16,
        mp=i17,
        i_c_h=i18,
        rc=i19,
        h=i20,) == pytest.approx(Z_p, 0.0001)
    
