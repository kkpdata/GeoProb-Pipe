"""Tests for the limitstate_piping module using external testset."""

import pytest
from open_stph import limitstatepiping_model4a
from typing import List
import pandas as pd
from pathlib import Path

testset_file = Path(__file__).parent / "data" / "testset_limitstate_piping.xlsx"


def get_data():
    """get data from external testset"""
    # read file
    testdata = pd.read_excel(testset_file)
    input_data = testdata.iloc[
        4, 0:20
    ].values.tolist()  # first 20 (0 to 19) columns are input data
    expected_output = testdata.iloc[
        4, [20, 21, 22, 23, 24, 32, 33, 34, 35, 40, 41, 42, 43, 44]
    ].values.tolist()

    # data_result = {"input_data": input_data, "expected_output": expected_output}

    return input_data, expected_output


test_dataset = get_data()
print(test_dataset)


# works if only one row is obtained from get_data()
def test_calc_Z_combin_piping():
    """Test the calc_Z_combin_piping function."""
    input_data = test_dataset[0]
    expected_output = test_dataset[1]
    result = limitstatepiping_model4a.calc_Z_combin_piping(input_data)
    assert result == pytest.approx(expected_output, 1e-3)
