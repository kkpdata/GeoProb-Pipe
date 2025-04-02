from pathlib import Path

import pandas as pd
import pytest

from app.helper_functions import limitstatepiping_model4a_function_implementation

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
    "DIST_L_GEOM", #i1
    "DIST_BUT", #i2
    "DIST_BIT", #i3
    "L3_geom", #i4
    "mv", #i5
    "pp", #i6
    "top_zand", #i7
    "gamma_sat_cover", #i8
    "gamma_w", #i9
    "kD_WVP", #i10
    "D_zand", #i11
    "D70", #i12
    "c_1", #i13
    "c_3", #i14
    "mu", #i15
    "mh", #i16
    "mp", #i17
    "i_c_h", #i18
    "rc", #i19
    "h", #i20
]

# Expected output keys
expected_keys = ["Z_u"] + ["Z_h"] + ["Z_p"] 
testset_keys = input_keys + expected_keys
testset_keys_string = ", ".join(testset_keys)
#print(testset_keys_string)
# Get the test data from the Excel file
testset_df = get_data()[testset_keys]
# Convert the DataFrame to a list of tuples for pytest parametrize
test_data = [tuple(row) for row in testset_df.itertuples(index=False, name=None)]
#print(test_data[:5])

# Test function for Uplift limit state function Z_u
# This function will be called for each row of test data
@pytest.mark.parametrize(
    "i1,i2,i3,i4,i5,i6,i7,i8,i9,i10,i11,i12,i13,i14,i15,i16,i17,i18,i19,i20,Z_u, Z_h, Z_p",
    test_data,
)
def test_calc_Z_combin_piping(
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
    Z_p,):
    assert limitstatepiping_model4a_function_implementation.calc_Z_combin_piping(
        dist_L_geom=i1,
        dist_BUT=i2,
        dist_BIT=i3,
        L3_geom=i4,
        mv=i5,
        pp=i6,
        top_zand=i7,
        gamma_sat_cover=i8,
        gamma_w=i9,
        kD_wvp=i10,
        D_wvp=i11,
        d70=i12,
        c_1=i13,
        c_3=i14,
        mu=i15,
        mh=i16,
        mp=i17,
        i_c_h=i18,
        rc=i19,
        h=i20)[0] == pytest.approx(Z_u, rel=1e-2, abs=1e-2)
    
